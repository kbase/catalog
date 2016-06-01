

import unittest
import os

from pprint import pprint
from time import time, sleep

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog
from biokbase.narrative_method_store.client import NarrativeMethodStore


# tests all the basic get methods
class RegistrationErrorTests(unittest.TestCase):


    def test_registration_error(self):

        giturl = self.cUtil.get_test_repo_1()
        githash = '4ada53f318f69a38276e82d0e841e685aa0c2362' # branch simple_good_repo

        # no git url provided, needs to fail
        with self.assertRaises(ValueError) as e:
            registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
                {'git_commit_hash':githash})[0]
        self.assertEqual(str(e.exception),
            'git_url not defined, but is required for registering a repository');

        # git url provided is not a url, needs to fail
        with self.assertRaises(ValueError) as e:
            registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
                {'git_url': 'not_a_url', 'git_commit_hash':githash})[0]
        self.assertEqual(str(e.exception),
            'The git url provided is not a valid URL.');

        # cannot register an inactive module
        with self.assertRaises(ValueError) as e:
            registration_id = self.catalog.register_repo({'user_id':'bad_user', 'token':'abc'},
                {'git_url': 'https://github.com/kbaseIncubator/pending_Release'})[0]
        self.assertEqual(str(e.exception),
            'You (bad_user) are an approved developer, but do not have permission to register this repo (https://github.com/kbaseIncubator/pending_Release)');

        # cannot register an inactive module
        with self.assertRaises(ValueError) as e:
            registration_id = self.catalog.register_repo({'user_id':'bad_user', 'token':'abc'},
                {'git_url': 'https://github.com/kbaseIncubator/pending_Release'})[0]
        self.assertEqual(str(e.exception),
            'You (bad_user) are an approved developer, but do not have permission to register this repo (https://github.com/kbaseIncubator/pending_Release)');

        # start a registration, try to register again should fail
        with self.assertRaises(ValueError) as e:
            registration_id = self.catalog.register_repo({'user_id':'wstester1', 'token':'abc'},
                {'git_url':'https://github.com/kbaseIncubator/registration_in_progress', 'git_commit_hash':githash})[0]
        self.assertEqual(str(e.exception),
            'Registration already in progress for this git repo (https://github.com/kbaseIncubator/registration_in_progress)');


    def test_release_errors(self):
        giturl = self.cUtil.get_test_repo_1()
        githash = '4ada53f318f69a38276e82d0e841e685aa0c2362' # branch simple_good_repo

        # can't push dev to beta if you aint a developer
        with self.assertRaises(ValueError) as e:
            self.catalog.push_dev_to_beta({'user_id':'some_usr','token':''}, 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'You are not an approved developer.  Contact us to request approval.');

        # can't push dev to beta if you aint an owner
        with self.assertRaises(ValueError) as e:
            self.catalog.push_dev_to_beta({'user_id':'bad_user','token':'asf'}, 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'You do not have permission to modify this module/repo.');

        # can't push dev to beta if it aint active
        with self.assertRaises(ValueError) as e:
            self.catalog.push_dev_to_beta({'user_id':'wstester1','token':'asf'}, 
                {'module_name':'inactive_module'})
        self.assertEqual(str(e.exception),
            'Cannot push dev to beta- module/repo is no longer active.');

        # can't push dev to beta if it has already been requested
        with self.assertRaises(ValueError) as e:
            self.catalog.push_dev_to_beta({'user_id':'kbasetest','token':'asf'}, 
                {'module_name':'pending_first_release'})
        self.assertEqual(str(e.exception),
            'Cannot push dev to beta- last release request of beta is still pending.');

        # can't request_release if you aint a developer
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release({'user_id':'some_usr','token':''}, 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'You are not an approved developer.  Contact us to request approval.');

        # can't request_release if you aint an owner
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release({'user_id':'bad_user','token':'asf'}, 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'You do not have permission to modify this module/repo.');

        # can't request_release if it aint active
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release({'user_id':'wstester1','token':'asf'}, 
                {'module_name':'inactive_module'})
        self.assertEqual(str(e.exception),
            'Cannot request release - module/repo is no longer active.');

        # can't request_release if it has already been requested
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release({'user_id':'kbasetest','token':'asf'}, 
                {'module_name':'pending_first_release'})
        self.assertEqual(str(e.exception),
            'Cannot request release - last release request of beta is still pending.');

       # can't request_release if it has no beta version
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release({'user_id':'kbasetest','token':'asf'}, 
                {'module_name':'pending_first_release'})
        self.assertEqual(str(e.exception),
            'Cannot request release - last release request of beta is still pending.');


    
    def test_release_review(self): 

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request({'user_id':'some_usr','token':''}, 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'You do not have permission to review a release request.');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'Cannot review request - module/repo is not under review!');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'release_history'})
        self.assertEqual(str(e.exception),
            'Cannot review request - module/repo is not under review!');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'pending_first_release'})
        self.assertEqual(str(e.exception),
            'Cannot set review - no "decision" was provided!');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'pending_first_release', 'decision':None})
        self.assertEqual(str(e.exception),
            'Cannot set review - no "decision" was provided!');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'pending_first_release', 'decision':'no decision'})
        self.assertEqual(str(e.exception),
            'Cannot set review - decision must be "approved" or "denied"');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'pending_first_release', 'decision':'denied'})
        self.assertEqual(str(e.exception),
            'Cannot set review - if denied, you must set a "review_message"!');

        with self.assertRaises(ValueError) as e:
            self.catalog.review_release_request(self.cUtil.admin_ctx(), 
                {'module_name':'pending_first_release', 'decision':'denied', 'review_message':''})
        self.assertEqual(str(e.exception),
            'Cannot set review - if denied, you must set a "review_message"!');


    @classmethod
    def setUpClass(cls):

        print('++++++++++++ RUNNING registration_error_tests.py +++++++++++')

        # hack for testing!! remove when docker and NMS components can be tested
        from biokbase.catalog.registrar import Registrar
        Registrar._TEST_WITHOUT_DOCKER = True

        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        # approve developers we will use
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(),'bad_user')
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(),'kbasetest')
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(),cls.cUtil.admin_ctx()['user_id'])
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(),cls.cUtil.user_ctx()['user_id'])

        cls.nms = NarrativeMethodStore(cls.cUtil.getCatalogConfig()['nms-url'])

        

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




