
import json
import pprint
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo import DESCENDING

'''

1) User registers git_repo git_url
2) User updates dev as often as needed
3) User moves dev to beta (can keep updating dev)
4) User requests release of beta
   -Admin must approve or deny
   -If approved, release version is updated, last release is archived
   -If denied, Admin can set message, User can always request again
    (changes are made by updating dev, and moving dev to beta)

- Cannot change module names ever for now, results in build error
- Cannot change git_url for a module
- Build must succeed to update dev


Module Document:
    {
        module_name: str, (unique index)
        module_name_lc: str, (unique index, lower case module name)
        git_url: str, (unique index)

        owners: [
            { kb_username: str } (eventually we might have different permissions or info here?)
        ],

        info: {
            ...
        },

        state: {
            active: True | False,
            release_approval: approved | denied | under_review | not_requested, (all releases require approval)
            review_message: str, (optional)
            registration: building | complete | error,
            error_message: str (optional),
            registration_id: str used to identify the build log,
            released: true | false (set to true if released, false or missing otherwise)
        },

        current_versions: {
            release: {
                timestamp:'',
                commit:'',
                registration_id:''
            },
            beta: {
                timestamp:'',
                commit:'',
                registration_id:''
            },
            dev: {
                timestamp:'',
                commit:'',
                registration_id:''
            }
        }

        release_versions: {
            timestamp : {
                commit:'',
                registration_id:''
            }
        }

        release_version_list: [


        ]
    }

FAVORITES
    {
        user:
        module_name:
        app_id:
        timestamp:
    }

'''
class MongoCatalogDBI:

    # Collection Names

    _MODULES='modules'
    _DEVELOPERS='developers'
    _BUILD_LOGS='build_logs'
    _FAVORITES='favorites'
    _CLIENT_GROUPS='client_groups'
    _EXEC_STATS_RAW='exec_stats_raw'
    _EXEC_STATS_APPS='exec_stats_apps'
    _EXEC_STATS_USERS='exec_stats_users'

    def __init__(self, mongo_host, mongo_db, mongo_user, mongo_psswd):

        # create the client
        self.mongo = MongoClient('mongodb://'+mongo_host)

        # Try to authenticate, will throw an exception if the user/psswd is not valid for the db
        if(mongo_user and mongo_psswd):
            self.mongo[mongo_db].authenticate(mongo_user, mongo_psswd)

        # Grab a handle to the database and collections
        self.db = self.mongo[mongo_db]
        self.modules = self.db[MongoCatalogDBI._MODULES]
        self.developers = self.db[MongoCatalogDBI._DEVELOPERS]
        self.build_logs = self.db[MongoCatalogDBI._BUILD_LOGS]
        self.favorites = self.db[MongoCatalogDBI._FAVORITES]
        self.client_groups = self.db[MongoCatalogDBI._CLIENT_GROUPS]
        self.exec_stats_raw = self.db[MongoCatalogDBI._EXEC_STATS_RAW]
        self.exec_stats_apps = self.db[MongoCatalogDBI._EXEC_STATS_APPS]
        self.exec_stats_apps.update({'avg_queue_time': {'$exists' : True}}, 
                                    {'$rename': {'avg_queue_time': 'total_queue_time',
                                                 'avg_exec_time': 'total_exec_time'}}, multi=True)
        self.exec_stats_users = self.db[MongoCatalogDBI._EXEC_STATS_USERS]
        self.exec_stats_users.update({'avg_queue_time': {'$exists' : True}}, 
                                    {'$rename': {'avg_queue_time': 'total_queue_time',
                                                 'avg_exec_time': 'total_exec_time'}}, multi=True)

        # Make sure we have an index on module and git_repo_url
        self.modules.ensure_index('module_name', unique=True, sparse=True)
        self.modules.ensure_index('module_name_lc', unique=True, sparse=True)
        self.modules.ensure_index('git_url', unique=True)

        # other indecies for query performance
        self.modules.ensure_index('owners.kb_username')

        self.developers.ensure_index('kb_username', unique=True)

        self.build_logs.ensure_index('registration_id',unique=True)
        self.build_logs.ensure_index('module_name_lc')
        self.build_logs.ensure_index('timestamp')
        self.build_logs.ensure_index('registration')
        self.build_logs.ensure_index('git_url')
        self.build_logs.ensure_index('current_versions.release.release_timestamp')

        # for favorites
        self.favorites.ensure_index('user')
        self.favorites.ensure_index('module_name_lc')
        self.favorites.ensure_index('id')
        # you can only favorite a method once, so put a unique index on the triple
        self.favorites.ensure_index([
            ('user',ASCENDING),
            ('id',ASCENDING),
            ('module_name_lc',ASCENDING)], 
            unique=True, sparse=False)

        # execution stats
        self.exec_stats_raw.ensure_index('user_id', 
                                         unique=False, sparse=False)
        self.exec_stats_raw.ensure_index([('app_module_name', ASCENDING), 
                                          ('app_id', ASCENDING)], 
                                         unique=False, sparse=True)
        self.exec_stats_raw.ensure_index([('func_module_name', ASCENDING),
                                          ('func_name', ASCENDING)], 
                                         unique=False, sparse=True)
        self.exec_stats_raw.ensure_index('creation_time', 
                                         unique=False, sparse=False)
        self.exec_stats_raw.ensure_index('finish_time', 
                                         unique=False, sparse=False)
        
        self.exec_stats_apps.ensure_index('module_name', 
                                          unique=False, sparse=True)
        self.exec_stats_apps.ensure_index([('full_app_id', ASCENDING),
                                           ('type', ASCENDING),
                                           ('time_range', ASCENDING)], 
                                          unique=True, sparse=False)
        self.exec_stats_apps.ensure_index([('type', ASCENDING),
                                           ('time_range', ASCENDING)], 
                                          unique=False, sparse=False)

        self.exec_stats_users.ensure_index([('user_id', ASCENDING), 
                                            ('type', ASCENDING),
                                            ('time_range', ASCENDING)], 
                                           unique=True, sparse=False)

        # client group
        #  app_id = [lower case module name]/[app id]
        self.client_groups.ensure_index('app_id', unique=True, sparse=False)


        self.correct_release_versions()


    def is_registered(self,module_name='',git_url=''):
        if not module_name and not git_url:
            return False
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module = self.modules.find_one(query, fields=['_id'])
        if module is not None:
            return True
        return False

    def module_name_lc_exists(self,module_name_lc=''):
        if not module_name_lc:
            return False
        module = self.modules.find_one({'module_name_lc':module_name_lc.lower()}, fields=['_id'])
        if module is not None:
            return True
        return False


    #### SET methods
    def create_new_build_log(self, registration_id, timestamp, registration_state, git_url):
        build_log = {
            'registration_id':registration_id,
            'timestamp':timestamp,
            'git_url':git_url,
            'registration':registration_state,
            'error_message':'',
            'log':[]
        }
        self.build_logs.insert(build_log)

    def delete_build_log(self, registration_id):
        self.build_logs.remove({'registration_id':registration_id})

    # new_lines is a list to objects, each representing a line
    # the object structure is : {'content':... 'error':True/False}
    def append_to_build_log(self,registration_id, new_lines):
        result = self.build_logs.update({'registration_id':registration_id}, 
            { '$push':{ 'log':{'$each':new_lines} } })
        return self._check_update_result(result)

    def set_build_log_state(self, registration_id, registration_state, error_message=''):
        result = self.build_logs.update({'registration_id':registration_id}, 
                    {'$set':{'registration':registration_state, 'error_message':error_message}})
        return self._check_update_result(result)


    def set_build_log_module_name(self, registration_id, module_name):
        result = self.build_logs.update({'registration_id':registration_id}, 
                    {'$set':{'module_name_lc':module_name.lower()}})
        return self._check_update_result(result)


    def list_builds(self, 
                skip = 0,
                limit = 1000,
                module_name_lcs = [],
                git_urls = [],
                only_running = False,
                only_error = False,
                only_complete = False):

        query = {}

        registration_match = None
        if only_running:
            registration_match = { '$nin': ['complete', 'error'] }
        elif only_error:
            registration_match = 'error'
        elif only_complete:
            registration_match = 'complete'

        if registration_match:
            query['registration'] = registration_match

        if len(module_name_lcs)>0:
            query['module_name_lc'] = { '$in':module_name_lcs }
        if len(git_urls)>0:
            query['git_urls'] = { '$in':git_urls }

        selection = {
                        'registration_id':1,
                        'timestamp':1,
                        'git_url':1,
                        'module_name_lc':1,
                        'registration':1,
                        'error_message':1,
                        '_id':0
                    }

        return list(self.build_logs.find(
                        query,selection,
                        skip=skip,
                        limit=limit,
                        sort=[['timestamp',DESCENDING]]))


    # slice arg is used in the mongo query for getting lines.  It is either a
    # pos int (get first n lines), neg int (last n lines), or array [skip, limit]
    def get_parsed_build_log(self,registration_id, slice_arg=None):
        selection = {
                        'registration_id':1,
                        'timestamp':1,
                        'git_url':1,
                        'module_name_lc':1,
                        'registration':1,
                        'error_message':1,
                        'log':1,
                        '_id':0
                    }
        if slice_arg:
            selection['log'] = {'$slice':slice_arg}

        return self.build_logs.find_one({'registration_id':registration_id},selection)


    def register_new_module(self, git_url, username, timestamp, registration_state, registration_id):
        # get current time since epoch in ms in utc
        module = {
            'info':{},
            'git_url':git_url,
            'owners':[{'kb_username':username}],
            'state': {
                'active': True,
                'released': False,
                'release_approval': 'not_requested',
                'registration': registration_state,
                'error_message' : '',
            },
            'current_versions': {
                'release':None,
                'beta':None,
                'dev': {
                    'timestamp' : timestamp,
                    'registration_id' : registration_id
                }
            },
            'release_version_list': []
        }
        self.modules.insert(module)


    # last_state is for concurency control.  If set, it will match on state as well, and will fail if the
    # last_state does not match indicating another process changed the state
    def set_module_registration_state(self, module_name='', git_url='', new_state=None, last_state=None, error_message=''):
        if new_state:
            query = self._get_mongo_query(module_name=module_name, git_url=git_url)
            if last_state:
                query['state.registration'] = last_state
            result = self.modules.update(query, {'$set':{'state.registration':new_state, 'state.error_message':error_message}})
            return self._check_update_result(result)
        return False

    def set_module_release_state(self, module_name='', git_url='', new_state=None, last_state=None, review_message=''):
        if new_state:
            query = self._get_mongo_query(module_name=module_name, git_url=git_url)
            if last_state:
                query['state.release_approval'] = last_state
            result = self.modules.update(query, {'$set':{'state.release_approval':new_state, 'state.review_message':review_message}})
            return self._check_update_result(result)
        return False


    def push_beta_to_release(self, module_name='', git_url='', release_timestamp=None):
        current_versions = self.get_module_current_versions(module_name=module_name, git_url=git_url)
        beta_version = current_versions['beta']

        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        query['current_versions.beta.timestamp'] = beta_version['timestamp']

        if not release_timestamp:
            raise ValueError('internal error- timestamp not set in push_beta_to_release')
        beta_version['release_timestamp'] = release_timestamp
        
        # we both update the release version, and since we archive release versions, we stash it in the release_versions list as well
        result = self.modules.update(query, {'$set':{
                                                'state.released':True,
                                                'current_versions.release':beta_version
                                                },
                                             '$push':{
                                                'release_version_list':beta_version
                                                }})
        return self._check_update_result(result)

    def push_dev_to_beta(self, module_name='', git_url=''):
        current_versions = self.get_module_current_versions(module_name=module_name, git_url=git_url)
        dev_version = current_versions['dev']

        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        query['current_versions.dev.timestamp'] = dev_version['timestamp']
        
        result = self.modules.update(query, {'$set':{'current_versions.beta':dev_version}})
        return self._check_update_result(result)

    def update_dev_version(self, version_info, module_name='', git_url=''):
        if version_info:
            query = self._get_mongo_query(module_name=module_name, git_url=git_url)
            result = self.modules.update(query, {'$set':{'current_versions.dev':version_info}})
            return self._check_update_result(result)
        return False



    def set_module_name(self, git_url, module_name):
        if not module_name:
            raise ValueError('module_name must be defined to set a module name')
        query = self._get_mongo_query(git_url=git_url)
        result = self.modules.update(query, {'$set':{'module_name':module_name,'module_name_lc':module_name.lower()}})
        return self._check_update_result(result)


    def set_module_info(self, info, module_name='', git_url=''):
        if not info:
            raise ValueError('info must be defined to set the info for a module')
        if type(info) is not dict:
            raise ValueError('info must be a dictionary')
        query = self._get_mongo_query(git_url=git_url, module_name=module_name)
        result = self.modules.update(query, {'$set':{'info':info}})
        return self._check_update_result(result)


    def set_module_owners(self, owners, module_name='', git_url=''):
        if not owners:
            raise ValueError('owners must be defined to set the owners for a module')
        if type(owners) is not list:
            raise ValueError('owners must be a list')
        query = self._get_mongo_query(git_url=git_url, module_name=module_name)
        result = self.modules.update(query, {'$set':{'owners':owners}})
        return self._check_update_result(result)

    # active = True | False
    def set_module_active_state(self, active, module_name='', git_url=''):
        query = self._get_mongo_query(git_url=git_url, module_name=module_name)
        result = self.modules.update(query, {'$set':{'state.active':active}})
        return self._check_update_result(result)


    #### GET methods
    def get_module_state(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query, fields=['state'])['state']

    def get_module_current_versions(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query, fields=['current_versions'])['current_versions']

    def get_module_owners(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query, fields=['owners'])['owners']

    def get_module_details(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query, fields=['module_name','git_url','info','owners','state','current_versions'])

    def get_module_full_details(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query)

    #### LIST / SEARCH methods

    def find_basic_module_info(self, query):
        return list(self.modules.find(query,{'module_name':1,'git_url':1,'_id':0}))

    def find_current_versions_and_owners(self, query):
        return list(self.modules.find(query,{'module_name':1,'git_url':1,'current_versions':1,'owners':1,'_id':0}))






    # tag should be one of dev, beta, release - do checking outside of this method
    def list_service_module_versions_with_tag(self, tag):
        query = {'info.dynamic_service':True, 'current_versions.'+tag+'.dynamic_service':True}
        projection = {
            '_id':0,
            'module_name':1,
            'current_versions.'+tag+'.version':1,
            'current_versions.'+tag+'.git_commit_hash':1
        }
        result = []
        for m in self.modules.find(query,projection):
            result.append({
                'module_name':m['module_name'],
                'version':m['current_versions'][tag]['version'],
                'git_commit_hash':m['current_versions'][tag]['git_commit_hash']})
        return result


    # all released service module versions
    def list_all_released_service_module_versions(self):
        result = self.modules.aggregate([
            {'$match':{'info.dynamic_service':True}}, # make sure it is a module that has at least one dynamic service
            {'$unwind':"$release_version_list"},      # look at all the release versions
            {'$match':{'release_version_list.dynamic_service':True}}, # find the dynamic service released versions
            {'$project':{
                    'module_name':1,
                    'version':'$release_version_list.version',
                    'git_commit_hash':'$release_version_list.git_commit_hash',
                    '_id':0
                }
            }])

        return list(result['result'])






    #### developer check methods

    def approve_developer(self, developer):
        # if the developer is already on the list, just return
        if self.is_approved_developer([developer])[0]:
            return
        self.developers.insert({'kb_username':developer})

    def revoke_developer(self, developer):
        # if the developer is not on the list, throw an error (maybe a typo, so let's catch it)
        if not self.is_approved_developer([developer])[0]:
            raise ValueError('Cannot revoke "'+developer+'", that developer was not found.')
        self.developers.remove({'kb_username':developer})

    def is_approved_developer(self, usernames):
        #TODO: optimize, but I expect the list of usernames will be fairly small, so we can loop.  Regardless, in
        # old mongo (2.x) I think this is even faster in most cases than using $in within a very large list
        is_approved = []
        for u in usernames:
            count = self.developers.find({'kb_username':u}).count()
            if count>0:
                is_approved.append(True)
            else:
                is_approved.append(False)
        return is_approved


    def list_approved_developers(self):
        return list(self.developers.find({},{'kb_username':1, '_id':0}))

    def migrate_module_to_new_git_url(self, module_name, current_git_url, new_git_url):
        if not new_git_url.strip():
            raise ValueError('New git url is required to migrate_module_to_new_git_url.')
        query = self._get_mongo_query(module_name=module_name, git_url=current_git_url)
        record = self.modules.find_one(query, fields=['_id'])
        if not record:
            raise ValueError('Cannot migrate git_url, no module found with the given name and current url.')
        result = self.modules.update(query, {'$set':{'git_url':new_git_url.strip()}})
        return self._check_update_result(result)

    def delete_module(self,module_name, git_url):
        if not module_name and not git_url:
            raise ValueError('Module name or git url is required to delete a module.')
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module_details = self.modules.find_one(query)
        if not module_details:
            raise ValueError('No module matches this selection criteria')

        if module_details['current_versions']['release']:
            raise ValueError('Cannot delete module that has been released.  Make it inactive instead.')

        if module_details['release_version_list']:
            raise ValueError('Cannot delete module that has released versions.  Make it inactive instead.')

        result = self.modules.remove({'_id':module_details['_id']})
        return self._check_update_result(result)


    def add_favorite(self, module_name, app_id, username, timestamp):
        favoriteAddition = {
            'user':username,
            'module_name_lc':module_name.strip().lower(),
            'id':app_id.strip()
        }
        found = self.favorites.find_one(favoriteAddition)
        if found:
            # already a favorite, so do nothing
            return None;
        # keep a timestamp
        favoriteAddition['timestamp']= timestamp
        self.favorites.insert(favoriteAddition)

    def remove_favorite(self, module_name, app_id, username):
        favoriteAddition = {
            'user':username,
            'module_name_lc':module_name.strip().lower(),
            'id':app_id.strip()
        }
        found = self.favorites.find_one(favoriteAddition)
        if not found:
            # wasn't a favorite, so do nothing
            return None;

        result = self.favorites.remove({'_id':found['_id']})
        return self._check_update_result(result)


    def list_user_favorites(self, username):
        query = {'user':username}
        selection = {'_id':0,'module_name_lc':1,'id':1,'timestamp':1}
        return list(self.favorites.find(
                        query,selection,
                        sort=[['timestamp',DESCENDING]]))

    def list_app_favorites(self, module_name, app_id):
        query = {'module_name_lc':module_name.strip().lower(), 'id':app_id.strip()}
        selection = {'_id':0,'user':1,'timestamp':1}
        return list(self.favorites.find(
                        query,selection,
                        sort=[['timestamp',DESCENDING]]))


    def aggregate_favorites_over_apps(self, module_names_lc):
        ### WARNING! If we switch to Mongo 3.x, the result object will change and this will break

        # setup the query
        aggParams = None;
        group = { 
            '$group':{
                '_id':{
                    'm':'$module_name_lc',
                    'a':'$id'
                },
                'count':{ 
                    '$sum':1 
                }
            }
        }

        if len(module_names_lc) > 0 :
            match = { 
                '$match': { 
                    'module_name_lc': {
                        '$in':module_names_lc 
                    }
                }
            }
            aggParams = [match,group]
        else:
            aggParams = [group]

        # run the aggregation
        result = self.favorites.aggregate(aggParams)

        # figure out and return results
        counts = []
        for c in result['result']:
            counts.append({
                'module_name_lc':c['_id']['m'],
                'id' : c['_id']['a'],
                'count' : c['count']
                })
        return counts


    # assumes module names in app_ids are already lower 
    def set_client_group(self, app_id, client_groups):
        if not app_id:
            return

        if not client_groups:
            client_groups = []

        # lower case the module name on insert
        tokens = app_id.strip().split('/')
        if len(tokens)==2 :
            app_id = tokens[0].lower() + '/' + tokens[1];

        return self._check_update_result(self.client_groups.update(
                {'app_id':app_id},
                {'app_id':app_id, 'client_groups': client_groups },
                upsert=True
            ))

    def list_client_groups(self, app_ids):
        query = {}
        selection = {
            "_id": 0,
            "app_id": 1, 
            "client_groups": 1
        }
        if app_ids:
            query['app_id'] = { '$in':app_ids }

        return list(self.client_groups.find(query, selection))


    #### utility methods
    def _get_mongo_query(self, module_name='', git_url=''):
        query={}
        if module_name:
            query['module_name_lc'] = module_name.strip().lower()
        if git_url:
            query['git_url'] = git_url.strip()
        return query

    # if it worked, return None.  If it didn't return something indicating an error
    def _check_update_result(self, result):
        if result:
            # Can't check for nModified because KBase prod mongo is 2.4!! (as of 10/13/15)
            # we can only check for 'n'!!
            nModified = 0
            if 'n' in result:
                nModified = result['n']
            if 'nMatched' in result:
                nModified = result['nMatched']
            if nModified < 1:
                return pprint.pformat(result) #json.dumps(result)
            return None
        return '{}'

    def add_exec_stats_raw(self, user_id, app_module_name, app_id, func_module_name, func_name, 
                           git_commit_hash, creation_time, exec_start_time, finish_time, is_error):
        stats = {
            'user_id': user_id,
            'app_module_name': app_module_name,
            'app_id': app_id,
            'func_module_name': func_module_name,
            'func_name': func_name,
            'git_commit_hash': git_commit_hash,
            'creation_time': creation_time,
            'exec_start_time': exec_start_time,
            'finish_time': finish_time,
            'is_error': is_error
        }
        self.exec_stats_raw.insert(stats)

    def add_exec_stats_apps(self, app_module_name, app_id, creation_time, exec_start_time, 
                            finish_time, is_error, type, time_range):
        if not app_id:
            return
        full_app_id = app_id
        if app_module_name:
            full_app_id = app_module_name + "/" + app_id
        queue_time = exec_start_time - creation_time
        exec_time = finish_time - exec_start_time
        new_data = {
            'module_name': app_module_name
        }
        inc_data = {
            'number_of_calls': 1,
            'number_of_errors': 1 if is_error else 0,
            'total_queue_time': queue_time,
            'total_exec_time': exec_time
        }
        self.exec_stats_apps.update({'full_app_id': full_app_id, 'type': type, 'time_range': time_range}, 
                                    {'$setOnInsert': new_data, '$inc': inc_data}, upsert=True)

    def add_exec_stats_users(self, user_id, creation_time, exec_start_time, 
                             finish_time, is_error, type, time_range):
        queue_time = exec_start_time - creation_time
        exec_time = finish_time - exec_start_time
        inc_data = {
            'number_of_calls': 1,
            'number_of_errors': 1 if is_error else 0,
            'total_queue_time': queue_time,
            'total_exec_time': exec_time
        }
        self.exec_stats_users.update({'user_id': user_id, 'type': type, 'time_range': time_range}, 
                                     {'$inc': inc_data}, upsert=True)


    def get_exec_stats_apps(self, full_app_ids, type, time_range):
        filter = {}
        if full_app_ids:
            filter['full_app_id'] = {'$in': full_app_ids}
        filter['type'] = type
        if time_range:
            filter['time_range'] = time_range
        selection = {
            "_id": 0,
            "module_name": 1, 
            "full_app_id": 1,
            "type": 1, 
            "time_range": 1,
            "number_of_calls": 1, 
            "number_of_errors": 1, 
            "total_exec_time": 1, 
            "total_queue_time": 1 
        }
        return list(self.exec_stats_apps.find(filter, selection))

    def aggr_exec_stats_table(self, minTime, maxTime):

        # setup the query
        aggParams = None;
        group = {
            '$group':{
                '_id':{
                    'u':'$user_id',
                    'm':'$app_module_name',
                    'a':'$app_id',
                    'f':'$func_name',
                    'fm':'$func_module_name'
                },
                'count':{
                    '$sum':1
                }
            }
        }

        # filter times based on creation times
        creationTimeFilter = {}
        if minTime is not None:
            creationTimeFilter['$gt']=minTime
        if maxTime is not None:
            creationTimeFilter['$lt']=maxTime
        if len(creationTimeFilter)>0:
            match = {
                '$match': {
                    'creation_time': creationTimeFilter
                }
            }
            aggParams = [match,group]
        else:
            aggParams = [group]

        # run the aggregation
        result = self.exec_stats_raw.aggregate(aggParams)

        # process the result
        counts = []
        for c in result['result']:
            full_id = c['_id']['a']
            if c['_id']['m']:
                full_id = c['_id']['m'] + '/' + c['_id']['a']
            counts.append({
                'user':c['_id']['u'],
                'app' : full_id,
                'n' : c['count'],
                'func' : c['_id']['f'],
                'func_mod' : c['_id']['fm']
                })

        return counts

    


    # release versions used to be in a map, but this makes mongo queries difficult
    # here we switch that in an existing db to a release_version_list
    def correct_release_versions(self):
        for m in self.modules.find({'release_versions': {'$exists' : True}}):
            release_version_list = []
            for timestamp in m['release_versions']:
                release_version_list.append(m['release_versions'][timestamp])

            self.modules.update(
                {'_id':m['_id']},
                {
                    '$unset':{'release_versions':''},
                    '$set':{'release_version_list':release_version_list}
                })







