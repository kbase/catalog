import unittest

from biokbase.catalog.Impl import Catalog
from catalog_test_util import CatalogTestUtil


# tests all the basic get methods
class BasicCatalogTest(unittest.TestCase):


    def test_basic_list_log(self):

        # limits to first 1000, hoping we don't have more than that for tests!
        full_build_list = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{})[0]

        # skip 5 and make sure that's what happened
        skip5 = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'skip':5})[0]
        self.assertEqual(len(full_build_list) - len(skip5), 5)
        self.assertEqual(full_build_list[5], skip5[0])
        self.assertEqual(full_build_list[-1], skip5[-1])

        # limit 2 and make sure that's what happened
        limit2 = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'limit':2})[0]
        self.assertEqual(len(limit2), 2)
        self.assertEqual(full_build_list[1], limit2[1])

        # do both
        skip3limit2 = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'skip':3, 'limit':2})[0]
        self.assertEqual(len(skip3limit2), 2)
        self.assertEqual(full_build_list[3], skip3limit2[0])

        # only in progress
        running = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'only_running':1})[0]
        self.assertTrue(len(running)>0)
        self.assertTrue(len(full_build_list) > len(running))
        for b in running:
            self.assertNotEqual(b['registration'],'complete')
            self.assertNotEqual(b['registration'],'error')

        # only complete
        complete = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'only_complete':1})[0]
        self.assertTrue(len(complete)>0)
        self.assertTrue(len(full_build_list) > len(complete))
        for b in complete:
            self.assertEqual(b['registration'],'complete')

        # only error
        error = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'only_error':1})[0]
        self.assertTrue(len(error)>0)
        self.assertTrue(len(full_build_list) > len(error))
        for b in error:
            self.assertEqual(b['registration'],'error')

        # only complete, with some limits
        complete_skip2limit1 = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'only_complete':1, 'skip':2, 'limit':1})[0]
        self.assertEqual(len(complete_skip2limit1),1)
        self.assertEqual(complete[2], complete_skip2limit1[0])

        # get specific module => TODO: doesn't quite behave how you expect when passing multiple modules with mixed git urls and module names
        module_builds = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'modules': [{'module_name':'onerepotest'},
            {'module_name':'registration_in_progress'}] })[0]
        self.assertEqual(len(module_builds),5)



    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING build_log_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




