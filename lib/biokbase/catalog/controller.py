

import warnings
import threading

import biokbase.catalog.version

from datetime import datetime
from biokbase.catalog.db import MongoCatalogDBI



class CatalogController:


    def __init__(self, config):

        # first grab the admin list
        self.adminList = []
        if 'admin-users' in config:
            self.adminList = [x.strip() for x in config['admin-users'].split(',')]
        if not self.adminList:
            warnings.warn('no "admin-users" are set in config of CatalogController.')
        print(self.adminList)

        # make sure the minimal mongo settings are in place
        if 'mongodb-host' not in config:
            raise ValueError('"mongodb-host" config variable must be defined to start a CatalogController!')
        if 'mongodb-database' not in config:
            raise ValueError('"mongodb-database" config variable must be defined to start a CatalogController!')

        # give warnings if no mongo user information is set
        if 'mongodb-user' not in config:
            warnings.warn('"mongodb-user" is not set in config of CatalogController.')
            config['mongodb-user']=''
            config['mongodb-pwd']=''
        if 'mongodb-pwd' not in config:
            warnings.warn('"mongodb-pwd" is not set in config of CatalogController.')
            config['mongodb-pwd']=''

        # instantiate the mongo client
        self.db = MongoCatalogDBI(
                    config['mongodb-host'],
                    config['mongodb-database'],
                    config['mongodb-user'],
                    config['mongodb-pwd'])

        self.registration_lock = threading.Lock()



    def register_repo(self, params, username):

        if 'git_url' not in params:
            raise ValueError('git_url not defined, but is required for registering a repository')
        git_url = params['git_url']
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()*1000)

        # 1) If the repo does not yet exist, then create it.  No permission checks needed
        if not self.db.is_registered(git_url) : 
            self.db.register_new_module(git_url, username, timestamp)
        
        # 2) If it has already been registered, make sure the user has permissions to update, and
        # that the module is in a state where it can be registered 
        else:
            # we need to lock so we don't kick off two registration builds at the same time
            # if another thread starts a registration, but hasn't written to mongo yet that it
            # has started
            self.registration_lock.acquire()
            try:
                module_details = self.db.get_module_details(git_url=git_url)

                # 2a) Make sure the user has permission to register this URL
                if self.has_permission(username,module_details['owners']):
                    # 2b) Make sure the current registration state is either 'complete' or 'error'
                    state = module_details['state']
                    registration_state = state['registration']
                    if registration_state == 'complete' or registration_state == 'error':
                        state['registration'] = 'started'
                        self.db.set_module_state(git_url=git_url, state=state)
                    else:
                        raise ValueError('Registration already in progress for this git repo ('+git_url+')')
                else :
                    raise ValueError('You ('+username+') do not have permission to register this git repo ('+git_url+')')
            finally:
                self.registration_lock.release()

        # 3) Ok, kick off the registration thread
        #   - This will check out the repo, attempt to build the image, run some tests, store the image
        #   - If all went well, and during the process, it will update the registration state of the
        #     module and finally update the dev version
        #   - If things failed, it will set the error state, and set an error message.


        # 4) provide the timestamp 
        return timestamp


    def has_permission(self, username, owners):
        if self.is_admin(username):
            return True
        for owner in owners:
            if username == owner['kb_username']:
                return True
        return False


    def is_admin(self, username):
        if username in self.adminList:
            return True
        return False


    def version(self):
        return biokbase.catalog.version.CATALOG_VERSION




