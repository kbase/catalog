import time
import sys
import git
import requests
from urlparse import urlparse
from docker import Client as DockerClient

from biokbase.catalog.db import MongoCatalogDBI


class Registrar:

    # params is passed in from the controller, should be the same as passed into the spec
    # db is a reference to the Catalog DB interface (usually a MongoCatalogDBI instance)
    def __init__(self, params, timestamp, username, token, db, temp_dir, docker_base_url):
        self.db = db
        self.params = params
        self.timestamp = timestamp
        self.username = username
        self.token = token
        self.db = db
        self.temp_dir = temp_dir
        self.docker_base_url = docker_base_url

    def start_registration(self):

        git_url=self.params['git_url']
        parsed_url=urlparse(git_url)
        # really should check whether dir exists already, and
        # whether it would be appropriate to remove and re-clone
        # or simply pull
        repo = git.Repo.clone_from(git_url,self.temp_dir+parsed_url.path)

	dockerclient = DockerClient(base_url = str(self.docker_base_url))
        # look for docker image / instance (might need an http call,
        # dockerhub-ci does not seem to respond to search API)
        # if image does not exist, build, push to dockerhub-ci, and set state
        # if instance does not exist, start and set state

        somefile = open(self.temp_dir+'/file'+str(self.timestamp), 'w')
#        somefile.write('doing something\n');
#        somefile.write(str(dockerclient.containers()));
        somefile.write(str(parsed_url.path));
        somefile.write(str(self.params));
        somefile.close();
