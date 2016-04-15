

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


# tests all the basic get methods
class DynamicServiceSupportTest(unittest.TestCase):


    def test_list_dynamic_modules(self):

        # first fetch without a tag, we should get all released versions
        mods = self.catalog.list_service_modules(self.cUtil.anonymous_ctx(),
            {})[0]
        mods.sort(key = lambda x: x['version'])
        self.assertEqual(len(mods),4)

        self.assertEqual(mods[0]['module_name'],'DynamicService')
        self.assertEqual(mods[0]['git_commit_hash'],'9bedf67800b2923982bdf60c89c57ce6fd2d9a1c')
        self.assertEqual(mods[0]['version'],'1.0.1')
        self.assertEqual(mods[0]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice.9bedf67800b2923982bdf60c89c57ce6fd2d9a1c')

        self.assertEqual(mods[1]['module_name'],'DynamicService')
        self.assertEqual(mods[1]['git_commit_hash'],'12edf67800b2923982bdf60c89c57ce6fd2d9a1c')
        self.assertEqual(mods[1]['version'],'1.0.2')
        self.assertEqual(mods[1]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice.12edf67800b2923982bdf60c89c57ce6fd2d9a1c')

        self.assertEqual(mods[2]['module_name'],'DynamicService2')
        self.assertEqual(mods[2]['git_commit_hash'],'29dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(mods[2]['version'],'1.5.0')
        self.assertEqual(mods[2]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice2.29dc505febb8f4cccb2078c58ded0de3320534d7')

        self.assertEqual(mods[3]['module_name'],'DynamicService')
        self.assertEqual(mods[3]['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(mods[3]['version'],'2.1.8')
        self.assertEqual(mods[3]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice.49dc505febb8f4cccb2078c58ded0de3320534d7')
        
        # get all dev services
        mods = self.catalog.list_service_modules(self.cUtil.anonymous_ctx(),
            {'tag':'dev'})[0]
        self.assertEqual(len(mods),1)
        self.assertEqual(mods[0]['module_name'],'DynamicService')
        self.assertEqual(mods[0]['git_commit_hash'],'b06c5f9daf603a4d206071787c3f6184000bf128')
        self.assertEqual(mods[0]['version'],'0.0.5')
        self.assertEqual(mods[0]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice.b06c5f9daf603a4d206071787c3f6184000bf128')


        # get all beta services
        mods = self.catalog.list_service_modules(self.cUtil.anonymous_ctx(),
            {'tag':'beta'})[0]
        mods.sort(key = lambda x: x['version'])
        self.assertEqual(len(mods),1)
        self.assertEqual(mods[0]['module_name'],'DynamicService2')
        self.assertEqual(mods[0]['git_commit_hash'],'39dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(mods[0]['version'],'1.5.1')
        self.assertEqual(mods[0]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice2.39dc505febb8f4cccb2078c58ded0de3320534d7')


        # get all released versions
        mods = self.catalog.list_service_modules(self.cUtil.anonymous_ctx(),
            {'tag':'release'})[0]
        mods.sort(key = lambda x: x['version'])
        self.assertEqual(len(mods),2)

        self.assertEqual(mods[0]['module_name'],'DynamicService2')
        self.assertEqual(mods[0]['git_commit_hash'],'29dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(mods[0]['version'],'1.5.0')
        self.assertEqual(mods[0]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice2.29dc505febb8f4cccb2078c58ded0de3320534d7')


        self.assertEqual(mods[1]['module_name'],'DynamicService')
        self.assertEqual(mods[1]['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(mods[1]['version'],'2.1.8')
        self.assertEqual(mods[1]['docker_img_name'],'dockerhub-ci.kbase.us/kbase:dynamicservice.49dc505febb8f4cccb2078c58ded0de3320534d7')


        # make sure bad tag throws an error
        with self.assertRaises(ValueError) as e:
            self.catalog.list_service_modules(self.cUtil.anonymous_ctx(),
                {'tag':'badtag'})[0]
        self.assertEqual(str(e.exception),
            'tag parameter must be either "dev", "beta", or "release".');



    def test_version_fetch_basics(self):

        # without args should throw an error
        with self.assertRaises(ValueError) as e:
            self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {})[0]
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');

        # no version given should give last released version
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService'})[0]
        self.assertEqual(ver['module_name'],'DynamicService')
        self.assertEqual(ver['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(ver['version'],'2.1.8')

        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService2'})[0]
        self.assertEqual(ver['module_name'],'DynamicService2')
        self.assertEqual(ver['git_commit_hash'],'29dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(ver['version'],'1.5.0')

        # dev works
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService', 'lookup':'dev'})[0]
        self.assertEqual(ver['module_name'],'DynamicService')
        self.assertEqual(ver['git_commit_hash'],'b06c5f9daf603a4d206071787c3f6184000bf128')
        self.assertEqual(ver['version'],'0.0.5')

        # if dev is not a dynamic service, will fail
        with self.assertRaises(ValueError) as e:
            ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService2', 'lookup':'dev'})[0]
        self.assertEqual(str(e.exception),
            'The "dev" version is not marked as a Service Module.');

        # same thing for beta
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService2', 'lookup':'beta'})[0]
        self.assertEqual(ver['module_name'],'DynamicService2')
        self.assertEqual(ver['git_commit_hash'],'39dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(ver['version'],'1.5.1')

        # if dev is not a dynamic service, will fail
        with self.assertRaises(ValueError) as e:
            ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService', 'lookup':'beta'})[0]
        self.assertEqual(str(e.exception),
            'The "beta" version is not marked as a Service Module.');

        # release works
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService','lookup':'release'})[0]
        self.assertEqual(ver['module_name'],'DynamicService')
        self.assertEqual(ver['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(ver['version'],'2.1.8')

        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService2','lookup':'release'})[0]
        self.assertEqual(ver['module_name'],'DynamicService2')
        self.assertEqual(ver['git_commit_hash'],'29dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(ver['version'],'1.5.0')


        # now the interesting part, getting things by semantic version
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService2','lookup':'==1.5.0'})[0]
        self.assertEqual(ver['version'],'1.5.0')

        with self.assertRaises(ValueError) as e:
            ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService2', 'lookup':'==1.5.1'})[0]
        self.assertEqual(str(e.exception),
            'No suitable version matches your lookup.');

        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService','lookup':'>=1.0.0,<2.0.0'})[0]
        self.assertEqual(ver['version'],'1.0.2')
        self.assertEqual(ver['git_commit_hash'],'12edf67800b2923982bdf60c89c57ce6fd2d9a1c')
        self.assertEqual(ver['module_name'],'DynamicService')

        # if we want a non-service version, we should get the higher bump
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService','lookup':'>=1.0.0,<2.0.0','only_service_versions':1})[0]
        self.assertEqual(ver['version'],'1.0.2')
        self.assertEqual(ver['git_commit_hash'],'12edf67800b2923982bdf60c89c57ce6fd2d9a1c')
        self.assertEqual(ver['module_name'],'DynamicService')
        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService','lookup':'>=1.0.0,<2.0.0','only_service_versions':0})[0]
        self.assertEqual(ver['version'],'1.1.0')
        self.assertEqual(ver['git_commit_hash'],'d6cd1e2bd19e03a81132a23b2025920577f84e37')
        self.assertEqual(ver['module_name'],'DynamicService')

        ver = self.catalog.module_version_lookup(self.cUtil.anonymous_ctx(),
                {'module_name':'DynamicService','lookup':'>2.0.0'})[0]
        self.assertEqual(ver['version'],'2.1.8')
        self.assertEqual(ver['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(ver['module_name'],'DynamicService')
    


    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING version_fetch_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




