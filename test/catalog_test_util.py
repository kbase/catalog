

import os
import json

from pprint import pprint, pformat
from datetime import datetime
from ConfigParser import ConfigParser
from pymongo import MongoClient


from biokbase.catalog.db import MongoCatalogDBI


class CatalogTestUtil:


    def __init__(self, test_dir):
        self.test_dir = os.path.abspath(test_dir)


    def setUp(self):
        self.log("setUp()")
        self.log("test directory="+self.test_dir)

        # 1 read config file and pull out some stuff
        if not os.path.isfile(os.path.join(self.test_dir,'test.cfg')):
            raise ValueError('test.cfg does not exist in test dir')
        config = ConfigParser()
        config.read(os.path.join(self.test_dir,'test.cfg'))
        self.test_cfg = {}
        for entry in config.items('catalog-test'):
            self.test_cfg[entry[0]] = entry[1]
        self.log('test.cfg parse\n'+pformat(self.test_cfg))

        self.test_user_1 = self.test_cfg['test-user-2']
        self.test_user_psswd_1 = self.test_cfg['test-user-psswd-1']
        self.test_user_2 = self.test_cfg['test-user-2']
        self.test_user_psswd_2 = self.test_cfg['test-user-psswd-2']

        # 2 check that db exists and collections are empty
        self.mongo = MongoClient('mongodb://'+self.test_cfg['mongodb-host'])
        db = self.mongo[self.test_cfg['mongodb-database']]
        self.modules = db[MongoCatalogDBI._MODULES]
        if self.modules.count() > 0 :
            raise ValueError('mongo database collection "'+MongoCatalogDBI._MODULES+'"" not empty (contains '+str(self.modules.count())+' records).  aborting.')

        self.initialize_mongo()

        # 3 setup the scratch space
        self.scratch_dir = os.path.join(self.test_dir,str(datetime.now()))
        self.log("scratch directory="+self.scratch_dir)
        os.mkdir(self.scratch_dir)


        # 4 startup any dependencies (nms, docker registry?)


        # 4 assemble the config file for the catalog service
        self.catalog_cfg = {
            'admin-users':self.test_user_2,
            'mongodb-host':self.test_cfg['mongodb-host'],
            'mongodb-database':self.test_cfg['mongodb-database'],
            'temp-dir':self.scratch_dir,
            'docker-base-url':self.test_cfg['docker-base-url'],
            'nms-url':self.test_cfg['nms-url'],
            'nms-admin-user':self.test_cfg['nms-admin-user'],
            'nms-admin-psswd':self.test_cfg['nms-admin-psswd']
        }


    def initialize_mongo(self):
        self.log("initializing mongo")
        # we only have one collection for now, but this should look over all collection folders
        load_count = 0
        modules_document_dir = os.path.join(self.test_dir, 'initial_mongo_state', MongoCatalogDBI._MODULES)
        for document_name in os.listdir(modules_document_dir):
            document_path = os.path.join(modules_document_dir,document_name)
            if os.path.isfile(document_path):
                with open(document_path) as document_file:
                    document = document_file.read()
                parsed_document = json.loads(document)
                self.modules.insert(parsed_document)
                load_count+=1

        self.log(str(load_count)+" documents loaded")



    def anonymous_ctx(self):
        return {}

    def user_ctx(self):
        return {
            "user_id": self.test_user_1
            # TODO: authenticate and add token, but not required yet
        }

    def admin_ctx(self):
        return {
            "user_id": self.test_user_2
            # TODO: authenticate and add token, but not required yet
        }


    def getCatalogConfig(self):
        return self.catalog_cfg

    def tearDown(self):
        self.log("tearDown()")
        self.modules.drop()

    def log(self, mssg):
        #print("CATALOG_TEST_UTIL: "+mssg)
        pass



