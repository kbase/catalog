

import unittest
import os

from pprint import pprint
from time import time

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog
from biokbase.narrative_method_store.client import NarrativeMethodStore


# tests all the basic get methods
class CoreRegistrationTest(unittest.TestCase):


    # assumes no developers have been added yet
    def test_full_module_lifecycle(self):

        # TODO: figure out git_commit hash or branch configuration
        # assume test user is already approved as a developer
        # (1) register the test repo
        giturl = self.cUtil.get_test_repo_1()
        githash = '4ada53f318f69a38276e82d0e841e685aa0c2362' # branch simple_good_repo
        timestamp = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash})[0]

        # (2) check state until error or complete, must be complete, and make sure this was relatively fast
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),timestamp)
        self.assertTrue(log is not None)

        # (3) get module info
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
        module_name = info['module_name']
        owners = [self.cUtil.user_ctx()['user_id']]
        self.assertIsNone(info['beta'])
        self.assertIsNone(info['release'])
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash)
        self.assertEqual(info['dev']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['timestamp'],timestamp)
        self.assertEqual(info['dev']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)

        # the method should appear in the NMS under the dev tag
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS')
        # but should not appear under beta or release
        method_list = self.nms.list_methods({'tag':'beta'})
        methMissing = True
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                methMissing = False
        self.assertTrue(methMissing,'Make sure we did not find the method in NMS under the beta tag')
        # but should not appear under beta or release
        method_list = self.nms.list_methods({'tag':'release'})
        methMissing = True
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                methMissing = False
        self.assertTrue(methMissing,'Make sure we did not find the method in NMS under the release tag')


        #(4) update beta
        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),{'module_name':module_name})
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertIsNone(info['release'])
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash)
        self.assertEqual(info['dev']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['timestamp'],timestamp)

        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)
        self.assertEqual(info['beta']['git_commit_hash'],githash)
        self.assertEqual(info['beta']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['beta']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['timestamp'],timestamp)
        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)

        # the method should appear in the NMS under the dev or beta tag
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS')
        # but should not appear under beta or release
        method_list = self.nms.list_methods({'tag':'beta'})
        foundMeth = False
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS under the beta tag')
        # but should not appear under beta or release
        method_list = self.nms.list_methods({'tag':'release'})
        methMissing = True
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                methMissing = False
        self.assertTrue(methMissing,'Make sure we did not find the method in NMS under the release tag')


        #(5) request release
        self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})

        #(6) list requested releases, admin rejects release
        releases = self.catalog.list_requested_releases(self.cUtil.anonymous_ctx())[0]
        found = False
        for r in releases:
            if r['git_commit_hash'] == githash:
                found=True
                self.assertEqual(r['module_name'],module_name)
                self.assertEqual(r['timestamp'],timestamp)
                self.assertEqual(r['owners'],[self.cUtil.user_ctx()['user_id']])
        self.assertTrue(found,'found new release request in list of release requests')
        self.catalog.review_release_request(self.cUtil.admin_ctx(),
                        {'module_name':module_name, 'decision':'denied', 'review_message':'ask later'})
        releases = self.catalog.list_requested_releases(self.cUtil.anonymous_ctx())[0]
        found = False
        for r in releases:
            if r['git_commit_hash'] == githash:
                found=True
        self.assertFalse(found,'found new release request that should have been removed')
        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertEqual(state['released'],0)
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['release_approval'],'denied')
        self.assertEqual(state['review_message'],'ask later')

        #(7) ask again, this time admin accepts
        self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})
        releases = self.catalog.list_requested_releases(self.cUtil.anonymous_ctx())[0]
        found = False
        for r in releases:
            if r['git_commit_hash'] == githash:
                found=True
                self.assertEqual(r['module_name'],module_name)
                self.assertEqual(r['timestamp'],timestamp)
                self.assertEqual(r['owners'],[self.cUtil.user_ctx()['user_id']])
        self.assertTrue(found,'found new release request in list of release requests')
        self.catalog.review_release_request(self.cUtil.admin_ctx(),
                        {'module_name':module_name, 'decision':'approved'})
        releases = self.catalog.list_requested_releases(self.cUtil.anonymous_ctx())[0]
        found = False
        for r in releases:
            if r['git_commit_hash'] == githash:
                found=True
        self.assertFalse(found,'found new release request that should have been removed')
        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertEqual(state['released'],1)
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['release_approval'],'approved')
        self.assertEqual(state['review_message'],'')

        #(8) release appears in release, and in release versions
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash)
        self.assertEqual(info['dev']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['timestamp'],timestamp)

        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)
        self.assertEqual(info['beta']['git_commit_hash'],githash)
        self.assertEqual(info['beta']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['beta']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['timestamp'],timestamp)
        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)

        self.assertEqual(info['release']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)
        self.assertEqual(info['release']['git_commit_hash'],githash)
        self.assertEqual(info['release']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['release']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['release']['version'],'0.0.1')
        self.assertEqual(info['release']['timestamp'],timestamp)
        self.assertEqual(info['release']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)

        versions = self.catalog.list_released_module_versions(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertEqual(len(versions),1)

        self.assertEqual(versions[0]['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)
        self.assertEqual(versions[0]['git_commit_hash'],githash)
        self.assertEqual(versions[0]['git_commit_message'],'added some basic things\n')
        self.assertEqual(versions[0]['narrative_methods'],['test_method_1'])
        self.assertEqual(versions[0]['version'],'0.0.1')
        self.assertEqual(versions[0]['timestamp'],timestamp)
        self.assertEqual(versions[0]['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)

        # the method should appear in the NMS under the dev/beta/release
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS')
        # but should not appear under beta or release
        method_list = self.nms.list_methods({'tag':'beta'})
        foundMeth = False
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS under the beta tag')
        # but should not appear under beta or release
        method_list = self.nms.list_methods({'tag':'release'})
        foundMeth = False
        for meth in method_list:
            if meth['id']==module_name+'/test_method_1' and meth['namespace']==module_name:
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS under the release tag')


        #(9) register again, dev is updated, beta and release are not
        githash2 = '599d796c6b7c30a47b3a8a496346d8f49c29a064' # branch simple_good_repo
        timestamp2 = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash2})[0]
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build 2 exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),timestamp2)
        self.assertTrue(log is not None)

        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash2)
        self.assertEqual(info['dev']['git_commit_message'],'added new method\n')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1','test_method_2'])
        self.assertEqual(info['dev']['version'],'0.0.2')
        self.assertEqual(info['dev']['timestamp'],timestamp2)

        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)
        self.assertEqual(info['beta']['git_commit_hash'],githash)
        self.assertEqual(info['beta']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['beta']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['timestamp'],timestamp)
        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)

        self.assertEqual(info['release']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)
        self.assertEqual(info['release']['git_commit_hash'],githash)
        self.assertEqual(info['release']['git_commit_message'],'added some basic things\n')
        self.assertEqual(info['release']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['release']['version'],'0.0.1')
        self.assertEqual(info['release']['timestamp'],timestamp)
        self.assertEqual(info['release']['docker_img_name'].split('/')[1],module_name.lower()+':'+githash)



    def test_module_with_bad_spec(self):

        # (1) register the test repo
        giturl = self.cUtil.get_test_repo_1()
        githash = 'ca3d7ae05af24cd1c5d21ec9e0e4c52c52695300' # branch fail_method_spec_1
        timestamp = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash})[0]

        # (2) check state until error or complete, must be error, and make sure this was relatively fast
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'error')
        self.assertTrue('Invalid narrative method specification (test_method_2)' in state['error_message'])
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),timestamp)[0]
        self.assertTrue(log is not None)
        self.assertTrue('param0_that_is_not_defined_in_yaml' in log)


    def validate_basic_test_module_info_fields(self,info,giturl,module_name,owners):
        self.assertEqual(info['git_url'],giturl)
        self.assertEqual(info['module_name'],module_name)
        self.assertEqual(info['owners'],owners)
        self.assertEqual(info['language'],'python')
        self.assertEqual(info['description'],'A test module')

#{'beta': None,
# 'description': u'A test module',
# 'dev': {u'git_commit_hash': u'4ada53f318f69a38276e82d0e841e685aa0c2362',
#         u'git_commit_message': u'added some basic things\n',
#         u'narrative_methods': [u'test_method_1'],
#         u'timestamp': 1445888811416L,
#         u'version': u'0.0.1'},
# 'git_url': u'https://github.com/kbaseIncubator/catalog_test_module',
# 'language': u'python',
# 'module_name': u'CatalogTestModule',
# 'owners': [u'wstester1'],
# 'release': None}




    @classmethod
    def setUpClass(cls):

        # hack for testing!! remove when docker and NMS components can be tested
        from biokbase.catalog.registrar import Registrar
        Registrar._TEST_WITHOUT_DOCKER = True

        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        # approve developers we will use
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(),cls.cUtil.admin_ctx()['user_id'])
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(),cls.cUtil.user_ctx()['user_id'])

        cls.nms = NarrativeMethodStore(cls.cUtil.getCatalogConfig()['nms-url'])

        

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




