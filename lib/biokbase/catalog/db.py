

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
        module: str, (unique index)
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

        old_release_versions: {
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
        self.modules.create_index('module_name', unique=True)
        self.modules.create_index('git_url', unique=True)



    def is_registered(self,module_name='',git_url=''):
        if module_name:
            module = self.modules.find_one({'module_name':module_name}, fields=['_id'])
            if module is not None:
                return True
        elif git_url:
            module = self.modules.find_one({'git_url':git_url}, fields=['_id'])
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
                'registration': 'building',
            },
            'current_versions': {
                'release':None,
                'beta':None,
                'dev': {
                    'timestamp' : timestamp
                }
            },
            'old_release_versions': { }
        }
        self.modules.insert(module)


    # last_state is for concurency control.  If set, it will match on state as well, and will fail if the
    # last_state does not match indicating another process changed the state
    def set_module_registration_state(self, module_name='', git_url='', new_state=None, last_state=None, error_message=''):
        if new_state:
            if module_name:
                if last_state:
                    result = self.modules.update({'module_name':module_name,'state.registration':last_state}, {'$set':{'state.registration':new_state, 'state.error_message':error_message}})
                else:
                    result = self.modules.update({'module_name':module_name}, {'$set':{'state.registration':new_state, 'state.error_message':error_message}})
            if git_url:
                if last_state:
                    result = self.modules.update({'git_url':git_url,'state.registration':last_state}, {'$set':{'state.registration':new_state, 'state.error_message':error_message}})
                else:
                    result = self.modules.update({'git_url':git_url}, {'$set':{'state.registration':new_state, 'state.error_message':error_message}})
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


    #### GET methods
    def get_module_state(self, module_name='', git_url=''):
        if module_name:
            print('searching by module name ('+module_name+')');
            return self.modules.find_one({'module_name':module_name}, fields=['state'])['state']
        if git_url:
            print('searching by git url');
            return self.modules.find_one({'git_url':git_url}, fields=['state'])['state']
        return None

    def get_module_details(self, module_name='', git_url=''):
        if module_name:
            return self.modules.find_one({'module_name':module_name}, fields=['module_name','git_url','info','owners','state','current_versions'])
        if git_url:
            return self.modules.find_one({'git_url':git_url}, fields=['module_name','git_url','info','owners','state','current_versions'])
        return None

    def get_module_full_details(self, module_name='', git_url=''):
        if module_name:
            return self.modules.find_one({'module_name':module_name})
        if git_url:
            return self.modules.find_one({'git_url':git_url})
        return None


    #### LIST / SEARCH methods

    def list_module_names(self):
        return self.modules.find({},{'module_name':1,'git_url':1,'_id':0})






