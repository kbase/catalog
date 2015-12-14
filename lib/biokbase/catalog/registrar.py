import re
import sys
import os
import traceback
import shutil
import time
import datetime
import pprint
import json

import git
import yaml
import requests
from urlparse import urlparse
from docker import Client as DockerClient

from biokbase.catalog.db import MongoCatalogDBI
from biokbase.narrative_method_store.client import NarrativeMethodStore

    
class Registrar:

    # params is passed in from the controller, should be the same as passed into the spec
    # db is a reference to the Catalog DB interface (usually a MongoCatalogDBI instance)
    def __init__(self, params, registration_id, timestamp, username, token, db, temp_dir, docker_base_url, 
                    docker_registry_host, nms_url, nms_admin_user, nms_admin_psswd, module_details):
        self.db = db
        self.params = params
        # at this point, we assume git_url has been checked
        self.git_url = params['git_url']

        self.registration_id = registration_id
        self.timestamp = timestamp
        self.username = username
        self.token = token
        self.db = db
        self.temp_dir = temp_dir
        self.docker_base_url = docker_base_url
        self.docker_registry_host = docker_registry_host

        self.nms_url = nms_url
        self.nms_admin_user = nms_admin_user
        self.nms_admin_psswd = nms_admin_psswd

        self.nms = NarrativeMethodStore(self.nms_url,user_id=self.nms_admin_user,password=self.nms_admin_psswd)

        # (most) of the mongo document for this module snapshot before this registration
        self.module_details = module_details

        self.log_buffer = [];
        self.last_log_time = time.time() # in seconds
        self.log_interval = 1.0 # save log to mongo every second


    def start_registration(self):
        try:
            self.logfile = open(self.temp_dir+'/registration.log.'+self.registration_id, 'w')
            self.log('Registration started on '+ str(datetime.datetime.now()) + ' by '+self.username)
            self.log('Registration ID: '+str(self.registration_id));
            self.log('Registration Parameters: '+str(self.params));

            ##############################
            # 1 - clone the repo into the temp directory that should already be reserved for us
            self.set_build_step('cloning git repo')
            if not os.path.isdir(os.path.join(self.temp_dir,self.registration_id)):
                raise('Directory for the git clone was not allocated!  This is an internal catalog server error, please report this problem.')

            basedir = os.path.join(self.temp_dir,self.registration_id,'module_repo')

            self.log('Attempting to clone into: '+basedir);
            self.log('git clone ' + self.git_url)
            repo = git.Repo.clone_from(self.git_url, basedir)
            # try to get hash from repo
            self.log('current commit hash at HEAD:' + str(repo.heads.master.commit))
            git_commit_hash = repo.heads.master.commit
            if 'git_commit_hash' in self.params:
                if self.params['git_commit_hash']:
                    self.log('git checkout ' + self.params['git_commit_hash'].strip())
                    repo.git.checkout(self.params['git_commit_hash'].strip())
                    git_commit_hash = self.params['git_commit_hash'].strip()

            # we *think* this will solve the pesky intermittent git.lock issue by releasing everything
            #repo.git.clear_cache()
            # it doesn't work

            ##############################
            # 2 - sanity check (things parse, files exist, module_name matches, etc)
            self.set_build_step('reading files and performing basic checks')
            self.sanity_checks_and_parse(repo, basedir)

            ##############################
            # 2.5 - waiting for one minute at most until git releases .git/config.lock, if it still exists then kill it
            timeout = time.time() + 60
            git_config_lock_file = os.path.join(basedir, ".git", "config.lock")
            while os.path.exists(git_config_lock_file) and time.time() <= timeout:
                self.log('.git/config.lock exists, waiting 5s for it to release')
                time.sleep(5)
            if os.path.exists(git_config_lock_file):
                self.log('.git/config.lock file still there, we are just going to delete it....')
                os.remove(git_config_lock_file)

            ##############################
            # 3 docker build - in progress
            # perhaps make this a self attr?
            module_name_lc = self.get_required_field_as_string(self.kb_yaml,'module-name').strip().lower()
            self.db.set_build_log_module_name(self.registration_id, module_name_lc)
            self.image_name = self.docker_registry_host + '/' + module_name_lc + ':' + str(git_commit_hash)
            if not Registrar._TEST_WITHOUT_DOCKER:
                # timeout set to 30 min because we often get timeouts if multiple people try to push at the same time
                dockerclient = None
                docker_timeout = 1800
                if len(str(self.docker_base_url)) > 0:
                    dockerclient = DockerClient(base_url = str(self.docker_base_url),timeout=docker_timeout)
                else:
                    docker_host = os.environ['DOCKER_HOST']
                    if docker_host is None or len(docker_host) == 0:
                        raise ValueError('Docker host should be defined either in configuration '
                                         '(docker-base-url property) or in DOCKER_HOST environment variable')
                    docker_tls_verify = os.environ['DOCKER_TLS_VERIFY']
                    if docker_host.startswith('tcp://'):
                        docker_protocol = "http"
                        if (docker_tls_verify is not None) and docker_tls_verify == '1':
                            docker_protocol = "https"
                        docker_host = docker_host.replace('tcp://', docker_protocol + '://')
                    docker_cert_path = os.environ['DOCKER_CERT_PATH']
                    docker_tls = False
                    if (docker_cert_path is not None) and len(docker_cert_path) > 0:
                        docker_tls = DockerTLSConfig(verify=False, 
                                                     client_cert=(docker_cert_path + '/cert.pem', 
                                                                  docker_cert_path + '/key.pem'))
                    self.log("Docker settings from environment variables are used: docker-host = " + docker_host + 
                             ", docker_cert_path = " + str(docker_cert_path))
                    dockerclient = DockerClient(base_url = docker_host,timeout=docker_timeout,
                            version='auto', tls=docker_tls)
                # look for docker image
                # this tosses cookies if image doesn't exist, so wrap in try, and build if try reports "not found"
                #self.log(str(dockerclient.inspect_image(repo_name)))
                # if image does not exist, build and set state
                self.set_build_step('building the docker image')
                # imageId is not yet populated properly
                imageId = self.build_docker_image(dockerclient,self.image_name,basedir)

                self.set_build_step('pushing docker image to registry')
                self.push_docker_image(dockerclient,self.image_name)

                #self.log(str(dockerClient.containers()));
            else:
                self.log('IN TEST MODE!! SKIPPING DOCKER BUILD AND DOCKER REGISTRY UPDATE!!')

            # 4 - Update the DB
            self.set_build_step('updating the catalog')
            self.update_the_catalog(repo, basedir)
            
            self.build_is_complete()

        except Exception as e:
            # set the build state to error and log it
            self.set_build_error(str(e))
            self.log(traceback.format_exc(), is_error=True)
            self.log('BUILD_ERROR: '+str(e), is_error=True)
        finally:
            self.flush_log_to_db();
            self.logfile.close();
            self.cleanup();



    def sanity_checks_and_parse(self, repo, basedir):
        # check that files exist
        yaml_filename = 'kbase.yaml'
        if not os.path.isfile(os.path.join(basedir,'kbase.yaml')) :
            if not os.path.isfile(os.path.join(basedir,'kbase.yml')):
                raise ValueError('kbase.yaml file does not exist in repo, but is required!')
            else:
                yaml_filename = 'kbase.yml'
        # parse some stuff, and check for things
        with open(os.path.join(basedir,yaml_filename)) as kb_yaml_file:
            kb_yaml_string = kb_yaml_file.read()
        self.kb_yaml = yaml.load(kb_yaml_string)
        self.log('=====kbase.yaml parse:')
        self.log(pprint.pformat(self.kb_yaml))
        self.log('=====end kbase.yaml')

        module_name = self.get_required_field_as_string(self.kb_yaml,'module-name').strip()
        module_description = self.get_required_field_as_string(self.kb_yaml,'module-description').strip()
        version = self.get_required_field_as_string(self.kb_yaml,'module-version').strip()
        service_language = self.get_required_field_as_string(self.kb_yaml,'service-language').strip()
        owners = self.get_required_field_as_list(self.kb_yaml,'owners')

        # module_name must match what exists (unless it is not yet defined)
        if 'module_name' in self.module_details:
            if self.module_details['module_name'] != module_name:
                raise ValueError('kbase.yaml file module_name field has changed since last version! ' +
                                    'Module names are permanent- if this is a problem, contact a kbase admin.')
        else:
            # This must be the first registration, so the module must not exist yet
            self.check_that_module_name_is_valid(module_name);

        # you can't remove yourself from the owners list, or register something that you are not an owner of
        if self.username not in owners:
            raise ValueError('Your kbase username ('+self.username+') must be in the owners list in the kbase.yaml file.')

        # OPTIONAL TODO: check if all the users are on the owners list?  not necessarily required, because we
        # do a check during registration of the person who started the registration...

        # TODO: check for directory structure, method spec format, documentation, version
        self.validate_method_specs(basedir)

        # return the parse so we can figure things out later
        return self.kb_yaml


    def check_that_module_name_is_valid(self, module_name):
        if self.db.is_registered(module_name=module_name):
            raise ValueError('Module name (in kbase.yaml) is already registered.  Please specify a different name and try again.')
        if self.db.module_name_lc_exists(module_name_lc=module_name.lower()):
            raise ValueError('The case-insensitive module name (in kbase.yaml) is not unique.  Please specify a different name.')
        # only allow alphanumeric and underscore
        if not re.match(r'^[A-Za-z0-9_]+$', module_name):
            raise ValueError('Module names must be alphanumeric characters (including underscores) only, with no spaces.')


    def update_the_catalog(self, repo, basedir):

        # get the basic info that we need
        commit_hash = repo.head.commit.hexsha
        commit_message = repo.head.commit.message

        module_name = self.get_required_field_as_string(self.kb_yaml,'module-name')
        module_description = self.get_required_field_as_string(self.kb_yaml,'module-description')
        version = self.get_required_field_as_string(self.kb_yaml,'module-version')
        service_language = self.get_required_field_as_string(self.kb_yaml,'service-language')
        owners = self.get_required_field_as_list(self.kb_yaml,'owners')

        # first update the module name, which is now permanent, if we haven't already
        if ('module_name' not in self.module_details) or ('module_name_lc' not in self.module_details):
            error = self.db.set_module_name(self.git_url, module_name)
            if error is not None:
                raise ValueError('Unable to set module_name - there was an internal database error.' +error)

        # TODO: Could optimize by combining all these things into one mongo call, but for now this is easier.
        # Combining it into one call would just mean that this update happens as a single transaction, but a partial
        # update for now that fails midstream is probably not a huge issue- we can always reregister.

        # next update the basic information
        info = {
            'description': module_description,
            'language' : service_language
        }
        self.log('new info: '+pprint.pformat(info))
        error = self.db.set_module_info(info, git_url=self.git_url)
        if error is not None:
            raise ValueError('Unable to set module info - there was an internal database error: '+error)

        # next update the owners
        ownersListForUpdate = []
        for o in owners:
            # TODO: add some validation that the username is a valid kbase user
            ownersListForUpdate.append({'kb_username':o})
        self.log('new owners list: '+pprint.pformat(ownersListForUpdate))
        error = self.db.set_module_owners(ownersListForUpdate, git_url=self.git_url)
        if error is not None:
            raise ValueError('Unable to set module owners - there was an internal database error: '+error)

        # finally update the actual dev version info
        narrative_methods = []
        if os.path.isdir(os.path.join(basedir,'ui','narrative','methods')) :
            for m in os.listdir(os.path.join(basedir,'ui','narrative','methods')):
                if os.path.isdir(os.path.join(basedir,'ui','narrative','methods',m)):
                    narrative_methods.append(m)

        new_version = {
            'timestamp':self.timestamp,
            'version' : version,
            'git_commit_hash': commit_hash,
            'git_commit_message': commit_message,
            'narrative_methods': narrative_methods,
            'docker_img_name': self.image_name
        }
        self.log('new dev version object: '+pprint.pformat(new_version))
        error = self.db.update_dev_version(new_version, git_url=self.git_url)
        if error is not None:
            raise ValueError('Unable to update dev version - there was an internal database error: '+error)

        #push to NMS
        self.log('registering specs with NMS')
        self.nms.register_repo({'git_url':self.git_url, 'git_commit_hash':commit_hash})

        self.log('\ndone')

        # done!!!


    def validate_method_specs(self, basedir):
        self.log('validating narrative method specifications')
        if os.path.isdir(os.path.join(basedir,'ui','narrative','methods')) :
            for m in os.listdir(os.path.join(basedir,'ui','narrative','methods')):
                if os.path.isdir(os.path.join(basedir,'ui','narrative','methods',m)):
                    self.log('    - validating method: '+m)
                    # first grab the spec and display files, which are required
                    method_path = os.path.join(basedir,'ui','narrative','methods',m)
                    if not os.path.isfile(os.path.join(method_path,'spec.json')):
                        raise ValueError('Invalid narrative method specification ('+m+'): No spec.json file defined.')
                    if not os.path.isfile(os.path.join(method_path,'display.yaml')):
                        raise ValueError('Invalid narrative method specification ('+m+'): No spec.json file defined.')
                    with open(os.path.join(method_path,'spec.json')) as spec_json_file:
                        spec_json = spec_json_file.read()
                    with open(os.path.join(method_path,'display.yaml')) as display_yaml_file:
                        display_yaml = display_yaml_file.read()

                    # gather any extra html files
                    extraFiles = {}
                    for extra_file_name in os.listdir(os.path.join(method_path)):
                        if not os.path.isfile(os.path.join(method_path,extra_file_name)): break
                        if not extra_file_name.endswith('.html'): break
                        with open(os.path.join(method_path,extra_file_name)) as extra_file:
                            extrafiles[extra_file_name] = extra_file.read()

                    # validate against the NMS target endpoint
                    result = self.nms.validate_method({'id':m, 'spec_json':spec_json, 'display_yaml':display_yaml, 'extra_files':extraFiles});
    
                    # inspect results
                    if result['is_valid']>0:
                        self.log('        - valid!')
                        if 'warnings' in result:
                            if result['warnings']:
                                for w in result['warnings']:
                                    self.log('        - warning: '+w)
                    else:
                        self.log('        - not valid!', is_error=True)
                        if 'errors' in result:
                            if result['errors']:
                                for e in result['errors']:
                                    self.log('        - error: '+e, is_error=True)
                        else:
                            self.log('        - error is undefined!'+e,  is_error=True)

                        raise ValueError('Invalid narrative method specification ('+m+')')

        else:
            self.log('    - no ui/narrative/methods directory found, so no narrative methods will be deployed')






    def get_required_field_as_string(self, kb_yaml, field_name):
        if field_name not in kb_yaml:
            raise ValueError('kbase.yaml file missing "'+field_name+'" required field')
        value = kb_yaml[field_name].strip()
        if not value:
            raise ValueError('kbase.yaml file missing value for "'+field_name+'" required field')
        return value

    def get_required_field_as_list(self, kb_yaml, field_name):
        if field_name not in kb_yaml:
            raise ValueError('kbase.yaml file missing "'+field_name+'" required field')
        value = kb_yaml[field_name]
        if not type(value) is list:
            raise ValueError('kbase.yaml file "'+field_name+'" required field must be a list')
        return value


    def log(self, message, no_end_line=False, is_error=False):
        if no_end_line:
            content = message
        else:
            content = message + '\n'
        self.logfile.write(content)
        self.logfile.flush()

        lines = content.splitlines();
        for l in lines:
            # add each line to the buffer
            self.log_buffer.append({'content':l, 'error':is_error})

        # save the buffer to mongo if enough time has elapsed, or the buffer is more than 1000 lines
        if (time.time() - self.last_log_time > self.log_interval) or (len(self.log_buffer)>1000):
            self.flush_log_to_db();

    def flush_log_to_db(self):
        # todo: if we lose log lines, that's ok.  Make sure we handle case if log is larger than mongo doc size
        self.db.append_to_build_log(self.registration_id, self.log_buffer)
        self.log_buffer = [] #clear the buffer
        self.last_log_time = time.time() # reset the log timer


    def set_build_step(self, step):
        self.db.set_module_registration_state(git_url=self.git_url, new_state='building: '+step)
        self.db.set_build_log_state(self.registration_id, 'building: '+step)

    def set_build_error(self, error_message):
        self.db.set_module_registration_state(git_url=self.git_url, new_state='error', error_message=error_message)
        self.db.set_build_log_state(self.registration_id, 'error', error_message=error_message)

    def build_is_complete(self):
        self.db.set_module_registration_state(git_url=self.git_url, new_state='complete')
        self.db.set_build_log_state(self.registration_id, 'complete')

    def cleanup(self):
        if os.path.isdir(os.path.join(self.temp_dir,self.registration_id)):
            shutil.rmtree(os.path.join(self.temp_dir,self.registration_id))

    def build_docker_image(self, docker_client, image_name, basedir):
        self.log('\nBuilding the docker image for ' + image_name);
        #response = [ line for line in docker_client.build(path=basedir,rm=True,tag=image_name) ]
        #response_stream = response
        #imageId = response_stream[-1]
        #self.log(str(response_stream[-1]))

        # examine stream to determine success/failure of build
        imageId=None
        last={}
        for line in docker_client.build(path=basedir,rm=True,tag=image_name):
            line_parse = json.loads(line)
            if 'stream' in line_parse:
                self.log(line_parse['stream'],no_end_line=True)
            if 'errorDetail' in line_parse:
                self.log(str(line_parse),no_end_line=True)
                raise ValueError('Docker build failed: '+str(line_parse['errorDetail']))
            last=line_parse
        
        if 'stream' in last and last['stream'][:19]=='Successfully built ':
            imageId = docker_client.inspect_image(image_name)['Id']

        self.log('Docker build successful.')
        self.log('    Image Id:   ' + imageId)
        self.log('    Image Name: ' + image_name+'\n\n')
        return imageId

    def push_docker_image(self, docker_client, image_name):
        self.log('\nPushing docker image to registry for ' + image_name);
        colon_pos = image_name.rfind(':')  # This logic supports images with "host:port/" prefix for private registry 
        image=image_name[:colon_pos]
        tag=image_name[colon_pos+1:]
        #response = [ line for line in docker_client.push(image, tag=tag, stream=True) ]
        #response_stream = response
        #self.log(str(response_stream))

        # to do: examine stream to determine success/failure of build
        for line in docker_client.push(image, tag=tag, stream=True):
            # example line:
            #'{"status":"Pushing","progressDetail":{"current":32,"total":32},"progress":"[==================================================\\u003e]     32 B/32 B","id":"da200da4256c"}'
            line_parse = json.loads(line)
            if 'id' in line_parse:
                self.log(line_parse['id']+' - ',no_end_line=True)
            if 'status' in line_parse:
                self.log(line_parse['status'],no_end_line=True)
            if 'progress' in line_parse:
                self.log(' - ' + line_parse['progress'],no_end_line=True)
            #if 'progressDetail' in line_parse:
            #    self.log(' - ' + str(line_parse['progressDetail']),no_end_line=True)
            self.log('') # add an endline

        # check for errors here somehow!

        
        self.log('done pushing docker image to registry for ' + image_name+'\n');


    # Temporary flags to test everything except docker
    # we should remove once the test rig can fully support docker and an NMS
    _TEST_WITHOUT_DOCKER = False




