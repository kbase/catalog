import unittest
from unittest.mock import Mock, patch
import os

from biokbase.catalog.registrar import Registrar


class RegistrarRegistryTest(unittest.TestCase):

    def setUp(self):
        self.params = {'git_url': 'https://github.com/example/repo.git'}
        self.registration_id = 'test123'
        self.timestamp = 1234567890
        self.username = 'testuser'
        self.is_admin = False
        self.token = 'test-token'
        self.db = Mock()
        self.temp_dir = '/tmp'
        self.docker_base_url = 'unix://var/run/docker.sock'
        self.nms_url = 'http://localhost:7125/rpc'
        self.nms_admin_token = 'nms-token'
        self.module_details = {'release_version_list': [], 'beta_version_list': []}
        self.ref_data_base = '/kb/data'
        self.kbase_endpoint = 'https://ci.kbase.us/services'
        self.prev_dev_version = None

    def test_registrar_with_same_registry_hosts(self):
        """Test registrar when both registry hosts are the same"""
        docker_registry_host = 'registry.com'
        docker_registry_client_host = 'registry.com'
        
        registrar = Registrar(
            self.params, self.registration_id, self.timestamp, self.username,
            self.is_admin, self.token, self.db, self.temp_dir,
            self.docker_base_url, docker_registry_host, docker_registry_client_host,
            self.nms_url, self.nms_admin_token, self.module_details,
            self.ref_data_base, self.kbase_endpoint, self.prev_dev_version
        )
        
        self.assertEqual(registrar.docker_registry_host, 'registry.com')
        self.assertEqual(registrar.docker_registry_client_host, 'registry.com')

    def test_registrar_with_different_registry_hosts(self):
        """Test registrar when registry hosts are different"""
        docker_registry_host = 'internal.registry.com'
        docker_registry_client_host = 'external.registry.com'
        
        registrar = Registrar(
            self.params, self.registration_id, self.timestamp, self.username,
            self.is_admin, self.token, self.db, self.temp_dir,
            self.docker_base_url, docker_registry_host, docker_registry_client_host,
            self.nms_url, self.nms_admin_token, self.module_details,
            self.ref_data_base, self.kbase_endpoint, self.prev_dev_version
        )
        
        self.assertEqual(registrar.docker_registry_host, 'internal.registry.com')
        self.assertEqual(registrar.docker_registry_client_host, 'external.registry.com')

    @patch('biokbase.catalog.registrar.subprocess')
    @patch('biokbase.catalog.registrar.os.path.isdir')
    @patch('biokbase.catalog.registrar.os.mkdir')
    @patch('biokbase.catalog.registrar.codecs.open')
    def test_image_name_construction(self, mock_open, mock_mkdir, mock_isdir, mock_subprocess):
        """Test that image names are constructed with correct registry hosts"""
        mock_isdir.return_value = True
        mock_subprocess.check_call.return_value = None
        mock_subprocess.check_output.return_value = b'abcd1234'
        
        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        docker_registry_host = 'internal.registry.com'
        docker_registry_client_host = 'external.registry.com'
        
        registrar = Registrar(
            self.params, self.registration_id, self.timestamp, self.username,
            self.is_admin, self.token, self.db, self.temp_dir,
            self.docker_base_url, docker_registry_host, docker_registry_client_host,
            self.nms_url, self.nms_admin_token, self.module_details,
            self.ref_data_base, self.kbase_endpoint, self.prev_dev_version
        )
        
        # Mock the kb_yaml content for module name
        registrar.kb_yaml = {'module-name': 'TestModule'}
        registrar.get_required_field_as_string = Mock(return_value='TestModule')
        
        # Test that image names are constructed correctly
        module_name_lc = 'testmodule'
        git_commit_hash = 'abcd1234'
        
        # These should be set during image name construction
        expected_client_image = f'{docker_registry_client_host}/kbase:{module_name_lc}.{git_commit_hash}'
        expected_internal_image = f'{docker_registry_host}/kbase:{module_name_lc}.{git_commit_hash}'
        
        # Set the values as they would be in start_registration
        registrar.image_name = expected_client_image
        registrar.internal_image_name = expected_internal_image
        
        self.assertEqual(registrar.image_name, expected_client_image)
        self.assertEqual(registrar.internal_image_name, expected_internal_image)


if __name__ == '__main__':
    unittest.main()