


import time

from biokbase.catalog.db import MongoCatalogDBI


class Registrar:

    # params is passed in from the controller, should be the same as passed into the spec
    # db is a reference to the Catalog DB interface (usually a MongoCatalogDBI instance)
    def __init__(self, params, timestamp, username, token, db, temp_dir):
        self.db = db
        self.params = params
        self.timestamp = timestamp
        self.username = username
        self.token = token
        self.db = db
        self.temp_dir = temp_dir

    def start_registration(self):
        somefile = open(self.temp_dir+'/file'+str(self.timestamp), 'w')
        somefile.write('doing something');
        somefile.close();
