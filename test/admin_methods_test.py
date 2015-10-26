

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


class AdminMethodsTest(unittest.TestCase):


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


    def test_migrate_module_to_new_git_url(self):

        params = {
            'module_name':"release_history",
            'current_git_url':"https://github.com/kbaseIncubator/release_history",
            'new_git_url':"https://github.com/kbase/release_history"
        }
        # first make sure we can find a module with this name and url
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':params['module_name'],
             'git_url':params['current_git_url']})[0]
        self.assertEqual(info['module_name'],params['module_name'])
        self.assertEqual(info['git_url'],params['current_git_url'])
        self.assertEqual(info['language'],'python')

        # next make sure we get an error if we are not an admin
        with self.assertRaises(ValueError):
            self.catalog.migrate_module_to_new_git_url(self.cUtil.user_ctx(),params)

        # if we are an admin, then it should work
        self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)

        # the old record should not be retrievable by that url anymore
        with self.assertRaises(ValueError):
            self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
                {'module_name':params['module_name'],
                 'git_url':params['current_git_url']})[0]
        # but the new url should work
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':params['module_name'],
             'git_url':params['new_git_url']})[0]
        self.assertEqual(info['module_name'],params['module_name'])
        self.assertEqual(info['git_url'],params['new_git_url'])
        self.assertEqual(info['language'],'python')

        # things should fail if we just try again
        with self.assertRaises(ValueError):
            self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)
        # or if the new url is not valid
        params['current_git_url'] = params['new_git_url']
        params['new_git_url'] = "http:not_a_url"
        with self.assertRaises(ValueError):
            self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)

        # but we should be able to switch back
        params['new_git_url'] = "https://github.com/kbaseIncubator/release_history"
        self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':params['module_name']})[0]
        self.assertEqual(info['module_name'],params['module_name'])
        self.assertEqual(info['git_url'],params['new_git_url'])
        self.assertEqual(info['language'],'python')




    @classmethod
    def setUpClass(cls):
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




