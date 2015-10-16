

from pprint import pprint
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
            error_message: str (optional)
            released: true | false (set to true if released, false or missing otherwise)
        },

        current_versions: {
            release: {
                timestamp:'',
                commit:''
            },
            beta: {
                timestamp:'',
                commit:''
            },
            dev: {
                timestamp:'',
                commit:''
            }
        }

        release_versions: {
            timestamp : {
                commit:''
            }
        }
    }

'''
class MongoCatalogDBI:

    # Collection Names

    _MODULES='modules'

    def __init__(self, mongo_host, mongo_db, mongo_user, mongo_psswd):

        # create the client
        self.mongo = MongoClient('mongodb://'+mongo_host)

        # Try to authenticate, will throw an exception if the user/psswd is not valid for the db
        if(mongo_user and mongo_psswd):
            self.mongo[mongo_db].authenticate(mongo_user, mongo_psswd)

        # Grab a handle to the database and collections
        self.db = self.mongo[mongo_db]
        self.modules = self.db[MongoCatalogDBI._MODULES]

        # Make sure we have an index on module and git_repo_url
        self.modules.create_index('module_name', unique=True, sparse=True)
        self.modules.create_index('git_url', unique=True)



    def is_registered(self,module_name='',git_url=''):
        if not module_name and not git_url:
            return False
        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        module = self.modules.find_one(query, fields=['_id'])
        if module is not None:
            return True
        return False


    #### SET methods

    def register_new_module(self, git_url, username, timestamp):
        # get current time since epoch in ms in utc
        module = {
            'info':{},
            'git_url':git_url,
            'owners':[{'kb_username':username}],
            'state': {
                'active': True,
                'release_approval': 'not_requested',
                'registration': 'building'
            },
            'current_versions': {
                'release':None,
                'beta':None,
                'dev': {
                    'timestamp' : timestamp
                }
            },
            'release_versions': { }
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


    def push_beta_to_release(self, module_name='', git_url=''):
        current_versions = self.get_module_current_versions(module_name=module_name, git_url=git_url)
        beta_version = current_versions['beta']

        query = self._get_mongo_query(module_name=module_name, git_url=git_url)
        query['current_versions.beta.timestamp'] = beta_version['timestamp']
        
        # we both update the release version, and since we archive release versions, we stash it in the release_versions list as well
        result = self.modules.update(query, {'$set':{
                                                'state.released':True,
                                                'current_versions.release':beta_version,
                                                'release_versions.'+str(beta_version['timestamp']):beta_version
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
        result = self.modules.update(query, {'$set':{'module_name':module_name}})
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



    #### utility methods
    def _get_mongo_query(self, module_name='', git_url=''):
        query={}
        if module_name:
            query['module_name'] = module_name
        if git_url:
            query['git_url'] = git_url
        return query

    def _check_update_result(self, result):
        if result:
            # Can't check for nModified because KBase prod mongo is 2.4!! (as of 10/13/15)
            # we can only check for 'n'!!
            nModified = 0
            if 'n' in result:
                nModified = result['n']
            if 'nMatched' in result:
                nModified = result['nMatched']
            if 'nModified' in result:
                nModified = result['nModified']
            if nModified < 1:
                return False
            return True
        return False





