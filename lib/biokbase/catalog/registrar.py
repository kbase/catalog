


import time
import sys

from biokbase.catalog.db import MongoCatalogDBI
from docker import Client as DockerClient


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
        # pseudocode
        # get_repo_details
        # look for docker image / instance
        # if image does not exist, build and set state
        # if instance does not exist, start and set state
        print self.docker_base_url
	dockerclient = DockerClient(base_url = str(self.docker_base_url))
        print dockerclient
        print dockerclient.containers
        somefile = open(self.temp_dir+'/file'+str(self.timestamp), 'w')
        somefile.write('doing something\n');
        somefile.write(str(dockerclient));
        somefile.write(str(dockerclient.containers()));
        somefile.write(str(self.params));
        somefile.close();
        print >> sys.stderr, dockerclient.containers()
