import time
import sys
import os
import traceback
import shutil
import git
import yaml
import git
import yaml
import requests
from urlparse import urlparse
from docker import Client as DockerClient

from biokbase.catalog.db import MongoCatalogDBI


class Registrar:

    # params is passed in from the controller, should be the same as passed into the spec
    # db is a reference to the Catalog DB interface (usually a MongoCatalogDBI instance)
    def __init__(self, params, timestamp, username, token, db, temp_dir, docker_base_url, module_details):
        self.db = db
        self.params = params
        # at this point, we assume git_url has been checked
        self.git_url = params['git_url']

        self.timestamp = timestamp
        self.username = username
        self.token = token
        self.db = db
        self.temp_dir = temp_dir
        self.docker_base_url = docker_base_url

        # (most) of the mongo document for this module snapshot before this registration
        self.module_details = module_details

    def start_registration(self):
        try:
            self.logfile = open(self.temp_dir+'/registration.log.'+str(self.timestamp), 'w')
            self.log(str(self.params));

            # 1 - clone the repo
            self.set_build_step('cloning git repo')
            parsed_url=urlparse(self.git_url)
            basedir = self.temp_dir+parsed_url.path
            # quick fix- if directory exists, then remove it.  should do something smarter
            if os.path.isdir(basedir):
                shutil.rmtree(basedir)
            repo = git.Repo.clone_from(self.git_url, basedir)
            # TODO: switch to the right commit/branch based on params
            self.log(str(parsed_url.path));

            # 2 - sanity check (things parse, files exist, module_name matches, etc)
            self.set_build_step('basic checks')
            kb_yaml = self.sanity_checks_and_parse(repo, basedir)

            # 3 docker build
            # pseudocode
            # get_repo_details
            # look for docker image / instance
            # if image does not exist, build and set state
            # if instance does not exist, start and set state
            dockerclient = DockerClient(base_url = str(self.docker_base_url))

            # 4 - Update the DB
            self.set_build_step('updating the catalog')
            self.update_the_catalog(repo, basedir, kb_yaml)
            
            self.build_is_complete(self)

        except Exception as e:
            # set the build state to error and log it
            self.set_build_error(str(e))
            self.log(traceback.format_exc())
            self.log('BUILD_ERROR: '+str(e))
        finally:
            self.logfile.close();



    def sanity_checks_and_parse(self, repo, basedir, module_details):
        # check that files exist
        if not os.path.isfile(basedir+'/kbase.yaml') :
            raise ValueError('kbase.yaml file does not exist in repo, but is required!')
        # parse some stuff, and check for things
        kb_yaml = yaml.load(basedir+'/kbase.yaml')

        module_name = get_required_field_as_string(kb_yaml,'module-name')
        module_description = get_required_field_as_string(kb_yaml,'module-description')
        service_language = get_required_field_as_string(kb_yaml,'service-language')
        owners = get_required_field_as_list(kb_yaml,'owners')

        # module_name must match what exists (unless it is not yet defined)
        if 'module_name' in module_details:
            if module_details['module_name'] != module_name:
                raise ValueError('kbase.yaml file module_name field has changed since last version! ' +
                                    'Module names are permanent- if this is a problem, contact an admin.')
        else:
            # This must be the first registration, so the module must not exist yet
            if self.db.is_registered(module_name=module_name):
                raise ValueError('Module name (in kbase.yaml) is already registered.  Please specify a different name and try again.')

        # return the parse so we can figure things out later
        return kb_yaml


    def update_the_catalog(self, repo, basedir, kb_yaml, module_details):

        # get the basic info that we need
        commit_hash = repo.head.commit
        module_name = get_required_field_as_string(kb_yaml,'module-name')
        module_description = get_required_field_as_string(kb_yaml,'module-description')
        service_language = get_required_field_as_string(kb_yaml,'service-language')
        owners = get_required_field_as_list(kb_yaml,'owners')

        # first update the module name, which is now permanent, if we haven't already
        #if 'module_name' not in module_details:



        pass



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


    def log(self, message):
        self.logfile.write(message+'\n')
        self.logfile.flush()

    def set_build_step(self, step):
        self.db.set_module_registration_state(git_url=self.git_url, new_state='building: '+step)

    def set_build_error(self, error_message):
        self.db.set_module_registration_state(git_url=self.git_url, new_state='error', error_message=error_message)

    def build_is_complete(self):
        self.db.set_module_registration_state(git_url=self.git_url, new_state='complete')
