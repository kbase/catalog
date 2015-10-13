

import warnings
import biokbase.catalog.version

from biokbase.catalog.db import MongoCatalogDBI



class CatalogController:


    def __init__(self, config):

        # first grab the admin list
        self.adminList = []
        if 'admin-users' in config:
            self.adminList = [x.strip() for x in config['admin-users'].split(',')]
        if not self.adminList:
            warnings.warn('no "admin-users" are set in config of CatalogController.')
        print(self.adminList)

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



    def register_repo(self, params, user):

        # 1) first check if the repo exists, and get the state

        # 2)
        self.db.set_repo_registration_state("http://github.com/msneddon/kb_sdk", {'state':'started'})


    def version(self):
        return biokbase.catalog.version.CATALOG_VERSION




