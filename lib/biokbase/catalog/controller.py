

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

        if 'docker-base-url' not in config:
            raise ValueError('"docker-base-url" config variable must be defined to start a CatalogController!')
        self.docker_base_url = config['docker-base-url']
        print(self.docker_base_url)

        if 'nms-url' not in config:
            raise ValueError('"nms-url" config variable must be defined to start a CatalogController!')
        self.nms_url = config['nms-url']
        if 'nms-admin-user' not in config:
            raise ValueError('"nms-admin-user" config variable must be defined to start a CatalogController!')
        self.nms_admin_user = config['nms-admin-user']
        if 'nms-admin-psswd' not in config:
            raise ValueError('"nms-admin-psswd" config variable must be defined to start a CatalogController!')
        self.nms_admin_psswd = config['nms-admin-psswd']


    def register_repo(self, params, username, token):

        if 'git_url' not in params:
            raise ValueError('git_url not defined, but is required for registering a repository')
        git_url = params['git_url']
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()*1000)

        # 1) If the repo does not yet exist, then create it.  No permission checks needed
        if not self.db.is_registered(git_url=git_url) : 
            self.db.register_new_module(git_url, username, timestamp)
            module_details = self.db.get_module_details(git_url=git_url)
        
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

        t = threading.Thread(target=_start_registration, args=(params,timestamp,username,token,self.db, self.temp_dir, self.docker_base_url, 
            self.nms_url, self.nms_admin_user, self.nms_admin_psswd, module_details))
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
                raise ValueError('Registration failed for git repo ('+git_url+')- some unknown database error.')


    def push_dev_to_beta(self, params, username):
        # first make sure everything exists and we have permissions
        params = self.filter_module_or_repo_selection(params)
        module_details = self.db.get_module_details(module_name=params['module_name'],git_url=params['git_url'])
        if not self.has_permission(username,module_details['owners']):
            raise ValueError('You do not have permission to modify this module/repo.')
        # next make sure the state of the module is ok (it must be active, no pending registrations or release requests)
        if not module_details['state']['active']:
            raise ValueError('Cannot push dev to beta- module/repo is no longer active.')
        if module_details['state']['registration'] != 'complete':
            raise ValueError('Cannot push dev to beta- last registration is in progress or has an error.')
        if module_details['state']['release_approval'] == 'under_review':
            raise ValueError('Cannot push dev to beta- last release request of beta is still pending.')
        # ok, do it.
        success = self.db.push_dev_to_beta(module_name=params['module_name'],git_url=params['git_url'])
        if not success:
            raise ValueError('Update operation failed - some unknown database error.')

    def request_release(self, params, username):
        # first make sure everything exists and we have permissions
        params = self.filter_module_or_repo_selection(params)
        module_details = self.db.get_module_details(module_name=params['module_name'],git_url=params['git_url'])
        if not self.has_permission(username,module_details['owners']):
            raise ValueError('You do not have permission to modify this module/repo.')
        # next make sure the state of the module is ok (it must be active, no pending release requests)
        if not module_details['state']['active']:
            raise ValueError('Cannot request release - module/repo is no longer active.')
        if module_details['state']['release_approval'] == 'under_review':
            raise ValueError('Cannot request release - last release request of beta is still pending.')
        # beta version must exist
        if not module_details['current_versions']['beta']:
            raise ValueError('Cannot request release - no beta version has been created yet.')

        # beta version must be different than release version (if release version exists)
        if module_details['current_versions']['release']:
            if module_details['current_versions']['beta']['timestamp'] == module_details['current_versions']['release']['timestamp']:
                raise ValueError('Cannot request release - beta version is identical to released version.')

        # ok, do it.
        success = self.db.set_module_release_state(
                        module_name=params['module_name'],git_url=params['git_url'],
                        new_state='under_review',
                        last_state=module_details['state']['release_approval']
                    )
        if not success:
            raise ValueError('Release request failed - some unknown database error.')

    def list_requested_releases(self):
        query={'state.release_approval':'under_review'}
        results=self.db.find_current_versions_and_owners(query)
        requested_releases = []
        for r in results:
            owners = []
            for o in r['owners']:
                owners.append(o['kb_username'])
            beta = r['current_versions']['beta']
            timestamp = beta['timestamp']
            requested_releases.append({
                    'module_name':r['module_name'],
                    'git_url':r['git_url'],
                    'timestamp':timestamp,
                    'git_commit_hash':beta['git_commit_hash'],
                    'git_commit_message':beta['git_commit_message'],
                    'owners':owners
                })
        return requested_releases


    def review_release_request(self, review, username):
        if not self.is_admin(username):
            raise ValueError('You do not have permission to review a release request.')
        review = self.filter_module_or_repo_selection(review)

        module_details = self.db.get_module_details(module_name=review['module_name'],git_url=review['git_url'])
        if module_details['state']['release_approval'] != 'under_review':
            raise ValueError('Cannot review request - module/repo is not under review!')

        if not module_details['state']['active']:
            raise ValueError('Cannot review request - module/repo is no longer active.')
        if module_details['state']['release_approval'] != 'under_review':
            raise ValueError('Cannot review request - module/repo is not under review!')

        if 'decision' not in review:
            raise ValueError('Cannot set review - no "decision" was provided!')
        if not review['decision']:
            raise ValueError('Cannot set review - no "decision" was provided!')
        if review['decision']=='denied':
            if 'review_message' not in review:
                raise ValueError('Cannot set review - if denied, you must set a "review_message"!')
        if 'review_message' not in review:
            review['review_message']=''
        if review['decision'] not in ['approved','denied']:
                raise ValueError('Cannot set review - decision must be "approved" or "denied"')

        # ok, do it.  

        # if the state is approved, then we need to save the beta version over the release version and stash
        # a new entry.  The DBI will handle that for us. (note that concurency issues don't really matter
        # here because if this is done twice (for instance, before the release_state is set to approved in
        # the document in the next call) there won't be any problems.)  I like nested parentheses.
        if review['decision']=='approved':
            success = self.db.push_beta_to_release(module_name=review['module_name'],git_url=review['git_url'])

        # Now we can update the release state state...
        success = self.db.set_module_release_state(
                        module_name=review['module_name'],git_url=review['git_url'],
                        new_state=review['decision'],
                        last_state=module_details['state']['release_approval'],
                        review_message=review['review_message']
                    )
        if not success:
            raise ValueError('Release review update failed - some unknown database error.')


    def get_module_state(self, params):
        params = self.filter_module_or_repo_selection(params)
        return self.db.get_module_state(module_name=params['module_name'],git_url=params['git_url'])


    def get_module_info(self, params):
        params = self.filter_module_or_repo_selection(params)
        details = self.db.get_module_details(module_name=params['module_name'], git_url=params['git_url'])

        owners = []
        for o in details['owners']:
            owners.append(o['kb_username'])

        info = {
            module_name: details['module_name'],
            git_url: details['git_url'],

            description: details['info']['description'],
            language: details['info']['language'],

            owners: owners,

            release: details['current_versions']['release'],
            beta: details['current_versions']['beta'],
            dev: details['current_versions']['dev']
        }
        return info

    def get_version_info(self,params):
        params = self.filter_module_or_repo_selection(params)
        current_versions = self.db.get_module_current_versions(module_name=params['module_name'], git_url=params['git_url'])
        if 'version' in params:
            return current_version[params['version']]
        if 'timestamp' in params:
            if current_version['dev']['timestamp'] == params['timestamp']:
                return current_version['dev']
            if current_version['beta']: 
                if current_version['beta']['timestamp'] == params['timestamp']:
                    return current_version['beta']
            if current_version['release']: 
                if current_version['release']['timestamp'] == params['timestamp']:
                    return current_version['release']

        # TODO: filter the modules old versions based on the info, and get the right one
        #details = self.db.get_module_full_details(module_name=params['module_name'], git_url=params['git_url'])

        return None

    def list_released_versions(self, params):
        params = self.filter_module_or_repo_selection(params)
        details = self.db.get_module_full_details(module_name=params['module_name'], git_url=params['git_url'])
        return details['release_versions']


    def is_registered(self,params):
        if 'git_url' not in params:
            params['git_url'] = ''
        if 'module_name' not in params:
            params['module_name'] = ''
        if self.db.is_registered(module_name=params['module_name'], git_url=params['git_url']) :
            return True
        return False

    def list_basic_module_info(self,params):
        query = { 'state.active':True, 'state.released':True }

        if 'include_disabled' in params:
            if params['include_disabled']>0:
                query.pop('state.active',None)

        if 'include_released' not in params:
            params['include_released'] = 1
        if 'include_unreleased' not in params:
            params['include_unreleased'] = 0

        # figure out release/unreleased options so we can get just the unreleased if needed
        # default (if none of these matches is to list only released)
        if params['include_released']<=0 and params['include_unreleased']<=0:
            return [] # don't include anything...
        elif params['include_released']<=0 and params['include_unreleased']>0:
            query['state.released']=False # include only unreleased
        elif params['include_released']>0 and params['include_unreleased']>0:
            query.pop('state.released',None) # include everything

        return self.db.find_basic_module_info(query)


    def get_build_log(self, timestamp):
        with open(self.temp_dir+'/registration.log.'+str(timestamp)) as log_file:
            log = log_file.read()
        return log

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
def _start_registration(params,timestamp,username,token, db, temp_dir, docker_base_url, nms_url, nms_admin_user, nms_admin_psswd, module_details):
    registrar = Registrar(params, timestamp, username, token, db, temp_dir, docker_base_url,
                            nms_url, nms_admin_user, nms_admin_psswd, module_details)
    registrar.start_registration()

