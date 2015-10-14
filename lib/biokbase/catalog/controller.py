

import warnings
import threading
import time
import copy
import os

import biokbase.catalog.version

from pprint import pprint
from datetime import datetime
from biokbase.catalog.db import MongoCatalogDBI
from biokbase.catalog.registrar import Registrar






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

        # check for the temp directory and make sure it exists
        if 'temp-dir' not in config:
            raise ValueError('"temp-dir" config variable must be defined to start a CatalogController!')
        self.temp_dir = config['temp-dir']
        if not os.path.exists(self.temp_dir):
            raise ValueError('"temp-dir" does not exist! It is required for registration to work!')
        if not os.path.exists(self.temp_dir):
            raise ValueError('"temp-dir" does not exist! Space is required for registration to work!')
        if not os.access(self.temp_dir, os.W_OK):
            raise ValueError('"temp-dir" not writable! Writable space is required for registration to work!')



    def register_repo(self, params, username, token):

        if 'git_url' not in params:
            raise ValueError('git_url not defined, but is required for registering a repository')
        git_url = params['git_url']
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()*1000)

        # 1) If the repo does not yet exist, then create it.  No permission checks needed
        if not self.db.is_registered(git_url=git_url) : 
            self.db.register_new_module(git_url, username, timestamp)
        
        # 2) If it has already been registered, make sure the user has permissions to update, and
        # that the module is in a state where it can be registered 
        else:
            module_details = self.db.get_module_details(git_url=git_url)

            # 2a) Make sure the user has permission to register this URL
            if self.has_permission(username,module_details['owners']):
                # 2b) Make sure the current registration state is either 'complete' or 'error'
                state = module_details['state']
                registration_state = state['registration']
                if registration_state == 'complete' or registration_state == 'error':
                    success = self.db.set_module_registration_state(git_url=git_url, new_state='started', last_state=registration_state)
                    if not success:
                        # we can fail if the registration state changed when we were first checking to now.  This is important
                        # to ensure we only ever kick off one registration thread at a time
                        raise ValueError('Registration failed for git repo ('+git_url+') - registration state was modified before build could begin.')
                    # we know we are the only operation working, so we can clear the dev version and upate the timestamp
                    self.db.update_dev_version({'timestamp':timestamp}, git_url=git_url)
                else:
                    raise ValueError('Registration already in progress for this git repo ('+git_url+')')
            else :
                raise ValueError('You ('+username+') do not have permission to register this git repo ('+git_url+')')

        # 3) Ok, kick off the registration thread
        #   - This will check out the repo, attempt to build the image, run some tests, store the image
        #   - If all went well, and during the process, it will update the registration state of the
        #     module and finally update the dev version
        #   - If things failed, it will set the error state, and set an error message.

        # first set the dev current_release timestamp

        t = threading.Thread(target=_start_registration, args=(params,timestamp,username,token,self.db, self.temp_dir))
        t.start()

        # 4) provide the timestamp 
        return timestamp



    def set_registration_state(self, params, username):
        # first some error handling
        if not self.is_admin(username):
            raise ValueError('You do not have permission to modify the registration state of this module/repo.')
        params = self.filter_module_or_repo_selection(params)
        if 'registration_state' not in params:
            raise ValueError('Update failed - no registration state indicated.')
        #TODO: possibly check for empty states or that the state is a valid state here
        #if not params['registration_state'] :
        error_message = ''
        if params['registration_state'] == 'error':
            if 'error_message' not in params:
                raise ValueError('Update failed - if state is "error", you must also set an "error_message".')
            if params['error_message']:
                raise ValueError('Update failed - if state is "error", you must also set an "error_message".')
            error_message = params['error_message']
        else:
            # then we update the state
            success = self.db.set_module_registration_state(
                        git_url=params['git_url'],
                        module_name=params['module_name'],
                        new_state=params['registration_state'],
                        error_message=error_message)
            if not success:
                raise ValueError('Registration failed for git repo ('+git_url+')- some unknown mongo error.')


    def get_module_state(self, params):
        params = self.filter_module_or_repo_selection(params)
        return self.db.get_module_state(module_name=params['module_name'],git_url=params['git_url'])

    def is_registered(self,params):
        if 'git_url' not in params:
            params['git_url'] = ''
        if 'module_name' not in params:
            params['module_name'] = ''
        if self.db.is_registered(module_name=params['module_name'], git_url=params['git_url']) :
            return True
        return False

    def list_basic_module_info(self,params):
        query = { 'state.active':True }
        if 'include_disabled' in params:
            if params['include_disabled']>0:
                query.pop('state.active',None)
        return self.db.find_basic_module_info(query)





    # Some utility methods

    def filter_module_or_repo_selection(self, params):
        if 'git_url' not in params:
            params['git_url'] = ''
        if 'module_name' not in params:
            params['module_name'] = ''
        if not self.db.is_registered(module_name=params['module_name'], git_url=params['git_url']) :
            raise ValueError('Operation failed - module/repo is not registered.')
        return params


    # always true if the user is in the admin list
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


# NOT PART OF CLASS CATALOG!!
def _start_registration(params,timestamp,username,token, db, temp_dir):
    registrar = Registrar(params, timestamp, username, token, db, temp_dir)
    registrar.start_registration()

