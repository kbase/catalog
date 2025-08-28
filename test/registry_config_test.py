import unittest
from unittest.mock import patch

from biokbase.catalog.controller import CatalogController


class RegistryConfigTest(unittest.TestCase):

    def get_base_config(self):
        return {
            'mongodb-host': 'localhost:27017',
            'mongodb-database': 'test',
            'temp-dir': '/tmp',
            'docker-base-url': 'unix://var/run/docker.sock',
            'ref-data-base': '/kb/data',
            'kbase-endpoint': 'https://ci.kbase.us/services',
            'auth-service-api': 'http://localhost:7777',
            'admin-roles': 'KBASE_ADMIN,CATALOG_ADMIN',
            'nms-url': 'http://localhost:7125/rpc',
            'nms-admin-token': 'test-token'
        }

    def test_docker_registry_host_only(self):
        """Test backward compatibility with only docker-registry-host set"""
        config = self.get_base_config()
        config['docker-registry-host'] = 'internal.registry.com'
        
        with patch('biokbase.catalog.controller.MongoCatalogDBI'):
            controller = CatalogController(config)
            self.assertEqual(controller.docker_registry_host, 'internal.registry.com')
            self.assertEqual(controller.docker_registry_client_host, 'internal.registry.com')

    def test_docker_registry_client_host_set(self):
        """Test with both registry hosts set to different values"""
        config = self.get_base_config()
        config['docker-registry-host'] = 'internal.registry.com'
        config['docker-registry-client-host'] = 'external.registry.com'
        
        with patch('biokbase.catalog.controller.MongoCatalogDBI'):
            controller = CatalogController(config)
            self.assertEqual(controller.docker_registry_host, 'internal.registry.com')
            self.assertEqual(controller.docker_registry_client_host, 'external.registry.com')

    def test_docker_registry_client_host_same_as_host(self):
        """Test with both registry hosts set to same value"""
        config = self.get_base_config()
        config['docker-registry-host'] = 'registry.com'
        config['docker-registry-client-host'] = 'registry.com'
        
        with patch('biokbase.catalog.controller.MongoCatalogDBI'):
            controller = CatalogController(config)
            self.assertEqual(controller.docker_registry_host, 'registry.com')
            self.assertEqual(controller.docker_registry_client_host, 'registry.com')


if __name__ == '__main__':
    unittest.main()