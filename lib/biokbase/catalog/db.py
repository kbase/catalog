import copy
import pprint

from pymongo import ASCENDING
from pymongo import DESCENDING
from pymongo import MongoClient

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


LOCAL_FUNCTIONS

    {
        module_name:
        module_name_lc:
        version:
        git_commit_hash:
        functions:
        
    }
'''


class MongoCatalogDBI:

    # Collection Names

    _DB_VERSION='db_version' #single

    _MODULES='modules'

    _MODULE_VERSIONS='module_versions'

    _LOCAL_FUNCTIONS='local_functions'
    _DEVELOPERS='developers'
    _BUILD_LOGS='build_logs'
    _FAVORITES='favorites'
    _CLIENT_GROUPS='client_groups'
    _VOLUME_MOUNTS='volume_mounts'
    _EXEC_STATS_RAW='exec_stats_raw'
    _EXEC_STATS_APPS='exec_stats_apps'
    _EXEC_STATS_USERS='exec_stats_users'
    _SECURE_CONFIG_PARAMS='secure_config_params'

    def __init__(self, mongo_host, mongo_db, mongo_user, mongo_psswd):

        # create the client
        self.mongo = MongoClient('mongodb://'+mongo_host)

        # Try to authenticate, will throw an exception if the user/psswd is not valid for the db
        if(mongo_user and mongo_psswd):
            self.mongo[mongo_db].authenticate(mongo_user, mongo_psswd)

        # Grab a handle to the database and collections
        self.db = self.mongo[mongo_db]
        self.modules = self.db[MongoCatalogDBI._MODULES]
        self.module_versions = self.db[MongoCatalogDBI._MODULE_VERSIONS]

        self.local_functions = self.db[MongoCatalogDBI._LOCAL_FUNCTIONS]
        self.developers = self.db[MongoCatalogDBI._DEVELOPERS]
        self.build_logs = self.db[MongoCatalogDBI._BUILD_LOGS]
        self.favorites = self.db[MongoCatalogDBI._FAVORITES]
        self.client_groups = self.db[MongoCatalogDBI._CLIENT_GROUPS]
        self.volume_mounts = self.db[MongoCatalogDBI._VOLUME_MOUNTS]

        self.exec_stats_raw = self.db[MongoCatalogDBI._EXEC_STATS_RAW]
        self.exec_stats_apps = self.db[MongoCatalogDBI._EXEC_STATS_APPS]
        self.exec_stats_users = self.db[MongoCatalogDBI._EXEC_STATS_USERS]

        self.secure_config_params = self.db[MongoCatalogDBI._SECURE_CONFIG_PARAMS]

        # check the db schema
        self.check_db_schema()

        # Make sure we have an index on module and git_repo_url
        self.module_versions.create_index('module_name_lc', sparse=False)
        self.module_versions.create_index('git_commit_hash', sparse=False)
        self.module_versions.create_index([
            ('module_name_lc',ASCENDING),
            ('git_commit_hash',ASCENDING)], 
            unique=True, sparse=False)

        # Make sure we have a unique index on module_name_lc and git_commit_hash
        self.local_functions.create_index('function_id')
        self.local_functions.create_index([
            ('module_name_lc',ASCENDING),
            ('function_id',ASCENDING),
            ('git_commit_hash',ASCENDING)], 
            unique=True, sparse=False)

        # local function indecies
        self.local_functions.create_index('module_name_lc')
        self.local_functions.create_index('git_commit_hash')
        self.local_functions.create_index('function_id')
        self.local_functions.create_index([
            ('module_name_lc',ASCENDING),
            ('function_id',ASCENDING),
            ('git_commit_hash',ASCENDING)], 
            unique=True, sparse=False)

        # developers indecies
        self.developers.create_index('kb_username', unique=True)

        self.build_logs.create_index('registration_id',unique=True)
        self.build_logs.create_index('module_name_lc')
        self.build_logs.create_index('timestamp')
        self.build_logs.create_index('registration')
        self.build_logs.create_index('git_url')
        self.build_logs.create_index('current_versions.release.release_timestamp')

        # for favorites
        self.favorites.create_index('user')
        self.favorites.create_index('module_name_lc')
        self.favorites.create_index('id')
        # you can only favorite a method once, so put a unique index on the triple
        self.favorites.create_index([
            ('user',ASCENDING),
            ('id',ASCENDING),
            ('module_name_lc',ASCENDING)], 
            unique=True, sparse=False)

        # execution stats
        self.exec_stats_raw.create_index('user_id',
                                         unique=False, sparse=False)
        self.exec_stats_raw.create_index([('app_module_name', ASCENDING),
                                          ('app_id', ASCENDING)], 
                                         unique=False, sparse=True)
        self.exec_stats_raw.create_index([('func_module_name', ASCENDING),
                                          ('func_name', ASCENDING)], 
                                         unique=False, sparse=True)
        self.exec_stats_raw.create_index('creation_time',
                                         unique=False, sparse=False)
        self.exec_stats_raw.create_index('finish_time',
                                         unique=False, sparse=False)
        
        self.exec_stats_apps.create_index('module_name',
                                          unique=False, sparse=True)
        self.exec_stats_apps.create_index([('full_app_id', ASCENDING),
                                           ('type', ASCENDING),
                                           ('time_range', ASCENDING)], 
                                          unique=True, sparse=False)
        self.exec_stats_apps.create_index([('type', ASCENDING),
                                           ('time_range', ASCENDING)], 
                                          unique=False, sparse=False)

        self.exec_stats_users.create_index([('user_id', ASCENDING),
                                            ('type', ASCENDING),
                                            ('time_range', ASCENDING)], 
                                           unique=True, sparse=False)

        # client groups and volume mounts
        self.client_groups.create_index([('module_name_lc', ASCENDING),
                                            ('function_name', ASCENDING)], 
                                           unique=True, sparse=False)

        self.volume_mounts.create_index([('client_group', ASCENDING),
                                            ('module_name_lc', ASCENDING),
                                            ('function_name', ASCENDING)], 
                                           unique=True, sparse=False)

        # hidden configuration parameters
        self.secure_config_params.create_index('module_name_lc')
        self.secure_config_params.create_index([
            ('module_name_lc',ASCENDING),
            ('version',ASCENDING),
            ('param_name',ASCENDING)], 
            unique=True, sparse=False)

    def is_registered(self,module_name='',git_url=''):
        if not module_name and not git_url:
            return False
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module = self.modules.find_one(query, ['_id'])
        if module is not None:
            return True
        return False

    def module_name_lc_exists(self,module_name_lc=''):
        if not module_name_lc:
            return False
        module = self.modules.find_one({'module_name_lc':module_name_lc.lower()}, ['_id'])
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
        self.build_logs.insert_one(build_log)

    def delete_build_log(self, registration_id):
        self.build_logs.delete_one({'registration_id':registration_id})

    # new_lines is a list to objects, each representing a line
    # the object structure is : {'content':... 'error':True/False}
    def append_to_build_log(self,registration_id, new_lines):
        result = self.build_logs.update_one({'registration_id':registration_id},
            { '$push':{ 'log':{'$each':new_lines} } })
        return self._check_update_result(result)

    def set_build_log_state(self, registration_id, registration_state, error_message=''):
        result = self.build_logs.update_one({'registration_id':registration_id},
                    {'$set':{'registration':registration_state, 'error_message':error_message}})
        return self._check_update_result(result)

    def set_build_log_module_name(self, registration_id, module_name):
        result = self.build_logs.update_one({'registration_id':registration_id},
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

        # TODO: doesn't quite behave how you expect when passing multiple modules with mixed git urls and module names
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
                'dev': None
            },
            'release_version_list': []
        }
        self.modules.insert_one(module)

    # last_state is for concurency control.  If set, it will match on state as well, and will fail if the
    # last_state does not match indicating another process changed the state
    def set_module_registration_state(self, module_name='', git_url='', new_state=None, last_state=None, error_message=''):
        if new_state:
            query = self._get_mongo_query(module_name=module_name, git_url=git_url)
            if last_state:
                query['state.registration'] = last_state
            result = self.modules.update_one(query, {'$set':{'state.registration':new_state, 'state.error_message':error_message}})
            return self._check_update_result(result)
        return False

    def set_module_release_state(self, module_name='', git_url='', new_state=None, last_state=None, review_message=''):
        if new_state:
            query = self._get_mongo_query(module_name=module_name, git_url=git_url)
            if last_state:
                query['state.release_approval'] = last_state
            result = self.modules.update_one(query, {'$set':{'state.release_approval':new_state, 'state.review_message':review_message}})
            return self._check_update_result(result)
        return False

    def push_beta_to_release(self, module_name='', git_url='', release_timestamp=None):

        current_versions = self.get_module_current_versions(module_name=module_name, git_url=git_url, substitute_versions=False)
        beta_tag = current_versions['beta']

        if not release_timestamp:
            raise ValueError('internal error- timestamp not set in push_beta_to_release')

        # update the module version record with released=True, and the release_timestamp
        result = self.module_versions.update_one( { 'git_commit_hash':beta_tag['git_commit_hash'] },
                        { '$set': { 'released': 1, 'release_timestamp': release_timestamp } })
        if self._check_update_result(result) is not None:
            return self._check_update_result(result)

        # update the tags in the module document
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        result = self.modules.update_one(query, {'$set':{
                                                'state.released':True,
                                                'current_versions.release':beta_tag
                                                },
                                             '$push':{
                                                'release_version_list':beta_tag
                                                }})
        return self._check_update_result(result)

    def push_dev_to_beta(self, module_name='', git_url=''):
        current_versions = self.get_module_current_versions(module_name=module_name, git_url=git_url, substitute_versions=False)
        dev_tag = current_versions['dev']
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        result = self.modules.update_one(query, {'$set':{'current_versions.beta':dev_tag}})

        return self._check_update_result(result)

    def update_dev_version(self, version_info):
        if version_info:
            if 'git_commit_hash' in version_info and 'module_name_lc' in version_info:
                
                # try to insert
                try:
                    v_info_copy = copy.deepcopy(version_info) # copy because insert has side effects on the data if it fails, stupid mongo!
                    self.module_versions.insert_one(v_info_copy)
                # if that doesn't work, try to update (NOTE: by now this version should only be updatable if it is a dev or orphan version, and
                # we assume that check has already been made)
                except:
                    result = self.module_versions.replace_one( {
                                                    'module_name_lc':version_info['module_name_lc'],
                                                    'git_commit_hash':version_info['git_commit_hash']
                                                },
                                                version_info)
                    if self._check_update_result(result) is not None:
                        return self._check_update_result(result)
                query = self._get_mongo_query(module_name=version_info['module_name_lc'])
                result = self.modules.update_one(query, {'$set':{'current_versions.dev':{'git_commit_hash':version_info['git_commit_hash']}}})
                return self._check_update_result(result)
            else:
                raise ValueError('git_commit_hash is required to register a new version')
        return False

    def save_local_function_specs(self, local_functions):
        # just using insert doesn't accept a list of docs in mongo 2.6, so loop for now
        for l in local_functions:
            matcher = {'module_name_lc':l['module_name_lc'], 'function_id':l['function_id'], 'git_commit_hash':l['git_commit_hash']}
            # insert or update- allows us to capture the latest info if a specific commit is reregistered without adding a duplicate
            # or throwing an error
            result = self.local_functions.update_one(matcher, l, upsert=True)
            if self._check_update_result(result):
                error = self._check_update_result(result)
                error['mssg'] = 'An insert/upsert did not work on ' + l['function_id']
                return error
        return None

    def lookup_module_versions(self, module_name, git_commit_hash=None, released=None, included_fields=[], excluded_fields=[]):

        query = { 'module_name_lc':module_name.strip().lower() }

        if git_commit_hash is not None:
            query['git_commit_hash'] = git_commit_hash
        if released is not None:
            query['released'] = released

        selection = { '_id':0 }
        if len(included_fields) > 0:
            for f in included_fields:
                selection[f] = 1
        elif len(excluded_fields) > 0:
            for f in excluded_fields:
                selection[f] = 0

        return list(self.module_versions.find(query,selection))

    def list_local_function_info(self, release_tag=None, module_names=[]):

        git_commit_hash_list = []
        git_commit_hash_release_tag_map = {}

        # get all module brief info
        tag = 'release'
        if release_tag:
            if release_tag not in ['release','beta','dev']:
                raise ValueError('"release_tag" must be either release, beta or dev')
            tag = release_tag

        # might want to add a flag if a module ever has a local function
        query = {
            'state.active':True,
            'info.local_functions':1,
            'current_versions.'+tag+'.git_commit_hash': {'$exists':True}
        }

        check_mods = False
        mod_name_lc = []
        if len(module_names)>0:
            check_mods = True
            for m in module_names:
                mod_name_lc.append(m.strip().lower())

        # get the list of git commit hashes to query on
        git_commit_hash_list = []
        git_mod_name_lookup = {}
        for mod in self.db.modules.find(query, {'module_name_lc':1, 'current_versions':1, '_id':0}):
            if check_mods:
                if mod['module_name_lc'] not in mod_name_lc:
                    continue
            git_commit_hash_list.append(mod['current_versions'][tag]['git_commit_hash'])
            release_tags = []
            for rt in ['release', 'beta', 'dev']:
                if rt in mod['current_versions'] and mod['current_versions'][rt] is not None:
                    if 'git_commit_hash' in mod['current_versions'][rt]:
                        if mod['current_versions'][rt]['git_commit_hash'] == mod['current_versions'][tag]['git_commit_hash']:
                            release_tags.append(rt)
            git_mod_name_lookup[mod['module_name_lc']+mod['current_versions'][tag]['git_commit_hash']] = release_tags

        # get the local functions
        included_fields = {
            '_id':0,
            'module_name':1,
            'module_name_lc':1,
            'function_id':1,
            'git_commit_hash':1,
            'version':1,
            'name':1,
            'short_description':1,
            'tags':1,
            'authors':1
        }
        local_funcs = list(self.db.local_functions.find({'git_commit_hash':{'$in':git_commit_hash_list}}, included_fields))

        # set the release_tag field
        returned_funcs = []
        for l in local_funcs:
            if (l['module_name_lc'] + l['git_commit_hash']) in git_mod_name_lookup:
                l['release_tag'] = git_mod_name_lookup[l['module_name_lc'] + l['git_commit_hash']]
                del(l['module_name_lc'])
                returned_funcs.append(l)

        return returned_funcs

    def get_local_function_spec(self, functions):

        result_list = []

        # first lookup all the module info so we can figure out any tags, and make a quick dict
        module_name_lc_lookup = []
        for f in functions:
            module_name_lc_lookup.append(f['module_name'].lower())

        mods = list(self.db.modules.find({'module_name_lc' : {'$in': module_name_lc_lookup}},
                        {   
                            '_id':0,
                            'module_name_lc':1,
                            'current_versions':1
                        }))

        mod_lookup = {}
        git_hash_release_tag_lookup = {}
        for m in mods:
            mod_lookup[m['module_name_lc']] = m
            for tag in ['release','beta','dev']:
                if tag in m['current_versions'] and m['current_versions'][tag] is not None:
                    if 'git_commit_hash' in m['current_versions'][tag]:
                        key = m['module_name_lc']+m['current_versions'][tag]['git_commit_hash']
                        if key in git_hash_release_tag_lookup:
                            git_hash_release_tag_lookup[key].append(tag)
                        else:
                            git_hash_release_tag_lookup[key] = [tag]

        # for now be lazy and break up the call into separate queries and loops over mod list...   lots of optimization you could do here
        # although we expect in general, most users will only get module details one at a time 
        for f in functions:
            query = {
                'module_name_lc':f['module_name'].lower(),
                'function_id':f['function_id']
            }

            if 'release_tag' in f:
                if query['module_name_lc'] not in mod_lookup:
                    continue
                module = mod_lookup[query['module_name_lc']]
                if f['release_tag'] in module['current_versions'] and module['current_versions'][f['release_tag']] is not None:
                    if 'git_commit_hash' in m['current_versions'][f['release_tag']]:
                        query['git_commit_hash'] = m['current_versions'][f['release_tag']]['git_commit_hash']
                else:
                    continue
                if 'git_commit_hash' in f:
                    if f['git_commit_hash'] != query['git_commit_hash']:
                        raise ValueError(f"For lookup: {f['module_name']}.{f['function_id']}, "
                                         f"{f['release_tag']} tag commit hash "
                                         f"({query['git_commit_hash']}) does not match selector "
                                         f"you gave ({f['git_commit_hash']})")
            else:
                if 'git_commit_hash' in f:
                    query['git_commit_hash'] = f['git_commit_hash']
                else:
                    if query['module_name_lc'] not in mod_lookup: 
                        continue
                    module = mod_lookup[query['module_name_lc']]
                    for t in ['release', 'beta', 'dev']:
                        if t in module['current_versions'] and module['current_versions'][t] is not None:
                            if 'git_commit_hash' in module['current_versions'][t]:
                                query['git_commit_hash'] = module['current_versions'][t]['git_commit_hash']
                                break
                    
            if 'git_commit_hash' not in query:
                # no version to be found, because we couldn't figure out what to lookup...
                continue

            # ok, finally do the query
            function_data = self.db.local_functions.find_one(query, { '_id':0 })

            # if we didn't get anything, then the git_commit_hash or function_id was wrong, and we just continue
            if function_data is None:
                continue

            long_description = function_data['long_description']
            del(function_data['long_description'])
            key = function_data['module_name_lc'] + function_data['git_commit_hash']
            if key in git_hash_release_tag_lookup:
                function_data['release_tag'] = git_hash_release_tag_lookup[key]
            else:
                function_data['release_tag'] = []

            del(function_data['module_name_lc']) # this is for internal use only
            result_list.append({
                'info': function_data,
                'long_description': long_description
            })

        return result_list

    def set_module_name(self, git_url, module_name):
        if not module_name:
            raise ValueError('module_name must be defined to set a module name')
        query = self._get_mongo_query(git_url=git_url)
        result = self.modules.update_one(query, {'$set':{'module_name':module_name,'module_name_lc':module_name.lower()}})
        return self._check_update_result(result)

    def set_module_info(self, info, module_name='', git_url=''):
        if not info:
            raise ValueError('info must be defined to set the info for a module')
        if type(info) is not dict:
            raise ValueError('info must be a dictionary')
        query = self._get_mongo_query(git_url=git_url, module_name=module_name)
        result = self.modules.update_one(query, {'$set':{'info':info}})
        return self._check_update_result(result)

    def set_module_owners(self, owners, module_name='', git_url=''):
        if not owners:
            raise ValueError('owners must be defined to set the owners for a module')
        if type(owners) is not list:
            raise ValueError('owners must be a list')
        query = self._get_mongo_query(git_url=git_url, module_name=module_name)
        result = self.modules.update_one(query, {'$set':{'owners':owners}})
        return self._check_update_result(result)

    # active = True | False
    def set_module_active_state(self, active, module_name='', git_url=''):
        query = self._get_mongo_query(git_url=git_url, module_name=module_name)
        result = self.modules.update_one(query, {'$set':{'state.active':active}})
        return self._check_update_result(result)

    #### GET methods
    def get_module_state(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query, ['state'])['state']

    def get_module_current_versions(self, module_name='', git_url='', substitute_versions=True):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module_document = self.modules.find_one(query, ['module_name_lc','current_versions'])
        if substitute_versions and 'module_name_lc' in module_document:
            self.substitute_hashes_for_version_info([module_document])
        return module_document['current_versions']

    def get_module_owners(self, module_name='', git_url=''):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        return self.modules.find_one(query, ['owners'])['owners']

    def get_module_details(self, module_name='', git_url='', substitute_versions=True):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module_details = self.modules.find_one(query, ['module_name','module_name_lc','git_url',
                                                       'info','owners','state', 'current_versions'])
        if substitute_versions and 'module_name_lc' in module_details:
            self.substitute_hashes_for_version_info([module_details])
        return module_details

    def get_module_full_details(self, module_name='', git_url='', substitute_versions=True):
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module_document = self.modules.find_one(query)
        if substitute_versions and 'module_name_lc' in module_document:
            self.substitute_hashes_for_version_info([module_document])
        return module_document

    #### LIST / SEARCH methods

    def find_basic_module_info(self, query):
        selection = {
            '_id':0,
            'module_name':1,
            'git_url':1,
            'info':1,
            'current_versions':1,
            'release_version_list':1,
            'owners':1
        }
        return list(self.modules.find(query,selection))

    def find_current_versions_and_owners(self, query):
        result = list(self.modules.find(query,{'module_name':1,'module_name_lc':1,'git_url':1,'current_versions':1,'owners':1,'_id':0}))
        self.substitute_hashes_for_version_info(result)
        return result

    def substitute_hashes_for_version_info(self, module_list):

        # get all the version commit hashes
        hash_list = []
        for mod in module_list:
            if 'module_name_lc' not in mod:
                raise ValueError('DB Error: module_name_lc must be specified to get version documents')

            if 'current_versions' in mod:
                for tag in ['release', 'beta', 'dev']:
                    if tag in mod['current_versions'] and mod['current_versions'][tag] is not None:
                        if 'git_commit_hash' in mod['current_versions'][tag]:
                            hash_list.append(mod['current_versions'][tag]['git_commit_hash'])

            if 'release_version_list' in mod:
                for r in mod['release_version_list']:
                    if 'git_commit_hash' in r:
                        hash_list.append(r['git_commit_hash'])

        # lookup the info, save it to a dict
        ver_lookup = {}
        for ver in self.module_versions.find({'git_commit_hash': {'$in':hash_list}},{'_id':0}):
            if ver['module_name_lc'] not in ver_lookup:
                ver_lookup[ver['module_name_lc']] = {}
            ver_lookup[ver['module_name_lc']][ver['git_commit_hash']] = ver

        # replace them
        for mod in module_list:
            if 'current_versions' in mod:
                for tag in ['release', 'beta', 'dev']:
                    if tag in mod['current_versions'] and mod['current_versions'][tag] is not None:
                        if 'git_commit_hash' in mod['current_versions'][tag]:
                            mod['current_versions'][tag] = ver_lookup[mod['module_name_lc']][mod['current_versions'][tag]['git_commit_hash']]

            if 'release_version_list' in mod:
                new_release_version_list = []
                for r in mod['release_version_list']:
                    if 'git_commit_hash' in r:
                        new_release_version_list.append(ver_lookup[mod['module_name_lc']][r['git_commit_hash']])
                mod['release_version_list'] = new_release_version_list

        return module_list

    # tag should be one of dev, beta, release - do checking outside of this method
    def list_service_module_versions_with_tag(self, tag):

        mods = list(self.modules.find({'info.dynamic_service':1}, {'module_name_lc':1, 'module_name':1, 'current_versions.'+tag : 1 }))
        self.substitute_hashes_for_version_info(mods)

        result = []
        for m in mods:
            if tag in m['current_versions'] and m['current_versions'][tag] is not None:
                if 'dynamic_service' in m['current_versions'][tag] and m['current_versions'][tag]['dynamic_service'] == 1:
                    result.append({
                            'module_name':m['module_name'],
                            'version':m['current_versions'][tag]['version'],
                            'git_commit_hash':m['current_versions'][tag]['git_commit_hash'],
                            'docker_img_name':m['current_versions'][tag]['docker_img_name']

                        })
        return result

    # all released service module versions
    def list_all_released_service_module_versions(self):
        return list(self.module_versions.find(
            {
                'dynamic_service':1,
                'released':1
            },
            {
                'module_name':1,
                'version':1,
                'git_commit_hash':1,
                'docker_img_name':1,
                '_id':0
            }))

    #### developer check methods

    def approve_developer(self, developer):
        # if the developer is already on the list, just return
        if self.is_approved_developer([developer])[0]:
            return
        self.developers.insert_one({'kb_username':developer})

    def revoke_developer(self, developer):
        # if the developer is not on the list, throw an error (maybe a typo, so let's catch it)
        if not self.is_approved_developer([developer])[0]:
            raise ValueError('Cannot revoke "'+developer+'", that developer was not found.')
        self.developers.delete_one({'kb_username':developer})

    def is_approved_developer(self, usernames):
        #TODO: optimize, but I expect the list of usernames will be fairly small, so we can loop.  Regardless, in
        # old mongo (2.x) I think this is even faster in most cases than using $in within a very large list
        is_approved = []
        for u in usernames:
            count = self.developers.count_documents({'kb_username':u})
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
        record = self.modules.find_one(query, ['_id'])
        if not record:
            raise ValueError('Cannot migrate git_url, no module found with the given name and current url.')
        result = self.modules.update_one(query, {'$set':{'git_url':new_git_url.strip()}})
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

        result = self.modules.delete_one({'_id':module_details['_id']})
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
            return None
        # keep a timestamp
        favoriteAddition['timestamp']= timestamp
        self.favorites.insert_one(favoriteAddition)

    def remove_favorite(self, module_name, app_id, username):
        favoriteAddition = {
            'user':username,
            'module_name_lc':module_name.strip().lower(),
            'id':app_id.strip()
        }
        found = self.favorites.find_one(favoriteAddition)
        if not found:
            # wasn't a favorite, so do nothing
            return None

        result = self.favorites.delete_one({'_id':found['_id']})
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
        aggParams = None
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
        for c in result:
            counts.append({
                'module_name_lc':c['_id']['m'],
                'id' : c['_id']['a'],
                'count' : c['count']
                })
        return counts

    # DEPRECATED! temporary function until everything is migrated to new client group structure
    def list_client_groups(self, app_ids):
        if app_ids is not None:
            selection = {
                '_id': 0,
                'function_name': 1, 
                'client_groups': 1,
                'module_name':1,
                'module_name_lc':1
            }
            gList = list(self.client_groups.find({}, selection))
            filteredGList = []
            for g in gList:
                for a in app_ids:
                    if g['module_name_lc'] + '/' + g['function_name'] == a:
                        filteredGList.append(g)
            for g in filteredGList:
                del[g['module_name_lc']]
            return filteredGList
        
        selection = {
            '_id': 0,
            'function_name': 1, 
            'client_groups': 1,
            'module_name':1
        }
        return list(self.client_groups.find({}, selection))

    def set_client_group_config(self, config):
        config['module_name_lc'] = config['module_name'].lower()
        return self._check_update_result(self.client_groups.replace_one(
                {
                    'module_name_lc':config['module_name_lc'],
                    'function_name':config['function_name']
                },
                config,
                upsert=True
            ))

    def remove_client_group_config(self, config):
        config['module_name_lc'] = config['module_name'].lower()
        return self._check_update_result(self.client_groups.delete_one(
                {
                    'module_name_lc':config['module_name_lc'],
                    'function_name':config['function_name']
                }
            ))

    def list_client_group_configs(self, filter):
        selection = { "_id": 0, "module_name_lc":0 }
        if 'module_name' in filter:
            filter['module_name_lc'] = filter['module_name'].lower()
            del(filter['module_name'])
        return list(self.client_groups.find(filter, selection))

    def set_volume_mount(self, volume_mount):
        volume_mount['module_name_lc'] = volume_mount['module_name'].lower()
        return self._check_update_result(self.volume_mounts.replace_one(
                {
                    'module_name_lc':volume_mount['module_name_lc'],
                    'function_name':volume_mount['function_name'],
                    'client_group':volume_mount['client_group']
                },
                volume_mount,
                upsert=True
            ))

    def remove_volume_mount(self, volume_mount):
        volume_mount['module_name_lc'] = volume_mount['module_name'].lower()
        return self._check_update_result(self.volume_mounts.delete_one(
                {
                    'module_name_lc':volume_mount['module_name_lc'],
                    'function_name':volume_mount['function_name'],
                    'client_group':volume_mount['client_group']
                }))

    def list_volume_mounts(self, filter):
        selection = { "_id": 0, "module_name_lc":0 }
        if 'module_name' in filter:
            filter['module_name_lc'] = filter['module_name'].lower()
            del(filter['module_name'])
        return list(self.volume_mounts.find(filter, selection))


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
        # TODO: This is an odd function. I modded it to maintain compatability but it seems like it should be rethought
        if result:
            # downgrades new DeleteResult and UpdateResult to old behavior
            if hasattr(result, "raw_result"):
                result = result.raw_result
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
                           git_commit_hash, creation_time, exec_start_time, finish_time, is_error,
                           job_id):
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
            'is_error': is_error,
            'job_id': job_id
        }
        self.exec_stats_raw.insert_one(stats)

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
        self.exec_stats_apps.update_one({'full_app_id': full_app_id, 'type': type, 'time_range': time_range},
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
        self.exec_stats_users.update_one({'user_id': user_id, 'type': type, 'time_range': time_range},
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
        aggParams = None
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
        for c in result:
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

    def get_exec_raw_stats(self, minTime, maxTime):

        filter = {}
        creationTimeFilter = {}
        if minTime is not None:
            creationTimeFilter['$gt']=minTime
        if maxTime is not None:
            creationTimeFilter['$lt']=maxTime
        if len(creationTimeFilter)>0:
            filter = {
                'creation_time': creationTimeFilter
            }

        return list(self.exec_stats_raw.find(filter, {'_id':0}))
    
    def set_secure_config_params(self, data_list):
        for param_data in data_list:
            param_data['module_name_lc'] = param_data['module_name'].lower()
            param_data['version'] = param_data.get('version', '')
            self.secure_config_params.replace_one(
                {
                    'module_name_lc': param_data['module_name_lc'],
                    'version': param_data['version'],
                    'param_name': param_data['param_name']
                },
                param_data,
                upsert=True)

    def remove_secure_config_params(self, data_list):
        for param_data in data_list:
            param_data['module_name_lc'] = param_data['module_name'].lower()
            param_data['version'] = param_data.get('version', '')
            self.secure_config_params.delete_one(
                {
                    'module_name_lc':param_data['module_name_lc'],
                    'version':param_data['version'],
                    'param_name':param_data['param_name']
                })

    def get_secure_config_params(self, module_name):
        selection = { "_id": 0, "module_name_lc": 0 }
        filter = { "module_name_lc": module_name.lower() }
        return list(self.secure_config_params.find(filter, selection))

    # DB version handling

    # todo: add 'in-progress' flag so if something goes done during an update, or if
    # another server is already starting an update, we can skip or abort
    def check_db_schema(self):

        db_version = self.get_db_version()
        print('db_version=' + str(db_version))

        if db_version<2:
            print('Updating DB schema to V2...')
            self.update_db_1_to_2()
            self.update_db_version(2)
            print('done.')

        if db_version<3:
            print('Updating DB schema to V3...')
            self.update_db_2_to_3()
            self.update_db_version(3)
            print('done.')

        if db_version<4:
            print('Updating DB schema to V4...')
            self.update_db_3_to_4()
            self.update_db_version(4)
            print('done.')

        if db_version>4:
            # bad version!
            raise IOError('Incompatible DB versions.  Expecting DB V4, found DV V'+str(db_version) + 
                '. You are probably running an old version of the service.  Start up failed.')

    def get_db_version(self):
        # version is a collection that should only have a single 
        version_collection = self.db[MongoCatalogDBI._DB_VERSION]
        ver = version_collection.find_one({})
        if(ver):
            return ver['version']
        else:
            # if there is no version document, then we are DB v1
            self.update_db_version(1)
            return 1

    def update_db_version(self, version):
        # make sure we can't have two version documents
        version_collection = self.db[MongoCatalogDBI._DB_VERSION]
        version_collection.create_index('version_doc', unique=True, sparse=False)
        version_collection.update_one({'version_doc': True}, {'$set': {'version': version}},
                                      upsert=True)

    # version 1 kept released module versions in a map, version 2 updates that to a list
    # and adds dynamic service tags
    def update_db_1_to_2(self):
        for m in self.modules.find({'release_versions': {'$exists' : True}}):
            release_version_list = []
            for timestamp in m['release_versions']:
                m['release_versions'][timestamp]['dynamic_service'] = 0
                release_version_list.append(m['release_versions'][timestamp])

            self.modules.update_one(
                {'_id':m['_id']},
                {
                    '$unset':{'release_versions':''},
                    '$set':{'release_version_list':release_version_list}
                })

            # make sure everything has the dynamic service flag
            if not 'dynamic_service' in m['info']:
                    self.modules.update_one(
                        {'_id':m['_id']},
                        {'$set':{'info.dynamic_service':0}})

            if m['current_versions']['release']:
                if not 'dynamic_service' in m['current_versions']['release']:
                    self.modules.update_one(
                        {'_id':m['_id']},
                        {'$set':{'current_versions.release.dynamic_service':0}})

            if m['current_versions']['beta']:
                if not 'dynamic_service' in m['current_versions']['beta']:
                    self.modules.update_one(
                        {'_id':m['_id']},
                        {'$set':{'current_versions.beta.dynamic_service':0}})

            if m['current_versions']['dev']:
                if not 'dynamic_service' in m['current_versions']['dev']:
                    self.modules.update_one(
                        {'_id':m['_id']},
                        {'$set':{'current_versions.dev.dynamic_service':0}})

        # also ensure the execution stats fields have correct names
        self.exec_stats_apps.update_many({'avg_queue_time': {'$exists': True}},
                                         {'$rename': {'avg_queue_time': 'total_queue_time',
                                                      'avg_exec_time': 'total_exec_time'}})
        self.exec_stats_users.update_many({'avg_queue_time': {'$exists' : True}},
                                          {'$rename': {'avg_queue_time': 'total_queue_time',
                                                       'avg_exec_time': 'total_exec_time'}})



    # version 3 moves the module version information out of the module document into
    # a separate module versions collection.  
    def update_db_2_to_3(self):

        self.module_versions.create_index('module_name_lc', sparse=False)
        self.module_versions.create_index('git_commit_hash', sparse=False)
        self.module_versions.create_index([
            ('module_name_lc',ASCENDING),
            ('git_commit_hash',ASCENDING)], 
            unique=True, sparse=False)

        # update all module versions
        for m in self.modules.find({}):

            # skip modules that have not been properly registered, might want to delete these later
            if 'module_name' not in m or 'module_name_lc' not in m:
                continue

            # skip modules that have not been properly registered, might want to delete these later
            if 'info' not in m:
                continue

            # first migrate over all released versions and update the module document
            new_release_version_list = []
            for rVer in m['release_version_list']:
                rVer['released'] = 1
                self.prepare_version_doc_for_db_2_to_3_update(rVer, m)
                try:
                    self.module_versions.insert_one(rVer)
                except:
                    print(' - Warning - '+rVer['module_name'] + '.' + rVer['git_commit_hash'] + ' already inserted, skipping.')
                new_release_version_list.append({
                    'git_commit_hash':rVer['git_commit_hash']
                })
            self.modules.update_one(
                    {'_id':m['_id']},
                    {'$set':{ 'release_version_list':new_release_version_list } }
                )

            for tag in ['release','beta','dev']: # we can skip release tags because that is already in the release_version_list
                if tag in m['current_versions'] and m['current_versions'][tag] is not None:
                    modVer = m['current_versions'][tag]
                    modVer['released'] = 0
                    self.prepare_version_doc_for_db_2_to_3_update(modVer, m)
                    if 'git_commit_hash' in modVer and modVer['git_commit_hash'] is not None:
                        try:
                            self.module_versions.insert_one(modVer)
                        except Exception as e:
                            # we expect this to happen for all 'release' tags and if, say, a version still tagged as dev/beta has been released
                            print(' - Warning - '+tag+ ' ver of ' + modVer['module_name'] + '.' + modVer['git_commit_hash'] + ' already inserted, skipping.')
                        self.modules.update_one(
                            {'_id':m['_id']},
                            {'$set':{ 'current_versions.'+tag: {'git_commit_hash':modVer['git_commit_hash']} } }
                        )
                    else:
                        self.modules.update_one(
                            {'_id':m['_id']},
                            {'$set':{ 'current_versions.'+tag: None } }
                        )
            print(' -> completed '+m['module_name'])

    def prepare_version_doc_for_db_2_to_3_update(self, version, module):
        version['module_name'] = module['module_name']
        version['module_name_lc'] = module['module_name_lc']
        version['module_description'] = module['info']['description']
        version['module_language'] = module['info']['language']
        version['notes'] = ''
        if 'local_functions' not in version:
            version['local_functions'] = []
        if 'compilation_report' not in version:
            version['compilation_report'] = None
        if 'narrative_methods' not in version:
            version['narrative_methods'] = []
        if 'release_timestamp' not in version:
            if version['released']==1:
                version['release_timestamp'] = version['timestamp']
            else:
                 version['release_timestamp'] = None

    # version 4 performs a small modification to the client group structure and volume_mounts structure
    def update_db_3_to_4(self):

        # make sure we don't have any indecies on the collections
        self.volume_mounts.drop_indexes()
        self.client_groups.drop_indexes()

        # update the volume_mounts, just need to rename app_id to function_name
        for vm in self.volume_mounts.find({}):
            if 'app_id' in vm and 'function_name' not in vm:
                self.volume_mounts.update_one(
                        {'_id':vm['_id']},
                        {'$set':{ 'function_name':vm['app_id'] }, '$unset':{ 'app_id':1 } }
                    )

        for cg in self.client_groups.find({}):
            if 'app_id' in cg:
                self.client_groups.delete_one({'_id':cg['_id']})
                tokens = cg['app_id'].split('/')
                if(len(tokens) != 2):
                    print('   When updating client groups, bad app_id found.  Record will be lost:')
                    pprint.pprint(cg)
                new_cg = {
                    'module_name' : tokens[0],
                    'module_name_lc' : tokens[0].lower(),
                    'function_name' : tokens[1],
                    'client_groups' : cg['client_groups']
                }
                self.client_groups.insert_one(new_cg)
