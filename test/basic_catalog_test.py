

import unittest

import os

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


# tests all the basic get methods
class BasicCatalogTest(unittest.TestCase):



    def test_version(self):
        self.assertEqual(self.catalog.version(self.cUtil.anonymous_ctx()),['0.0.2'],
            'incorrect version number')


    def test_register(self):
        pass



    @classmethod
    def setUpClass(cls):
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()



