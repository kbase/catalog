import unittest

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


class HiddenConfigParamsTest(unittest.TestCase):

    # assumes no client groups exist
    def test_permissions(self):
        anonCtx = self.cUtil.anonymous_ctx()
        userCtx = self.cUtil.user_ctx()

        # set_secure_config_params
        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(anonCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' +
                         'configuration parameters.')

        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(userCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' +
                         'configuration parameters.')

        # remove_secure_config_params
        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(anonCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' +
                         'configuration parameters.')

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(userCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' +
                         'configuration parameters.')

        # get_secure_config_params
        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(anonCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' +
                         'configuration parameters.')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(userCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' +
                         'configuration parameters.')

    def test_errors(self):
        adminCtx = self.cUtil.admin_ctx()

        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(adminCtx, {})
        self.assertEqual(str(e.exception),
                         'data parameter field is required')

        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(adminCtx, {'data': "test"})
        self.assertEqual(str(e.exception),
                         'data parameter field must be a list')

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(adminCtx, {})
        self.assertEqual(str(e.exception),
                         'data parameter field is required')

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(adminCtx, {'data': "test"})
        self.assertEqual(str(e.exception),
                         'data parameter field must be a list')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(adminCtx, {})
        self.assertEqual(str(e.exception),
                         'module_name parameter field is required')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(adminCtx, {'module_name': [1, 2, 3]})
        self.assertEqual(str(e.exception),
                         'module_name parameter field must be a string')

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(adminCtx, {'module_name': 'abc',
                                                             'version': [1, 2, 3]})
        self.assertEqual(str(e.exception),
                         'version parameter field must be a string')

    def test_no_data(self):
        adminCtx = self.cUtil.admin_ctx()

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test0',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 0)

    def test_set_parameters(self):
        adminCtx = self.cUtil.admin_ctx()
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test1',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value0'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test1',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['module_name'], 'Test1')
        self.assertEqual(params[0]['param_name'], 'param0')
        self.assertEqual(params[0]['param_value'], 'value0')
        self.assertEqual(params[0]['version'], '')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test1',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value1'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'Test1',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_value'], 'value1')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test1',
                                                                   'param_name': 'param2',
                                                                   'param_value': 'value2'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test1',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 2)

    def test_remove_parameters(self):
        adminCtx = self.cUtil.admin_ctx()
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test2',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value0'},
                                                                  {'module_name': 'Test2',
                                                                   'param_name': 'param1',
                                                                   'param_value': 'value1'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test2',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 2)

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': 'Test2',
                                                                      'param_name': 'param1'}]})

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test2',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_name'], 'param0')
        self.assertEqual(params[0]['param_value'], 'value0')

    def test_versions(self):
        adminCtx = self.cUtil.admin_ctx()
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value0'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 1)

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                   'param_name': 'param0',
                                                                   'version': 'special_version',
                                                                   'param_value': 'value1'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 2)

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                      'param_name': 'param0'}]})

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_name'], 'param0')
        self.assertEqual(params[0]['param_value'], 'value1')
        self.assertEqual(params[0]['version'], 'special_version')

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                      'param_name': 'param0',
                                                                      'version': 'special_version'}]})

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3',
                                                                  'load_all_versions': 1})[0]
        self.assertEqual(len(params), 0)

    def test_module_versions(self):
        adminCtx = self.cUtil.admin_ctx()
        module_name = 'onerepotest'
        version_tag = 'release'
        mv = self.catalog.get_module_version(adminCtx, {'module_name': module_name,
                                                        'version': version_tag})[0]
        git_commit_hash = mv['git_commit_hash']
        semantic_version = mv['version']
        mv2 = self.catalog.get_module_version(adminCtx, {'module_name': module_name,
                                                         'version': semantic_version})[0]

        garbage = 'garbage'
        param_name = 'param0'
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                   'param_name': param_name,
                                                                   'param_value': 'value0'},
                                                                  {'module_name': module_name,
                                                                   'param_name': param_name,
                                                                   'version': garbage,
                                                                   'param_value': 'value1'}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value0')

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                      'param_name': param_name,
                                                                      'version': garbage}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value0')
        self.check_secure_param_value(module_name, git_commit_hash, 'param0', 'value0')
        self.check_secure_param_value(module_name, semantic_version, 'param0', 'value0')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                   'param_name': param_name,
                                                                   'version': version_tag,
                                                                   'param_value': 'value1'}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value1')
        self.check_secure_param_value(module_name, git_commit_hash, 'param0', 'value1')
        self.check_secure_param_value(module_name, semantic_version, 'param0', 'value1')

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                      'param_name': param_name,
                                                                      'version': version_tag}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value0')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                   'param_name': param_name,
                                                                   'version': git_commit_hash,
                                                                   'param_value': 'value2'}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value2')
        self.check_secure_param_value(module_name, git_commit_hash, 'param0', 'value2')
        self.check_secure_param_value(module_name, semantic_version, 'param0', 'value2')

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                      'param_name': param_name,
                                                                      'version': git_commit_hash}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value0')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': module_name,
                                                                   'param_name': param_name,
                                                                   'version': semantic_version,
                                                                   'param_value': 'value3'}]})
        self.check_secure_param_value(module_name, version_tag, 'param0', 'value3')
        self.check_secure_param_value(module_name, git_commit_hash, 'param0', 'value3')
        self.check_secure_param_value(module_name, semantic_version, 'param0', 'value3')

    def check_secure_param_value(self, module_name, version, param_name, param_value):
        params = self.catalog.get_secure_config_params(self.cUtil.admin_ctx(),
                                                       {'module_name': module_name,
                                                        'version': version})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_name'], param_name)
        self.assertEqual(params[0]['param_value'], param_value)

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING secure_config_params.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.')  # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        print('ready')

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()
