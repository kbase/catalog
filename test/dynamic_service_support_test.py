

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


# tests all the basic get methods
class DynamicServiceSupportTest(unittest.TestCase):


    def test_list_dynamic_modules(self):

        mods = self.catalog.list_service_modules(self.cUtil.anonymous_ctx(),
            {})[0]
        pprint(mods)

        #ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
        #    {'module_name':'DynamicService'})[0]
        #pprint(ver)

        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
            {'module_name':'DynamicService','only_service_versions':0,'lookup':'>0.0.0,<2.0.0'})[0]
        print('------')
        pprint(ver)


    #def test_version_fetch_basics(self):

    #    version = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
    #        {'module_name':'release_history','version':'dev'})[0]
    #    pprint(version)
    #    print 'howdy'
    

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING version_fetch_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        pass #cls.cUtil.tearDown()




