

import sys
import os
import traceback
import shutil

import git
import yaml
import pprint

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
    #        dockerclient = DockerClient(base_url = str(self.docker_base_url))
    #        somefile.write(str(dockerclient.containers()));


            # 4 - Update the DB
            self.set_build_step('updating the catalog')
            self.update_the_catalog(repo, basedir, kb_yaml)
            
            self.build_is_complete()

        except Exception as e:
            # set the build state to error and log it
            self.set_build_error(str(e))
            self.log(traceback.format_exc())
            self.log('BUILD_ERROR: '+str(e))
        finally:
            self.logfile.close();



    def sanity_checks_and_parse(self, repo, basedir):
        # check that files exist
        if not os.path.isfile(basedir+'/kbase.yaml') :
            raise ValueError('kbase.yaml file does not exist in repo, but is required!')
        # parse some stuff, and check for things
        with open(basedir+'/kbase.yaml') as kb_yaml_file:
            kb_yaml_string = kb_yaml_file.read()
        kb_yaml = yaml.load(kb_yaml_string)
        self.log('=====kbase.yaml parse:')
        self.log(pprint.pformat(kb_yaml))
        self.log('=====end kbase.yaml')

        module_name = self.get_required_field_as_string(kb_yaml,'module-name')
        module_description = self.get_required_field_as_string(kb_yaml,'module-description')
        version = self.get_required_field_as_string(kb_yaml,'module-version')
        service_language = self.get_required_field_as_string(kb_yaml,'service-language')
        owners = self.get_required_field_as_list(kb_yaml,'owners')

        # module_name must match what exists (unless it is not yet defined)
        if 'module_name' in self.module_details:
            if self.module_details['module_name'] != module_name:
                raise ValueError('kbase.yaml file module_name field has changed since last version! ' +
                                    'Module names are permanent- if this is a problem, contact an admin.')
        else:
            # This must be the first registration, so the module must not exist yet
            if self.db.is_registered(module_name=module_name):
                raise ValueError('Module name (in kbase.yaml) is already registered.  Please specify a different name and try again.')
            # TODO: additional contratins on the module name

        # you can't remove yourself from the owners list, or register something that you are not an owner of
        if self.username not in owners:
            raise ValueError('Your kbase username ('+self.username+') must be in the owners list in the kbase.yaml file.')

        # TODO: check for directory structure, method spec format, documentation, version 

        # return the parse so we can figure things out later
        return kb_yaml


    def update_the_catalog(self, repo, basedir, kb_yaml):

        # get the basic info that we need
        commit_hash = repo.head.commit.hexsha
        commit_message = repo.head.commit.message

        module_name = self.get_required_field_as_string(kb_yaml,'module-name')
        module_description = self.get_required_field_as_string(kb_yaml,'module-description')
        version = self.get_required_field_as_string(kb_yaml,'module-version')
        service_language = self.get_required_field_as_string(kb_yaml,'service-language')
        owners = self.get_required_field_as_list(kb_yaml,'owners')

        # first update the module name, which is now permanent, if we haven't already
        if 'module_name' not in self.module_details:
            success = self.db.set_module_name(self.git_url, module_name)
            if not success:
                raise ValueError('Unable to set module_name - there was an internal database error.')

        # TODO: Could optimize by combining all these things into one mongo call, but for now this is easier.
        # Combining it into one call would just mean that this update happens as a single transaction, but a partial
        # update for now that fails midstream is probably not a huge issue- we can always reregister.

        # next update the basic information
        info = {
            'description': module_description,
            'language' : service_language,
            'version' : version
        }
        self.log('new info: '+pprint.pformat(info))
        success = self.db.set_module_info(info, git_url=self.git_url)
        if not success:
            raise ValueError('Unable to set module info - there was an internal database error.')

        # next update the owners
        ownersListForUpdate = []
        for o in owners:
            # TODO: add some validation that the username is a valid kbase user
            ownersListForUpdate.append({'kb_username':o})
        self.log('new owners list: '+pprint.pformat(ownersListForUpdate))
        success = self.db.set_module_owners(ownersListForUpdate, git_url=self.git_url)
        if not success:
            raise ValueError('Unable to set module owners - there was an internal database error.')

        # finally update the actual dev version info
        narrative_methods = []
        if os.path.isdir(basedir+'/ui/narrative/methods') :
            for m in os.listdir(basedir+'/ui/narrative/methods'):
                if os.path.isdir(basedir+'/ui/narrative/methods/'+m):
                    narrative_methods.append(m)

        new_version = {
            'timestamp':self.timestamp,
            'git_commit_hash': commit_hash,
            'git_commit_message': commit_message,
            'narrative_methods': narrative_methods
        }
        self.log('new dev version object: '+pprint.pformat(new_version))
        success = self.db.update_dev_version(new_version, git_url=self.git_url)
        if not success:
            raise ValueError('Unable to update dev version - there was an internal database error.')

        # done!!!



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