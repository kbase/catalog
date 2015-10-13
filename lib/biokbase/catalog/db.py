

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
        self.modules.create_index('module', unique=True)
        self.modules.create_index('git_url', unique=True)


    def module_exists(self, module):
        if module_name:
            module = self.modules.find_one({'module':module}, fields=['_id'])
            if module is not None:
                return True
        return False

    def is_registered(self, git_url):
        if git_url:
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


    def set_module_state(self, module='', git_url='', state=None):
        if state:
            if module:
                self.modules.update( {'module':module}, {'$set':{'state':state}})
            if git_url:
                self.modules.update( {'git_url':git_url}, {'$set':{'state':state}})



    #### GET methods

    def get_module_state(self, module='', git_url=''):
        if module:
            return self.modules.find_one({'module':module}, fields=['module','git_url','state'])
        if git_url:
            return self.modules.find_one({'git_url':git_url}, fields=['module','git_url','state'])
        return None

    def get_module_details(self, module='', git_url=''):
        if module:
            return self.modules.find_one({'module':module}, fields=['module','git_url','info','owners','state','current_versions'])
        if git_url:
            return self.modules.find_one({'git_url':git_url}, fields=['module','git_url','info','owners','state','current_versions'])
        return None

    def get_module_full_details(self, module='', git_url=''):
        if module:
            return self.modules.find_one({'module':module})
        if git_url:
            return self.modules.find_one({'git_url':git_url})
        return None


    #### LIST / SEARCH methods

    def list_module_names(self):
        return self.modules.find({},{'module':1,'git_url':1,'_id':0})






