import datetime
import json
import os
from configparser import ConfigParser
from pprint import pformat

from docker import APIClient as DockerAPIClient
from pymongo import MongoClient

from biokbase.catalog.db import MongoCatalogDBI


class CatalogTestUtil:

    def __init__(self, test_dir):
        self.test_dir = os.path.abspath(test_dir)

    def setUpEmpty(self, db_version=None):
        self.log("setUp()")
        self.log("test directory="+self.test_dir)
        self._setup_config()
        self._init_db_handles()
        self._clear_db()

        if db_version is not None:
            self.db_version.insert_one({'version_doc':True, 'version':db_version})

    def setUp(self):
        self.log("setUp()")
        self.log("test directory="+self.test_dir)

        self._setup_config()
        self._init_db_handles()
        self._clear_db()
        self._initialize_mongo_data()

    def _setup_config(self):

        # 1 read config file and pull out some stuff
        if not os.path.isfile(os.path.join(self.test_dir,'test.cfg')):
            raise ValueError('test.cfg does not exist in test dir')
        config = ConfigParser()
        config.read(os.path.join(self.test_dir,'test.cfg'))
        self.test_cfg = {}
        self.nms_test_cfg = {}
        for entry in config.items('catalog-test'):
            self.test_cfg[entry[0]] = entry[1]
        for entry in config.items('NarrativeMethodStore'):
            self.nms_test_cfg[entry[0]] = entry[1]
        self.log('test.cfg parse\n'+pformat(self.test_cfg))

        # passwords not needed in tests yet
        self.test_user_1 = self.test_cfg['test-user-1']
        #self.test_user_psswd_1 = self.test_cfg['test-user-psswd-1']
        self.test_user_2 = self.test_cfg['test-user-2']
        #self.test_user_psswd_2 = self.test_cfg['test-user-psswd-2']

        # 2 setup the scratch space
        self.scratch_dir = os.path.join(self.test_dir,'temp_test_files',datetime.datetime.now().strftime("%Y-%m-%d-(%H-%M-%S-%f)"))
        self.log("scratch directory="+self.scratch_dir)
        os.makedirs(self.scratch_dir)

        # 3 assemble the config file for the catalog service
        self.catalog_cfg = {
            'admin-users':self.test_user_2,
            'mongodb-host':self.test_cfg['mongodb-host'],
            'mongodb-database':self.test_cfg['mongodb-database'],
            'temp-dir':self.scratch_dir,
            'docker-base-url':self.test_cfg['docker-base-url'],
            'docker-registry-host':self.test_cfg['docker-registry-host'],
            'nms-url':self.test_cfg['nms-url'],
            'nms-admin-user':self.test_cfg.get('nms-admin-user', ''),
            'nms-admin-psswd':self.test_cfg.get('nms-admin-psswd', ''),
            'nms-admin-token': self.test_cfg.get('nms-admin-token', ''),
            'ref-data-base':self.test_cfg['ref-data-base'],
            'kbase-endpoint':self.test_cfg['kbase-endpoint'],
            'auth-service-url': self.test_cfg.get('auth-service-url', '')
        }
        self.dockerclient = DockerAPIClient(base_url=self.catalog_cfg['docker-base-url'])

    def _init_db_handles(self):
        # 2 check that db exists and collections are empty
        self.mongo = MongoClient('mongodb://'+self.test_cfg['mongodb-host'])
        db = self.mongo[self.test_cfg['mongodb-database']]
        self.db_version = db[MongoCatalogDBI._DB_VERSION]
        self.modules = db[MongoCatalogDBI._MODULES]
        self.module_versions = db[MongoCatalogDBI._MODULE_VERSIONS]
        self.local_functions = db[MongoCatalogDBI._LOCAL_FUNCTIONS]
        self.developers = db[MongoCatalogDBI._DEVELOPERS]
        self.build_logs = db[MongoCatalogDBI._BUILD_LOGS]
        self.favorites = db[MongoCatalogDBI._FAVORITES]
        self.client_groups = db[MongoCatalogDBI._CLIENT_GROUPS]
        self.volume_mounts = db[MongoCatalogDBI._VOLUME_MOUNTS]
        self.secure_config_params = db[MongoCatalogDBI._SECURE_CONFIG_PARAMS]

        self.exec_stats_raw = db[MongoCatalogDBI._EXEC_STATS_RAW]
        self.exec_stats_apps = db[MongoCatalogDBI._EXEC_STATS_APPS]
        self.exec_stats_users = db[MongoCatalogDBI._EXEC_STATS_USERS]

    def _clear_db(self):
        # just drop the test db
        self.db_version.drop()
        self.modules.drop()
        self.module_versions.drop()
        self.local_functions.drop()
        self.developers.drop()
        self.build_logs.drop()
        self.favorites.drop()
        self.client_groups.drop()
        self.volume_mounts.drop()
        self.exec_stats_raw.drop()
        self.exec_stats_apps.drop()
        self.exec_stats_users.drop()
        self.secure_config_params.drop()

        #if self.modules.count() > 0 :
        #    raise ValueError('mongo database collection "'+MongoCatalogDBI._MODULES+'"" not empty (contains '+str(self.modules.count())+' records).  aborting.')


    def _initialize_mongo_data(self):
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
                self.modules.insert_one(parsed_document)
                load_count+=1

        logs_document_dir = os.path.join(self.test_dir, 'initial_mongo_state', MongoCatalogDBI._BUILD_LOGS)
        for document_name in os.listdir(logs_document_dir):
            document_path = os.path.join(logs_document_dir,document_name)
            if os.path.isfile(document_path):
                with open(document_path) as document_file:
                    document = document_file.read()
                parsed_document = json.loads(document)
                self.build_logs.insert_one(parsed_document)
                load_count+=1

        favorites_document_dir = os.path.join(self.test_dir, 'initial_mongo_state', MongoCatalogDBI._FAVORITES)
        for document_name in os.listdir(favorites_document_dir):
            document_path = os.path.join(favorites_document_dir,document_name)
            if os.path.isfile(document_path):
                with open(document_path) as document_file:
                    document = document_file.read()
                parsed_document = json.loads(document)
                if isinstance(parsed_document,list):
                    for p in parsed_document:
                        self.favorites.insert_one(p)
                        load_count+=1
                else:
                    self.favorites.insert_one(parsed_document)
                    load_count+=1

        volume_mounts_dir = os.path.join(self.test_dir, 'initial_mongo_state', MongoCatalogDBI._VOLUME_MOUNTS)
        for document_name in os.listdir(volume_mounts_dir):
            document_path = os.path.join(volume_mounts_dir,document_name)
            if os.path.isfile(document_path):
                with open(document_path) as document_file:
                    document = document_file.read()
                parsed_document = json.loads(document)
                if isinstance(parsed_document,list):
                    for p in parsed_document:
                        self.volume_mounts.insert_one(p)
                        load_count+=1
                else:
                    self.volume_mounts.insert_one(parsed_document)
                    load_count+=1

        client_groups_dir = os.path.join(self.test_dir, 'initial_mongo_state', MongoCatalogDBI._CLIENT_GROUPS)
        for document_name in os.listdir(client_groups_dir):
            document_path = os.path.join(client_groups_dir,document_name)
            if os.path.isfile(document_path):
                with open(document_path) as document_file:
                    document = document_file.read()
                parsed_document = json.loads(document)
                if isinstance(parsed_document,list):
                    for p in parsed_document:
                        self.client_groups.insert_one(p)
                        load_count+=1
                else:
                    self.client_groups.insert_one(parsed_document)
                    load_count+=1

        self.log(str(load_count)+" documents loaded")



    def anonymous_ctx(self):
        return {}

    def user_ctx(self):
        return {
            "user_id": self.test_user_1,
            "token":'fake_token'
            # TODO: authenticate and add real token, but not required yet
        }

    def admin_ctx(self):
        return {
            "user_id": self.test_user_2,
            "token":'fake_token'
            # TODO: authenticate and add real token, but not required yet
        }

    def get_test_repo_1(self):
        return self.test_cfg['test-module-repo-1']

    def get_test_repo_2(self):
        return self.test_cfg['test-module-repo-2']

    def getCatalogConfig(self):
        return self.catalog_cfg

    def tearDown(self):
        self.log("tearDown()")
        self._clear_db()

        # remove testing images
        for image in self.dockerclient.images(
                name=self.catalog_cfg['docker-registry-host']+"/kbase"):
            print(image)
            self.dockerclient.remove_image(image['Id'])

        # make sure NMS is clean after each test
        self.mongo.drop_database(self.nms_test_cfg['method-spec-mongo-dbname'])

    def log(self, mssg):
        # uncomment to debug test rig- warning: on travis this may print any passwords in your config
        #print("CATALOG_TEST_UTIL: "+mssg)
        pass



