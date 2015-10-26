

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


# tests all the basic get methods
class DeveloperAddRemoveTest(unittest.TestCase):


    # assumes no developers have been added yet
    def test_add_remove_developers(self):

        # nothing there yet
        devs = self.catalog.list_approved_developers(self.cUtil.anonymous_ctx())[0]
        self.assertEqual(devs,[])
        is_approved = self.catalog.is_approved_developer([],self.cUtil.anonymous_ctx())[0]
        self.assertEqual(is_approved,[])
        is_approved = self.catalog.is_approved_developer(self.cUtil.anonymous_ctx(),
            ['somebody','otherperson'])[0]
        self.assertEqual(is_approved,[0l,0l])

        # add somebody fails without admin user
        with self.assertRaises(ValueError):
            self.catalog.approve_developer(self.cUtil.user_ctx(),'alice')
        with self.assertRaises(ValueError):
            # should fail if we specified something empty
            self.catalog.approve_developer(self.cUtil.admin_ctx(),' ')

        # add some users
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'eve')
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'alice')
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'bob')
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'bob') # should be able to add again without error
        devs = self.catalog.list_approved_developers(self.cUtil.anonymous_ctx())[0]
        self.assertEqual(devs,['alice','bob','eve']) # should be sorted
        is_approved = self.catalog.is_approved_developer(self.cUtil.anonymous_ctx(),
            ['somebody','alice','otherperson','bob','bob'])[0]
        self.assertEqual(is_approved,[0l,1l,0l,1l,1l])

        # remove some
        with self.assertRaises(ValueError):
            # should fail, only admins can revoke users
            self.catalog.revoke_developer(self.cUtil.user_ctx(),'alice')
        with self.assertRaises(ValueError):
            # should fail if we misspelled a name
            self.catalog.revoke_developer(self.cUtil.admin_ctx(),'b0b')
        with self.assertRaises(ValueError):
            # should fail if we specified something empty
            self.catalog.revoke_developer(self.cUtil.admin_ctx(),' ')
        self.catalog.revoke_developer(self.cUtil.admin_ctx(),'alice')

        # should have truncated list
        devs = self.catalog.list_approved_developers(self.cUtil.anonymous_ctx())[0]
        self.assertEqual(devs,['bob','eve']) # should be sorted
        is_approved = self.catalog.is_approved_developer(self.cUtil.anonymous_ctx(),
            ['somebody','alice','otherperson','bob','bob'])[0]
        self.assertEqual(is_approved,[0l,0l,0l,1l,1l])

        # should block registration for non-developers
        with self.assertRaises(ValueError):
            self.catalog.register_repo(self.cUtil.user_ctx(),
                {'git_url':'https://madeupurl.com'})

        # after the developer is added, should be allowed to start now (give a bogus url so if finishes registration
        # right away with an error
        self.catalog.approve_developer(self.cUtil.admin_ctx(),self.cUtil.test_user_1)
        self.catalog.register_repo(self.cUtil.user_ctx(),{'git_url':'https://madeupurl.com'})
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':'https://madeupurl.com'})[0]
            #pprint(state)
            if state['registration'] in ['complete','error']:
                break



    @classmethod
    def setUpClass(cls):
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




