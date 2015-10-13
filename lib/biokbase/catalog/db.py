

from pymongo import MongoClient


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



    def set_repo_registration_state(self, repo_url, state):

        new_state = {
            'git_url':repo_url,
            'state': { 'registration': state }
            }

        # if the record for this repo already exists, then we update
        # otherwise we add a new record.
        current_state = self.get_repo_registration_state(repo_url);
        if current_state:
            self.modules.update({'_id':current_state['_id']},new_state)
        else:
            self.modules.insert(new_state);


    def get_repo_registration_state(self, repo_url):
        return self.modules.find_one({'git_url':repo_url}, fields=['_id','module','registration_state'])


   # def save(self, document):
   #     print('saving dont work yet')
