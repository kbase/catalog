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

    def test_docker_registry_host_configuration(self):
        # Test with only docker-registry-host set (backward compatibility)
        config = self.catalog_cfg.copy()
        catalog = Catalog(config)
        self.assertEqual(catalog.cc.docker_registry_host, config['docker-registry-host'])
        self.assertEqual(catalog.cc.docker_registry_client_host, config['docker-registry-host'])

    def test_docker_registry_client_host_configuration(self):
        # Test with both registry hosts set
        config = self.catalog_cfg.copy()
        config['docker-registry-client-host'] = 'external.example.com'
        catalog = Catalog(config)
        self.assertEqual(catalog.cc.docker_registry_host, config['docker-registry-host'])
        self.assertEqual(catalog.cc.docker_registry_client_host, 'external.example.com')

    @classmethod
    def setUpClass(cls):
        print("++++++++++++ RUNNING catalog_config_test.py +++++++++++")
        cls.cUtil = CatalogTestUtil(".")  # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog_cfg = cls.cUtil.getCatalogConfig()

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()
