

import warnings
import threading
import time
import copy
import os
import random
import semantic_version
import re
import uuid

import biokbase.catalog.version

from pprint import pprint
from datetime import datetime
from urlparse import urlparse
from biokbase.catalog.db import MongoCatalogDBI
from biokbase.catalog.registrar import Registrar
from biokbase.narrative_method_store.client import NarrativeMethodStore



class CatalogController:


    def __init__(self, config):

        # first grab the admin list
        self.adminList = []
        if 'admin-users' in config:
            tokens = config['admin-users'].split(',')
            for t in tokens:
                if t.strip():
                    self.adminList.append(t.strip())
        if not self.adminList:  # pragma: no cover
            warnings.warn('no "admin-users" are set in config of CatalogController.')
        
        # make sure the minimal mongo settings are in place
        if 'mongodb-host' not in config: # pragma: no cover
            raise ValueError('"mongodb-host" config variable must be defined to start a CatalogController!')
        if 'mongodb-database' not in config: # pragma: no cover
            raise ValueError('"mongodb-database" config variable must be defined to start a CatalogController!')

        # give warnings if no mongo user information is set
        if 'mongodb-user' not in config: # pragma: no cover
            warnings.warn('"mongodb-user" is not set in config of CatalogController.')
            config['mongodb-user']=''
            config['mongodb-pwd']=''
        if 'mongodb-pwd' not in config: # pragma: no cover
            warnings.warn('"mongodb-pwd" is not set in config of CatalogController.')
            config['mongodb-pwd']=''

        # instantiate the mongo client
        self.db = MongoCatalogDBI(
                    config['mongodb-host'],
                    config['mongodb-database'],
                    config['mongodb-user'],
                    config['mongodb-pwd'])

        # check for the temp directory and make sure it exists
        if 'temp-dir' not in config: # pragma: no cover
            raise ValueError('"temp-dir" config variable must be defined to start a CatalogController!')
        self.temp_dir = config['temp-dir']
        if not os.path.exists(self.temp_dir): # pragma: no cover
            raise ValueError('"temp-dir" does not exist! It is required for registration to work!')
        if not os.path.exists(self.temp_dir): # pragma: no cover
            raise ValueError('"temp-dir" does not exist! Space is required for registration to work!')
        if not os.access(self.temp_dir, os.W_OK): # pragma: no cover
            raise ValueError('"temp-dir" not writable! Writable space is required for registration to work!')

        if 'docker-base-url' not in config: # pragma: no cover
            raise ValueError('"docker-base-url" config variable must be defined to start a CatalogController!')
        self.docker_base_url = config['docker-base-url']
        print('Docker base url config = '+ self.docker_base_url)

        if 'docker-registry-host' not in config: # pragma: no cover
            raise ValueError('"docker-registry-host" config variable must be defined to start a CatalogController!')
        self.docker_registry_host = config['docker-registry-host']
        print('Docker registry host config = '+ self.docker_registry_host)
        
        self.docker_push_allow_insecure = None # none should just set this to default?
        if 'docker-push-allow-insecure' in config:
            print('Docker docker-push-allow-insecure = '+ config['docker-push-allow-insecure'])
            if config['docker-push-allow-insecure'].strip() == "1": # pragma: no cover
                self.docker_push_allow_insecure = True;
                print('WARNING!! - Docker push is set to allow insecure connections.  This should never be on in production.')


        if 'ref-data-base' not in config: # pragma: no cover
            raise ValueError('"ref-data-base" config variable must be defined to start a CatalogController!')
        self.ref_data_base = config['ref-data-base']

        if 'kbase-endpoint' not in config: # pragma: no cover
            raise ValueError('"kbase-endpoint" config variable must be defined to start a CatalogController!')
        self.kbase_endpoint = config['kbase-endpoint']
        
        if 'nms-url' not in config: # pragma: no cover
            raise ValueError('"nms-url" config variable must be defined to start a CatalogController!')
        self.nms_url = config['nms-url']
        if 'nms-admin-user' not in config: # pragma: no cover
            raise ValueError('"nms-admin-user" config variable must be defined to start a CatalogController!')
        self.nms_admin_user = config['nms-admin-user']
        if 'nms-admin-psswd' not in config: # pragma: no cover
            raise ValueError('"nms-admin-psswd" config variable must be defined to start a CatalogController!')
        self.nms_admin_psswd = config['nms-admin-psswd']

        self.nms = NarrativeMethodStore(self.nms_url,user_id=self.nms_admin_user,password=self.nms_admin_psswd)


    def register_repo(self, params, username, token):

        if 'git_url' not in params:
            raise ValueError('git_url not defined, but is required for registering a repository')
        git_url = params['git_url']
        if not bool(urlparse(git_url).netloc):
            raise ValueError('The git url provided is not a valid URL.')

        # TODO: normalize github urls


        # generate a unique registration ID based on a timestamp in ms + a UUID
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()*1000)
        registration_id = str(timestamp)+'_'+str(uuid.uuid4())

        # reserve some scratch space on the server for this registration
        try:
            os.mkdir(os.path.join(self.temp_dir,registration_id))
        except:
            raise ValueError('Unable to allocate a directory for building.  Try again, and if the problem persists contact us.')
        if not os.path.isdir(os.path.join(self.temp_dir,registration_id)):
            raise ValueError('Unable to allocate a directory for building.  Try again, and if the problem persists contact us.')

        # 0) Make sure the submitter is on the list
        if not self.is_approved_developer([username])[0]:
            raise ValueError('You are not an approved developer.  Contact us to request approval.')

        prev_dev_version = None

        # 1) If the repo does not yet exist, then create it.  No additional permission checks needed
        if not self.db.is_registered(git_url=git_url) : 
            self.db.register_new_module(git_url, username, timestamp, 'waiting to start', registration_id)
            module_details = self.db.get_module_full_details(git_url=git_url)
        
        # 2) If it has already been registered, make sure the user has permissions to update, and
        # that the module is in a state where it can be registered 
        else:
            module_details = self.db.get_module_full_details(git_url=git_url)

            # 2a) Make sure the user has permission to register this URL
            if self.has_permission(username,module_details['owners']):
                # 2b) Make sure the current registration state is either 'complete' or 'error', and the module is active
                state = module_details['state']
                active_state = state['active']
                if not active_state:
                    raise ValueError('You cannot register new versions of this module.  It is inactive.')

                registration_state = state['registration']
                if registration_state == 'complete' or registration_state == 'error':
                    error = self.db.set_module_registration_state(git_url=git_url, new_state='started', last_state=registration_state)
                    if error is not None:
                        # we can fail if the registration state changed when we were first checking to now.  This is important
                        # to ensure we only ever kick off one registration thread at a time
                        raise ValueError('Registration failed for git repo ('+git_url+') - registration state was modified before build could begin: '+error)
                    # we know we are the only operation working, so we can clear the dev version and upate the timestamp
                    #self.db.update_dev_version({'timestamp':timestamp, 'registration_id':registration_id}, git_url=git_url)
                else:
                    raise ValueError('Registration already in progress for this git repo ('+git_url+')')
            else :
                raise ValueError('You ('+username+') are an approved developer, but do not have permission to register this repo ('+git_url+')')

        # 3) Allocate a build log
        self.db.create_new_build_log(registration_id, timestamp, 'waiting to start', git_url)

        # 3) Ok, kick off the registration thread
        #   - This will check out the repo, attempt to build the image, run some tests, store the image
        #   - If all went well, and during the process, it will update the registration state of the
        #     module and finally update the dev version
        #   - If things failed, it will set the error state, and set an error message.

        # first set the dev current_release timestamp

        t = threading.Thread(target=_start_registration, args=(params,registration_id,timestamp,username,token,self.db, self.temp_dir, self.docker_base_url, 
            self.docker_registry_host, self.docker_push_allow_insecure, self.nms_url, self.nms_admin_user, self.nms_admin_psswd, module_details, self.ref_data_base, self.kbase_endpoint,
            prev_dev_version))
        t.start()

        # 4) provide the registration_id 
        return registration_id



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
            if not params['error_message']:
                raise ValueError('Update failed - if state is "error", you must also set an "error_message".')
            error_message = params['error_message']
        
        # then we update the state
        error = self.db.set_module_registration_state(
                    git_url=params['git_url'],
                    module_name=params['module_name'],
                    new_state=params['registration_state'],
                    error_message=error_message)
        if error is not None:
            raise ValueError('Registration failed for git repo ('+git_url+')- some unknown database error: ' + error)


    def push_dev_to_beta(self, params, username):
        # first make sure everything exists and we have permissions
        params = self.filter_module_or_repo_selection(params)
        module_details = self.db.get_module_details(module_name=params['module_name'],git_url=params['git_url'])
        # Make sure the submitter is still an approved developer
        if not self.is_approved_developer([username])[0]:
            raise ValueError('You are not an approved developer.  Contact us to request approval.')

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
        self.nms.push_repo_to_tag({'module_name':module_details['module_name'], 'tag':'beta'})
        error = self.db.push_dev_to_beta(module_name=params['module_name'],git_url=params['git_url'])
        if error is not None:
            raise ValueError('Update operation failed - some unknown database error: '+error)

    def request_release(self, params, username):
        # first make sure everything exists and we have permissions
        params = self.filter_module_or_repo_selection(params)
        module_details = self.db.get_module_details(module_name=params['module_name'],git_url=params['git_url'])
        # Make sure the submitter is still an approved developer
        if not self.is_approved_developer([username])[0]:
            raise ValueError('You are not an approved developer.  Contact us to request approval.')
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
            if module_details['current_versions']['beta']['version'] == module_details['current_versions']['release']['version']:
                raise ValueError('Cannot request release - beta version has same version number to released version.')
            # check that the version number actually increased (assume at this point we already confirmed semantic version was correct)
            beta_sv = semantic_version.Version(module_details['current_versions']['beta']['version'])
            release_sv = semantic_version.Version(module_details['current_versions']['release']['version'])
            if beta_sv <= release_sv:
                raise ValueError('Cannot request release - beta semantic version ('+str(beta_sv)+') must be greater '
                    +'than the released semantic version '+str(release_sv)+', as determined by http://semver.org')
            # TODO: may want to make sure that only v1.0.0+ are released
            #if beta_sv < semantic_version.Version('1.0.0'):
            #    raise ValueError('Cannot request release - beta semantic version must be greater than 1.0.0')


        # ok, do it.
        error = self.db.set_module_release_state(
                        module_name=params['module_name'],git_url=params['git_url'],
                        new_state='under_review',
                        last_state=module_details['state']['release_approval']
                    )
        if error is not None:
            raise ValueError('Release request failed - some unknown database error.'+error)

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

        if 'decision' not in review:
            raise ValueError('Cannot set review - no "decision" was provided!')
        if not review['decision']:
            raise ValueError('Cannot set review - no "decision" was provided!')
        if review['decision']=='denied':
            if 'review_message' not in review:
                raise ValueError('Cannot set review - if denied, you must set a "review_message"!')
            if not review['review_message'].strip():
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
            release_timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()*1000)
            self.nms.push_repo_to_tag({'module_name':module_details['module_name'], 'tag':'release'})
            error = self.db.push_beta_to_release(
                        module_name=review['module_name'],
                        git_url=review['git_url'],
                        release_timestamp=release_timestamp)

        # Now we can update the release state state...
        error = self.db.set_module_release_state(
                        module_name=review['module_name'],git_url=review['git_url'],
                        new_state=review['decision'],
                        last_state=module_details['state']['release_approval'],
                        review_message=review['review_message']
                    )
        if error is not None:
            raise ValueError('Release review update failed - some unknown database error. ' + error)


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
            'module_name': details['module_name'],
            'git_url': details['git_url'],

            'description': details['info']['description'],
            'language': details['info']['language'],

            'owners': owners,

            'release': details['current_versions']['release'],
            'beta': details['current_versions']['beta'],
            'dev': details['current_versions']['dev']
        }
        return info

    def get_version_info(self,params):
        params = self.filter_module_or_repo_selection(params)
        current_version = self.db.get_module_current_versions(module_name=params['module_name'], git_url=params['git_url'])

        if not current_version:
            return None

        # TODO: can make this more effecient and flexible by putting in some indicies and doing the query on mongo side
        # right now, we require a module name / git url, and request specific version based on selectors.  in the future
        # we could, for instance, get all versions that match a particular git commit hash, or timestamp...

        # If version is in params, it should be one of dev, beta, release
        if 'version' in params:
            if params['version'] not in ['dev','beta','release']:
                raise ValueError('invalid version selection, valid versions are: "dev" | "beta" | "release"')
            v = current_version[params['version']]
            # if timestamp or git_commit_hash is given, those need to match as well
            if 'timestamp' in params:
                if v['timestamp'] != params['timestamp'] :
                    return None;
            if 'git_commit_hash' in params:
                if v['git_commit_hash'] != params['git_commit_hash'] :
                    return None;
            return v

        if 'timestamp' in params:
            # first check in current versions
            for version in ['dev','beta','release']:
                if current_version[version]['timestamp'] == params['timestamp']:
                    v = current_version[version]
                    if 'git_commit_hash' in params:
                        if v['git_commit_hash'] != params['git_commit_hash'] :
                            return None;
                    return v
            # if we get here, we have to look in full history
            details = self.db.get_module_full_details(module_name=params['module_name'], git_url=params['git_url'])
            all_versions = details['release_version_list']
            for v in all_versions:
                if v['timestamp'] == params['timestamp']:
                    if 'git_commit_hash' in params:
                        if v['git_commit_hash'] != params['git_commit_hash'] :
                            return None;
                    return v
            return None

        # if we get here, version and timestamp are not defined, so just look for the commit hash
        if 'git_commit_hash' in params:
            # check current versions
            for version in ['dev','beta','release']:
                if 'git_commit_hash' in current_version[version] and current_version[version]['git_commit_hash'] == params['git_commit_hash']:
                    v = current_version[version]
                    return v
            # if we get here, we have to look in full history
            details = self.db.get_module_full_details(module_name=params['module_name'], git_url=params['git_url'])
            all_versions = details['release_version_list']
            for v in all_versions:
                if v['git_commit_hash'] == params['git_commit_hash']:
                    return v
            return None

        # didn't get nothing, so return
        return None


    def get_module_version(self, params):

        # Make sure the git_url and/or module_name are set
        if 'git_url' not in params and 'module_name' not in params:
            raise ValueError('Missing required fields git_url or module_name')
        if 'git_url' not in params:
            params['git_url'] = ''
        if 'module_name' not in params:
            params['module_name'] = ''

        # get the module details so we can look up releases and tags
        module_details = self.db.get_module_full_details(module_name=params['module_name'], git_url=params['git_url'], substitute_versions=False)
        if module_details is None:
            raise ValueError('Module cannot be found based on module_name or git_url parameters.')

        if 'module_name_lc' not in module_details:
            raise ValueError('Module was never properly registered, and has no available versions.')
        module_name_lc = module_details['module_name_lc']

        # figure out what info we actually need to fetch
        excluded_fields = []
        if not ('include_module_description' in params and str(params['include_module_description']).strip()=='1'):
            excluded_fields.append('module_description')
        if not ('include_compilation_report' in params and str(params['include_compilation_report']).strip()=='1'):
            excluded_fields.append('compilation_report')


        # no version string specified, so default to returning release, beta, or dev in that order
        if 'version' not in params or params['version'] is None or params['version'].strip() is '':
            for tag in ['release','beta','dev']:
                if tag in module_details['current_versions'] and module_details['current_versions'][tag] is not None:
                    # get the version info
                    versions = self.db.lookup_module_versions(
                                            module_name_lc,
                                            git_commit_hash = module_details['current_versions'][tag]['git_commit_hash'],
                                            excluded_fields = excluded_fields)
                    if len(versions) != 1:
                        raise ValueError('Catalog DB Error: could not identify proper version - version documents found: ' + str(len(versions)))
                    v = versions[0]
                    self.prepare_version_for_return(v, module_details)
                    return v
            return None

        # return the specific tag specified
        if params['version'] in ['release','beta','dev']:
            tag = params['version']
            if tag in module_details['current_versions'] and module_details['current_versions'][tag] is not None:
                # get the version info
                versions = self.db.lookup_module_versions(
                                        module_name_lc,
                                        git_commit_hash = module_details['current_versions'][tag]['git_commit_hash'],
                                        excluded_fields = excluded_fields)
                if len(versions) != 1:
                    raise ValueError('Catalog DB Error: could not identify proper version - N version documents found: ' + str(len(versions)))
                v = versions[0]
                self.prepare_version_for_return(v, module_details)
                return v
            return None


        # because this is the most common option, just assume it is a git commit hash and try to fetch before we deal with semantic version logic
        versions = self.db.lookup_module_versions(
                                module_name_lc,
                                git_commit_hash = params['version'],
                                excluded_fields = excluded_fields)
        if len(versions)==1:
            v = versions[0]
            self.prepare_version_for_return(v, module_details)
            return v
        elif len(versions)>1:
            raise ValueError('Catalog DB Error: could not identify proper version - N version documents found: ' + str(len(versions)))


        # ok, didn't work.  let's try it as a semantic version, which only works on released modules.  First let's try to parse
        spec = None
        exact_version = None
        try:
            exact_version = semantic_version.Version(params['version'].strip())
        except:
            # wasn't a semantic version, but could still be a semantic version spec
            try:
                spec = semantic_version.Spec(params['version'].strip())
            except:
                # couldn't figure out what to do, so just return that we can't find anything
                return None

        # get the released version list with semantic versions
        released_version_list = self.db.lookup_module_versions(
                                    module_name_lc,
                                    released = 1,
                                    included_fields = ['version', 'git_commit_hash'])

        # we are looking for an exact semantic version match
        if exact_version:
            for r in released_version_list:
                if exact_version == semantic_version.Version(r['version']):
                    versions = self.db.lookup_module_versions(
                                module_name_lc,
                                git_commit_hash = r['git_commit_hash'],
                                excluded_fields = excluded_fields)
                    if len(versions)==1:
                        v = versions[0]
                        self.prepare_version_for_return(v, module_details)
                        return v
                    else:
                        raise ValueError('Catalog DB Error: could not identify proper version - N version documents found: ' + str(len(versions)))

        if spec:
            svers = []
            for r in released_version_list:
                svers.append(semantic_version.Version(r['version']))
            theRightVersion = spec.select(svers)
            if theRightVersion:
                for r in released_version_list:
                    if theRightVersion == semantic_version.Version(r['version']):
                        versions = self.db.lookup_module_versions(
                                module_name_lc,
                                git_commit_hash = r['git_commit_hash'],
                                excluded_fields = excluded_fields)
                        if len(versions)==1:
                            v = versions[0]
                            self.prepare_version_for_return(v, module_details)
                            return v
                        else:
                            raise ValueError('Catalog DB Error: could not identify proper version - N version documents found: ' + str(len(versions)))

        return None


    def prepare_version_for_return(self, version, module_details):

        # remove module_name_lc if it exists (should always be there, but if it was already removed don't worry)
        try:
            del(version['module_name_lc'])
        except:
            pass

        # add git_url
        version['git_url'] = module_details['git_url']
        version['module_name'] = module_details['module_name']

        # add release tag information
        release_tags = []
        for tag in ['release','beta','dev']:
            if tag in module_details['current_versions'] and module_details['current_versions'][tag] is not None:
                if 'git_commit_hash' in module_details['current_versions'][tag]:
                    if module_details['current_versions'][tag]['git_commit_hash'] == version['git_commit_hash']:
                        release_tags.append(tag)
        version['release_tags'] = release_tags

        if 'release_timestamp' not in version:
            if version['released']==1:
                version['release_timestamp'] = version['timestamp']
            else:
                version['release_timestamp'] = None



    def list_released_versions(self, params):
        params = self.filter_module_or_repo_selection(params)
        details = self.db.get_module_full_details(module_name=params['module_name'], git_url=params['git_url'])
        return sorted(details['release_version_list'], key= lambda v: v['timestamp'])


    def is_registered(self,params):
        if 'git_url' not in params:
            params['git_url'] = ''
        if 'module_name' not in params:
            params['module_name'] = ''
        if self.db.is_registered(module_name=params['module_name'], git_url=params['git_url']) :
            return True
        return False

    # note: maybe a little too mongo centric, but ok for now...
    def list_basic_module_info(self,params):
        query = { 'state.active':True, 'state.released':True }

        if 'include_disabled' in params:
            if params['include_disabled']>0:
                query.pop('state.active',None)

        if 'include_released' not in params:
            params['include_released'] = 1
        if 'include_unreleased' not in params:
            params['include_unreleased'] = 0

        if 'include_modules_with_no_name_set' not in params:
            query['module_name_lc'] = { '$exists':True }
        elif params['include_modules_with_no_name_set'] != 1:
            query['module_name_lc'] = { '$exists':True }

        # figure out release/unreleased options so we can get just the unreleased if needed
        # default (if none of these matches is to list only released)
        if params['include_released']<=0 and params['include_unreleased']<=0:
            return [] # don't include anything...
        elif params['include_released']<=0 and params['include_unreleased']>0:
            # minor change that could be removed eventually: check for released=False or missing
            query.pop('state.released',None)
            query['$or']=[{'state.released':False},{'state.released':{'$exists':False}}]
            #query['state.released']=False # include only unreleased (only works if everything has this flag)
        elif params['include_released']>0 and params['include_unreleased']>0:
            query.pop('state.released',None) # include everything

        if 'owners' in params:
            if params['owners']: # might want to filter out empty strings in the future
                query['owners.kb_username']={'$in':params['owners']}

        return self.db.find_basic_module_info(query)




#    typedef structure {
#        string release_tag;
#        list<string> module_name;
#    } ListLocalFunctionParams;

#    funcdef list_local_functions(ListLocalFunctionParams params) returns (list<LocalFunctionInfo> info_list);



#    typedef structure {
#        string module_name;
#        string function_id;
#        string release_tag;
#        string git_commit_hash;
#    } SelectOneLocalFunction;

#    typedef structure {
#        list<SelectOneLocalFunction> functions;
#    } GetLocalFunctionDetails;



    def list_local_functions(self, params):

        module_names = []
        if 'module_names' in params:
            if isinstance(params['module_names'], list):
                for m in params['module_names']:
                    if not isinstance(m,basestring):
                        raise ValueError('module_names parameter field must be a list of module names (list of strings)')
                module_names = params['module_names']
            else:
                raise ValueError('Module Names must be a list of module names')

        if len(module_names)>0:
            release_tag = None
        else:
            release_tag = 'release'
        if 'release_tag' in params:
            if not isinstance(params['release_tag'],basestring):
                raise ValueError('release_tag parameter field must be a string (release | beta | dev)')
            if not params['release_tag'] in ['dev','beta','release']:
                raise ValueError('release_tag parameter field must be either: "release" | "beta" | "dev"')

            release_tag = params['release_tag']

        return self.db.list_local_function_info(module_names=module_names, release_tag=release_tag)

    def get_local_function_details(self, params):

        #info_list = self.cc.list_local_functions(params)

        if 'functions' not in params:
            raise ValueError('Missing required parameter field "functions"')

        if not isinstance(params['functions'],list):
            raise ValueError('Parameter field "functions" must be a list')

        if len(params['functions']) == 0:
            return []

        for f in params['functions']:
            if not isinstance(f,dict):
                raise ValueError('Values of the "functions" list must be objects')
            # must have module_name and function_id
            if 'module_name' not in f:
                raise ValueError('All functions specified must specify a "module_name"')
            if not isinstance(f['module_name'],basestring):
                raise ValueError('"module_name" in function specification must be a string')
            if 'function_id' not in f:
                raise ValueError('All functions specified must specify a "function_id"')
            if not isinstance(f['function_id'],basestring):
                raise ValueError('"function_id" in function specification must be a string')
            # optionally, release tag or git_commit_hash must be strings
            if 'release_tag' in f:
                if not isinstance(f['release_tag'],basestring):
                    raise ValueError('"release_tag" in function specification must be a string')
                if f['release_tag'] not in ['dev','beta','release']:
                    raise ValueError('"release_tag" must be one of dev | beta | release')
            if 'git_commit_hash' in f:
                if not isinstance(f['git_commit_hash'],basestring):
                    raise ValueError('"git_commit_hash" in function specification must be a string')

        return self.db.get_local_function_spec(params['functions'])


    def set_module_active_state(self, active, params, username):
        params = self.filter_module_or_repo_selection(params)
        if not self.is_admin(username):
            raise ValueError('Only Admin users can set a module to be active/inactive.')
        module_details = self.db.get_module_details(module_name=params['module_name'], git_url=params['git_url'])
        error = self.db.set_module_active_state(active, module_name=params['module_name'], git_url=params['git_url'])
        if error is not None:
            raise ValueError('Update operation failed - some unknown database error: '+error)

        # if set to inactive, disable the repo in NMS
        if(not active):
            self.nms.disable_repo({'module_name':module_details['module_name']})
        # if set to active, enable the repo
        else:
            self.nms.enable_repo({'module_name':module_details['module_name']})


    def approve_developer(self, developer, username):
        if not developer:
            raise ValueError('No username provided')
        if not developer.strip():
            raise ValueError('No username provided')
        if not self.is_admin(username):
            raise ValueError('Only Admin users can approve or revoke developers.')
        self.db.approve_developer(developer)

    def revoke_developer(self, developer, username):
        if not developer:
            raise ValueError('No username provided')
        if not developer.strip():
            raise ValueError('No username provided')
        if not self.is_admin(username):
            raise ValueError('Only Admin users can approve or revoke developers.')
        self.db.revoke_developer(developer)

    def is_approved_developer(self, usernames):
        if not usernames: return []
        return self.db.is_approved_developer(usernames)

    def list_approved_developers(self):
        dev_list = self.db.list_approved_developers()
        simple_kbase_dev_list = []
        for d in dev_list:
            simple_kbase_dev_list.append(d['kb_username'])
        return sorted(simple_kbase_dev_list)

    # get the build log from file that it is being written to
    def get_build_log(self, registration_id):
        try:
            with open(self.temp_dir+'/registration.log.'+str(registration_id)) as log_file:
                log = log_file.read()
        except:
            log = '[log not found - registration_id is invalid or the log has been deleted]'
        return log

    # get the parsed build log from mongo
    def get_parsed_build_log(self, params):
        if 'registration_id' not in params:
            raise ValueError('You must specify a registration_id to retrieve a build log')

        slice_arg = None
        if 'skip' in params:
            if 'limit' not in params:
                raise ValueError('Cannot specify the skip argument without a limit- blame Mongo')    
            slice_arg = [int(params['skip']),int(params['limit'])]

        if 'first_n' in params:
            if slice_arg is not None:
                raise ValueError('Cannot combine skip/limit with first_n parameters')
            slice_arg = int(params['first_n'])

        if 'last_n' in params:
            if slice_arg is not None:
                raise ValueError('Cannot combine skip/limit/first_n with last_n parameters')
            slice_arg = -int(params['last_n'])

        return self.db.get_parsed_build_log(params['registration_id'], slice_arg = slice_arg)

    def list_builds(self, params):

        only_running = False
        only_error = False
        only_complete = False

        if 'only_running' in params:
            if params['only_running']:
                only_running = True
                #registration_match = { '$or': [{'$ne':'complete'}, {'$ne':'error'}] }
        if 'only_error' in params:
            if params['only_error']:
                if only_running:
                    raise ValueError('Cannot combine only_error=1 with only_running=1 parameters')
                only_error = True
                #registration_match = 'error'
        if 'only_complete' in params:
            if params['only_complete']:
                if only_running or only_error:
                    raise ValueError('Cannot combine only_complete=1 with only_running=1 or only_error=1 parameters')
                only_complete = True
        
        skip = 0
        if 'skip' in params:
            skip = int(params['skip'])
        limit = 1000
        if 'limit' in params:
            limit = int(params['limit'])

        git_url_match_list = []
        module_name_lc_match_list = []

        if 'modules' in params:
            for mod in params['modules']:
                if 'git_url' in mod:
                    git_url_match_list.append(mod['git_url'])
                if 'module_name' in mod:
                    module_name_lc_match_list.append(str(mod['module_name']).lower())

        return self.db.list_builds(
                skip = skip,
                limit = limit,
                module_name_lcs = module_name_lc_match_list,
                git_urls = git_url_match_list,
                only_running = only_running,
                only_error = only_error,
                only_complete = only_complete
            )


    def delete_module(self,params,username):
        if not self.is_admin(username):
            raise ValueError('Only Admin users can delete modules.')
        if 'module_name' not in params and 'git_url' not in params:
            raise ValueError('You must specify the "module_name" or "git_url" of the module to delete.')
        params = self.filter_module_or_repo_selection(params)
        module_details = self.db.get_module_details(module_name=params['module_name'], git_url=params['git_url'])
        error = self.db.delete_module(module_name=params['module_name'], git_url=params['git_url'])
        if error is not None:
            raise ValueError('Delete operation failed - some unknown database error: '+error)
        self.nms.disable_repo({'module_name':module_details['module_name']})


    def migrate_module_to_new_git_url(self, params, username):
        if not self.is_admin(username):
            raise ValueError('Only Admin users can migrate module git urls.')
        if 'module_name' not in params:
            raise ValueError('You must specify the "module_name" of the module to modify.')
        if 'current_git_url' not in params:
            raise ValueError('You must specify the "current_git_url" of the module to modify.')
        if 'new_git_url' not in params:
            raise ValueError('You must specify the "new_git_url" of the module to modify.')
        if not bool(urlparse(params['new_git_url']).netloc):
            raise ValueError('The new git url is not a valid URL.')
        error = self.db.migrate_module_to_new_git_url(params['module_name'],params['current_git_url'],params['new_git_url'])
        if error is not None:
            raise ValueError('Update operation failed - some unknown database error: '+error)



    def add_favorite(self, params, username):
        timestamp = int((datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()*1000)

        if 'module_name' not in params:
            module_name = 'nms.legacy'
        elif not params['module_name']:
            module_name = 'nms.legacy'
        else:
            module_name = params['module_name']

        if 'id' not in params:
            raise ValueError('Cannot add favorite- id not set')
        if not params['id']:
            raise ValueError('Cannot add favorite- id not set')
        app_id = params['id']

        if not username:
            raise ValueError('Cannot add favorite- username not set')

        error = self.db.add_favorite(module_name, app_id, username, timestamp)
        if error is not None:
            raise ValueError('Add favorite operation failed - some unknown database error: '+error)

    def remove_favorite(self, params, username):
        if 'module_name' not in params:
            module_name = 'nms.legacy'
        elif not params['module_name']:
            module_name = 'nms.legacy'
        else:
            module_name = params['module_name']

        if 'id' not in params:
            raise ValueError('Cannot remove favorite- id not set')
        if not params['id']:
            raise ValueError('Cannot remove favorite- id not set')
        app_id = params['id']

        if not username:
            raise ValueError('Cannot remove favorite- username not set')

        error = self.db.remove_favorite(module_name, app_id, username)
        if error is not None:
            raise ValueError('Remove favorite operation failed - some unknown database error: '+error)

    def list_user_favorites(self, username):
        return self.db.list_user_favorites(username)

    def list_app_favorites(self, item):
        if 'module_name' not in item:
            module_name = 'nms.legacy'
        elif not item['module_name']:
            module_name = 'nms.legacy'
        else:
            module_name = item['module_name']

        if 'id' not in item:
            raise ValueError('Cannot list app favorites- id not set')
        if not item['id']:
            raise ValueError('Cannot list app favorites- id not set')
        app_id = item['id']

        return self.db.list_app_favorites(module_name, app_id)

    def aggregate_favorites_over_apps(self, params):
        # no params right now, this just returns everything
        module_names_lc = []
        if 'modules' in params:
            for i in params['modules']:
                module_names_lc.append(i.lower())

        return self.db.aggregate_favorites_over_apps(module_names_lc)




    def list_service_modules(self, filter):
        # if we have the tag flag, then return the specific tagged version
        if 'tag' in filter:
            if filter['tag'] not in ['dev', 'beta', 'release']:
                raise ValueError('tag parameter must be either "dev", "beta", or "release".')
            return self.db.list_service_module_versions_with_tag(filter['tag'])

        # otherwise we need to go through everything that has been released
        mods = self.db.list_all_released_service_module_versions()
        return mods



    def module_version_lookup(self, selection):

        # todo: speed up queries by doing more work in Mongo??

        selection = self.filter_module_or_repo_selection(selection)

        only_services = True
        if 'only_service_versions' in selection:
            only_services = selection['only_service_versions'] > 0

        lookup = '>=0.0.0'
        if 'lookup' in selection:
            lookup = selection['lookup']
            # if the lookup was a tag, return the exact tag
            if selection['lookup'] in ['dev','beta','release']:
                details = self.db.get_module_details(module_name=selection['module_name'],git_url=selection['git_url'])
                version = details['current_versions'][selection['lookup']]

                if only_services:
                    if 'dynamic_service' in version:
                        if not version['dynamic_service']:
                            raise ValueError('The "'+selection['lookup']+'" version is not marked as a Service Module.')
                return {
                    'module_name': details['module_name'],
                    'version':version['version'],
                    'git_commit_hash':version['git_commit_hash'],
                    'docker_img_name':version['docker_img_name']
                }


        # assume semantic versioning which only can select released versions
        # we should optimize to fetch only the details/versions we need from mongo.
        details = self.db.get_module_full_details(module_name=selection['module_name'])
        versions = details['release_version_list']

        try:
            spec = semantic_version.Spec(lookup)
            svers = []
            for v in versions:
                if only_services:
                    if 'dynamic_service' not in v: continue
                    if not v['dynamic_service']: continue
                svers.append(semantic_version.Version(v['version']))

            theRightVersion = spec.select(svers)
            if theRightVersion:
                for v in versions:
                    if v['version'] == str(theRightVersion):
                        return {
                            'module_name': details['module_name'],
                            'version':v['version'],
                            'git_commit_hash':v['git_commit_hash'],
                            'docker_img_name':v['docker_img_name']
                        }

                raise ValueError('No suitable version matches your lookup - but this seems wrong.')
            else:
                raise ValueError('No suitable version matches your lookup.')
        except ValueError:
            # probably we could not parse as a semantic version, so check as a commit hash
            for v in versions:
                if v['git_commit_hash'] == lookup:
                    if only_services:
                        if 'dynamic_service' not in v:
                            raise ValueError('The "'+selection['lookup']+'" version is not marked as a Service Module.')
                        if not v['dynamic_service']:
                            raise ValueError('The "'+selection['lookup']+'" version is not marked as a Service Module.')
                    return {
                        'module_name': details['module_name'],
                        'version':v['version'],
                        'git_commit_hash':v['git_commit_hash'],
                        'docker_img_name':v['docker_img_name']
                    }
            # still didn't find it, so it may be the hash of the dev/beta version
            details = self.db.get_module_details(module_name=selection['module_name'],git_url=selection['git_url'])
            cv = details['current_versions']
            if cv['dev']['git_commit_hash'] == lookup:
                if 'dynamic_service' in cv['dev']:
                    if not cv['dev']['dynamic_service']:
                        raise ValueError('The "'+selection['lookup']+'" version is not marked as a Service Module.')
                return {
                    'module_name': details['module_name'],
                    'version':cv['dev']['version'],
                    'git_commit_hash':cv['dev']['git_commit_hash'],
                    'docker_img_name':cv['dev']['docker_img_name']
                }
            if cv['beta']['git_commit_hash'] == lookup:
                if 'dynamic_service' in cv['beta']:
                    if not cv['beta']['dynamic_service']:
                        raise ValueError('The "'+selection['lookup']+'" version is not marked as a Service Module.')
                return {
                    'module_name': details['module_name'],
                    'version':cv['beta']['version'],
                    'git_commit_hash':cv['beta']['git_commit_hash'],
                    'docker_img_name':cv['beta']['docker_img_name']
                }

        # if we got here and didn't find anything, throw an error.
        raise ValueError('No suitable version matches your lookup.')
        return None





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


    def log_exec_stats(self, admin_user_id, user_id, app_module_name, app_id, func_module_name,
                       func_name, git_commit_hash, creation_time, exec_start_time, finish_time,
                       is_error):
        if not self.is_admin(admin_user_id):
            raise ValueError('You do not have permission to log execution statistics.')
        self.db.add_exec_stats_raw(user_id, app_module_name, app_id, func_module_name, func_name, 
                                   git_commit_hash, creation_time, exec_start_time, finish_time, 
                                   is_error)
        parts = datetime.fromtimestamp(creation_time).isocalendar()
        week_time_range = str(parts[0]) + "-W" + str(parts[1])
        self.db.add_exec_stats_apps(app_module_name, app_id, creation_time, exec_start_time, 
                                    finish_time, is_error, "a", "*")
        self.db.add_exec_stats_apps(app_module_name, app_id, creation_time, exec_start_time, 
                                    finish_time, is_error, "w", week_time_range)
        self.db.add_exec_stats_users(user_id, creation_time, exec_start_time, 
                                    finish_time, is_error, "a", "*")
        self.db.add_exec_stats_users(user_id, creation_time, exec_start_time, 
                                    finish_time, is_error, "w", week_time_range)


    def get_exec_aggr_stats(self, full_app_ids, per_week):
        type = "w" if per_week else "a"
        time_range = None if per_week else "*"
        return self.db.get_exec_stats_apps(full_app_ids, type, time_range)


    def get_exec_aggr_table(self, requesting_user, params):
        if not self.is_admin(requesting_user):
            raise ValueError('You do not have permission to view this data.')

        minTime = None
        maxTime = None
        if 'begin' in params:
            minTime = params['begin']
        if 'end' in params:
            maxTime = params['end']

        return self.db.aggr_exec_stats_table(minTime, maxTime)


    def get_exec_raw_stats(self, requesting_user, params):
        if not self.is_admin(requesting_user):
            raise ValueError('You do not have permission to view this data.')

        minTime = None
        maxTime = None
        if 'begin' in params:
            minTime = params['begin']
        if 'end' in params:
            maxTime = params['end']

        return self.db.get_exec_raw_stats(minTime, maxTime)




    def set_client_group(self, username, params):

        if not self.is_admin(username):
            raise ValueError('You do not have permission to set execution client groups.')

        if not 'app_id' in params:
            raise ValueError('You must set the "app_id" parameter to [module_name]/[app_id]')

        client_groups = []
        if 'client_groups' in params:
            if not isinstance(params['client_groups'], list):
                raise ValueError('client_groups parameter must be a list')
            for c in params['client_groups']:
                #if not isinstance(c, str):
                #    raise ValueError('client_groups parameter must be a list of strings')
                # other client group checks should go here if needed
                client_groups.append(c)

        error = self.db.set_client_group(params['app_id'], client_groups)
        if error is not None:
            raise ValueError('Update probably failed, blame mongo: update operation returned: '+error)

    def get_client_groups(self, params):
        app_ids = None
        if 'app_ids' in params:
            if not isinstance(params['app_ids'], list):
                raise ValueError('app_ids parameter must be a list');
            app_ids = [];
            for a in params['app_ids']:
                tokens = a.strip().split('/')
                if len(tokens)==2:
                    a = tokens[0].lower() + '/' + tokens[1]
                app_ids.append(a)
            if len(app_ids) == 0 :
                app_ids = None
        return self.db.list_client_groups(app_ids)




# NOT PART OF CLASS CATALOG!!
def _start_registration(params,registration_id, timestamp,username,token, db, temp_dir, docker_base_url, docker_registry_host,
                        docker_push_allow_insecure,
                        nms_url, nms_admin_user, nms_admin_psswd, module_details, ref_data_base, kbase_endpoint, prev_dev_version):
    registrar = Registrar(params, registration_id, timestamp, username, token, db, temp_dir, docker_base_url, docker_registry_host,
                            docker_push_allow_insecure, 
                            nms_url, nms_admin_user, nms_admin_psswd, module_details, ref_data_base, kbase_endpoint, prev_dev_version)
    registrar.start_registration()

