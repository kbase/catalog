import unittest

from biokbase.catalog.Impl import Catalog
from catalog_test_util import CatalogTestUtil

_RETRY_WRITES = "mongodb-retrywrites"


class CatalogConfigTest(unittest.TestCase):

    def test_catalog_without_retryWrites(self):
        self.catalog_cfg.pop(_RETRY_WRITES, None)
        catalog = Catalog(self.catalog_cfg)
        self.assertFalse(catalog.cc.db.mongo_retry_writes)

    def test_catalog_with_retryWrites_is_true(self):
        self.catalog_cfg[_RETRY_WRITES] = "true"
        catalog = Catalog(self.catalog_cfg)
        self.assertTrue(catalog.cc.db.mongo_retry_writes)

    @classmethod
    def setUpClass(cls):
        print("++++++++++++ RUNNING catalog_config_test.py +++++++++++")
        cls.cUtil = CatalogTestUtil(".")  # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog_cfg = cls.cUtil.getCatalogConfig()

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()
