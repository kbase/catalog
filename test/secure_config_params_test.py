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
                         'configuration parameters.');

        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(userCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' + 
                         'configuration parameters.');

        # remove_secure_config_params
        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(anonCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' + 
                         'configuration parameters.');

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(userCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' + 
                         'configuration parameters.');

        # get_secure_config_params
        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(anonCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' + 
                         'configuration parameters.');

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(userCtx, {})
        self.assertEqual(str(e.exception), 'You do not have permission to work with hidden ' + 
                         'configuration parameters.');


    def test_errors(self):
        adminCtx = self.cUtil.admin_ctx()

        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(adminCtx, {})
        self.assertEqual(str(e.exception),
            'data parameter field is required');

        with self.assertRaises(ValueError) as e:
            self.catalog.set_secure_config_params(adminCtx, {'data': "test"})
        self.assertEqual(str(e.exception),
            'data parameter field must be a list');

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(adminCtx, {})
        self.assertEqual(str(e.exception),
            'data parameter field is required');

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_secure_config_params(adminCtx, {'data': "test"})
        self.assertEqual(str(e.exception),
            'data parameter field must be a list');

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(adminCtx, {})
        self.assertEqual(str(e.exception),
            'module_name parameter field is required');

        with self.assertRaises(ValueError) as e:
            self.catalog.get_secure_config_params(adminCtx, {'module_name': [1, 2, 3]})
        self.assertEqual(str(e.exception),
            'module_name parameter field must be a string');


    def test_no_data(self):
        adminCtx = self.cUtil.admin_ctx()

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test0'})[0]
        self.assertEqual(len(params), 0)
        

    def test_set_parameters(self):
        adminCtx = self.cUtil.admin_ctx()
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test1',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value0'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test1'})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['module_name'], 'Test1')
        self.assertEqual(params[0]['param_name'], 'param0')
        self.assertEqual(params[0]['param_value'], 'value0')
        self.assertEqual(params[0]['version_tag'], '')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test1',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value1'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'Test1'})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_value'], 'value1')

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test1',
                                                                   'param_name': 'param2',
                                                                   'param_value': 'value2'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test1'})[0]
        self.assertEqual(len(params), 2)


    def test_remove_parameters(self):
        adminCtx = self.cUtil.admin_ctx()
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test2',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value0'},
                                                                  {'module_name': 'Test2',
                                                                   'param_name': 'param1',
                                                                   'param_value': 'value1'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test2'})[0]
        self.assertEqual(len(params), 2)

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': 'Test2',
                                                                      'param_name': 'param1'}]})

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test2'})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_name'], 'param0')
        self.assertEqual(params[0]['param_value'], 'value0')


    def test_versions(self):
        adminCtx = self.cUtil.admin_ctx()
        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                   'param_name': 'param0',
                                                                   'param_value': 'value0'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3'})[0]
        self.assertEqual(len(params), 1)

        self.catalog.set_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                   'param_name': 'param0',
                                                                   'version_tag': 'special_version',
                                                                   'param_value': 'value1'}]})
        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3'})[0]
        self.assertEqual(len(params), 2)

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                      'param_name': 'param0'}]})

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3'})[0]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]['param_name'], 'param0')
        self.assertEqual(params[0]['param_value'], 'value1')
        self.assertEqual(params[0]['version_tag'], 'special_version')

        self.catalog.remove_secure_config_params(adminCtx, {'data': [{'module_name': 'Test3',
                                                                      'param_name': 'param0',
                                                                      'version_tag': 'special_version'}]})

        params = self.catalog.get_secure_config_params(adminCtx, {'module_name': 'test3'})[0]
        self.assertEqual(len(params), 0)



    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING client_group_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        print('ready')

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




