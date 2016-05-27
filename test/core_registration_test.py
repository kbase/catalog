

import unittest
import os

from pprint import pprint
from time import time, sleep

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
        registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash})[0]
        timestamp = int(registration_id.split('_')[0])

        # (2) check state until error or complete, must be complete, and make sure this was relatively fast
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                pprint(state)
                break
            self.assertTrue(time()-start < timeout, 'simple registration build exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')

        # (3) check the log
        parsed_log = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {'registration_id':registration_id})[0]
        self.assertEqual(parsed_log['registration'],'complete')
        self.assertEqual(parsed_log['registration_id'],registration_id)
        self.assertEqual(parsed_log['git_url'],giturl)
        self.assertEqual(parsed_log['error_message'],'')
        self.assertIsNotNone(parsed_log['module_name_lc'])
        self.assertTrue(len(parsed_log['log'])>0)

        # get the log file directly
        raw_log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),registration_id)[0]
        self.assertTrue(raw_log is not None)

        log_lines = raw_log.splitlines();
        self.assertTrue(log_lines, parsed_log['log'])

        # check getting specific lines
        parsed_log_subset = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {
                                'registration_id':registration_id, 
                                'first_n':5 
                            })[0]
        self.assertEqual(len(parsed_log_subset['log']),5)
        self.assertEqual(parsed_log['log'][0],parsed_log_subset['log'][0])
        self.assertEqual(parsed_log['log'][1],parsed_log_subset['log'][1])
        self.assertEqual(parsed_log['log'][2],parsed_log_subset['log'][2])
        self.assertEqual(parsed_log['log'][3],parsed_log_subset['log'][3])
        self.assertEqual(parsed_log['log'][4],parsed_log_subset['log'][4])

        parsed_log_subset = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {
                                'registration_id':registration_id, 
                                'last_n':5 
                            })[0]
        self.assertEqual(len(parsed_log_subset['log']),5)
        self.assertEqual(parsed_log['log'][-1],parsed_log_subset['log'][4])
        self.assertEqual(parsed_log['log'][-2],parsed_log_subset['log'][3])
        self.assertEqual(parsed_log['log'][-3],parsed_log_subset['log'][2])
        self.assertEqual(parsed_log['log'][-4],parsed_log_subset['log'][1])
        self.assertEqual(parsed_log['log'][-5],parsed_log_subset['log'][0])

        parsed_log_subset = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {
                                'registration_id':registration_id, 
                                'skip':4,
                                'limit':2 
                            })[0]
        self.assertEqual(len(parsed_log_subset['log']),2)
        self.assertEqual(parsed_log['log'][4],parsed_log_subset['log'][0])
        self.assertEqual(parsed_log['log'][5],parsed_log_subset['log'][1])

        # should show up as the top hit when we list logs
        recent_build_list = self.catalog.list_builds(self.cUtil.anonymous_ctx(),{'limit':6})[0]

        self.assertEqual(len(recent_build_list),6)
        self.assertEqual(recent_build_list[0]['registration_id'],registration_id)
        self.assertEqual(recent_build_list[0]['registration'],'complete')
        self.assertEqual(recent_build_list[0]['error_message'],'')
        self.assertIsNotNone(recent_build_list[0]['module_name_lc'])
        self.assertEqual(recent_build_list[0]['git_url'],giturl)

        # check some bad parameters
        with self.assertRaises(ValueError) as e:
            parsed_log_subset = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {'registration_id':registration_id, 'skip':4 })[0]
        self.assertEqual(str(e.exception),
            'Cannot specify the skip argument without a limit- blame Mongo');
        with self.assertRaises(ValueError) as e:
            parsed_log_subset = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {'registration_id':registration_id, 'first_n':4, 'last_n':2 })[0]
        self.assertEqual(str(e.exception),
            'Cannot combine skip/limit/first_n with last_n parameters');

        # (3) get module info
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
        module_name = info['module_name']
        owners = [self.cUtil.user_ctx()['user_id']]
        self.assertIsNone(info['beta'])
        self.assertIsNone(info['release'])
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash)
        self.assertEqual(info['dev']['git_commit_message'],'added some basic things')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['timestamp'],timestamp)
        self.assertEqual(info['dev']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

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

        #(3b) registration again should work
        registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash})[0]
        timestamp = int(registration_id.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                pprint(state)
                break
            self.assertTrue(time()-start < timeout, 'simple registration build exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')

        #(4) update beta
        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),{'module_name':module_name})
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertIsNone(info['release'])
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash)
        self.assertEqual(info['dev']['git_commit_message'],'added some basic things')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['timestamp'],timestamp)

        self.assertEqual(info['beta']['docker_img_name'].split('/')[1], 'kbase:' + module_name.lower()+'.'+githash)
        self.assertEqual(info['beta']['git_commit_hash'],githash)
        self.assertEqual(info['beta']['git_commit_message'],'added some basic things')
        self.assertEqual(info['beta']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['timestamp'],timestamp)

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
        self.assertEqual(info['dev']['git_commit_message'],'added some basic things')
        self.assertEqual(info['dev']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['timestamp'],timestamp)
        self.assertEqual(info['dev']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

        self.assertEqual(info['beta']['git_commit_hash'],githash)
        self.assertEqual(info['beta']['git_commit_message'],'added some basic things')
        self.assertEqual(info['beta']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['timestamp'],timestamp)
        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

        self.assertEqual(info['release']['git_commit_hash'],githash)
        self.assertEqual(info['release']['git_commit_message'],'added some basic things')
        self.assertEqual(info['release']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['release']['version'],'0.0.1')
        self.assertEqual(info['release']['timestamp'],timestamp)
        self.assertTrue(info['release']['release_timestamp']>info['release']['timestamp']);
        self.assertEqual(info['release']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

        versions = self.catalog.list_released_module_versions(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertEqual(len(versions),1)

        self.assertEqual(versions[0]['git_commit_hash'],githash)
        self.assertEqual(versions[0]['git_commit_message'],'added some basic things')
        self.assertEqual(versions[0]['narrative_methods'],['test_method_1'])
        self.assertEqual(versions[0]['version'],'0.0.1')
        self.assertEqual(versions[0]['timestamp'],timestamp)
        self.assertEqual(versions[0]['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

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
        registration_id2 = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash2})[0]
        timestamp2 = int(registration_id2.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build 2 exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),registration_id2)
        self.assertTrue(log is not None)

        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.validate_basic_test_module_info_fields(info,giturl,module_name,owners)
        self.assertEqual(info['dev']['git_commit_hash'],githash2)
        self.assertEqual(info['dev']['git_commit_message'],'added new method')
        self.assertEqual(sorted(info['dev']['narrative_methods']),sorted(['test_method_1','test_method_2']))
        self.assertEqual(info['dev']['version'],'0.0.2')
        self.assertEqual(info['dev']['timestamp'],timestamp2)
        self.assertEqual(info['dev']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash2)

        self.assertEqual(info['beta']['git_commit_hash'],githash)
        self.assertEqual(info['beta']['git_commit_message'],'added some basic things')
        self.assertEqual(info['beta']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['timestamp'],timestamp)
        self.assertEqual(info['beta']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

        self.assertEqual(info['release']['git_commit_hash'],githash)
        self.assertEqual(info['release']['git_commit_message'],'added some basic things')
        self.assertEqual(info['release']['narrative_methods'],['test_method_1'])
        self.assertEqual(info['release']['version'],'0.0.1')
        self.assertEqual(info['release']['timestamp'],timestamp)
        self.assertEqual(info['release']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash)

        # assert fail on request release because you can't update release version if they are the same
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})
        self.assertEqual(str(e.exception),
            'Cannot request release - beta version is identical to released version.')


        # 10) migrate dev to beta again, release it.  Should work. 
        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),{'module_name':module_name})
        self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})
        self.catalog.review_release_request(self.cUtil.admin_ctx(),
                        {'module_name':module_name, 'decision':'approved'})
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertEqual(info['release']['git_commit_hash'],githash2)
        self.assertEqual(info['release']['git_commit_message'],'added new method')
        self.assertEqual(sorted(info['release']['narrative_methods']),sorted(['test_method_1','test_method_2']))
        self.assertEqual(info['release']['version'],'0.0.2')
        self.assertEqual(info['release']['timestamp'],timestamp2)
        self.assertTrue(info['release']['release_timestamp']>timestamp2)
        self.assertEqual(info['release']['docker_img_name'].split('/')[1],'kbase:' + module_name.lower()+'.'+githash2)

        # 11) register new version, but with bad version number.  Should fail.  Needs to be a semantic version
        githash3 = '9908c20cd5d275190490d7b852f22e5da73f9260' # branch simple_good_repo
        registration_id3 = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash3})[0]
        timestamp3 = int(registration_id3.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build 3 exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'error')
        sleep(3) # sleep to make sure the catalog db gets the final log messages
        log = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),{'registration_id':registration_id3})
        self.assertTrue(log is not None)
        found_correct_error = False
        for l in log:
            if 'must be in semantic version format' in l['error_message']:
                found_correct_error = True
        self.assertTrue(found_correct_error, 'correct error was thrown in log for semantic version error')

        #Register new version, but with same version number as in the release so should fail
        githash4 = '6add31077a4982d6c8a5bc161915d30bfec3fe0c' # branch simple_good_repo
        registration_id4 = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash4})[0]
        timestamp4 = int(registration_id4.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build 4 exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),registration_id4)
        self.assertTrue(log is not None)

        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),{'module_name':module_name})
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})
        self.assertEqual(str(e.exception),
            'Cannot request release - beta version has same version number to released version.')

        # Try once again but with a version number that is less than the current release version
        githash5 = '7627fa25e75515316407577e5578c2cb120ca40f' # branch simple_good_repo
        registration_id5 = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash5})[0]
        timestamp5 = int(registration_id5.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build 5 exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),registration_id5)
        self.assertTrue(log is not None)

        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),{'module_name':module_name})
        with self.assertRaises(ValueError) as e:
            self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})
        self.assertEqual(str(e.exception),
            'Cannot request release - beta semantic version (0.0.1) must be greater than the released semantic version 0.0.2, as determined by http://semver.org')


        # Register with a proper version number and indicate it is a dynamic service now
        githash6 = '026fd0421a03f12c78fb5dbffbbaa04a254fcbe7' # branch simple_good_repo
        registration_id6 = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash6})[0]
        timestamp6 = int(registration_id6.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build 5 exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),registration_id6)
        self.assertTrue(log is not None)

        self.catalog.push_dev_to_beta(self.cUtil.user_ctx(),{'module_name':module_name})

        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.catalog.request_release(self.cUtil.user_ctx(),{'module_name':info['module_name']})
        self.catalog.review_release_request(self.cUtil.admin_ctx(),
                        {'module_name':module_name, 'decision':'approved'})
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),{'module_name':module_name})[0]
        self.assertEqual(info['release']['git_commit_hash'],githash6)
        self.assertEqual(info['release']['version'],'1.0.1')
        self.assertEqual(info['release']['timestamp'],timestamp6)
        self.assertTrue(info['release']['release_timestamp']>timestamp6)
        self.assertTrue('dynamic_service' in info['release'])
        self.assertTrue(info['release']['dynamic_service'])


        # TODO test method store to be sure we can get old method specs by commit hash
        #pprint(info)


    def validate_basic_test_module_info_fields(self,info,giturl,module_name,owners):
        self.assertEqual(info['git_url'],giturl)
        self.assertEqual(info['module_name'],module_name)
        self.assertEqual(info['owners'],owners)
        self.assertEqual(info['language'],'python')
        self.assertEqual(info['description'],'A test module')

#{'beta': None,
# 'description': u'A test module',
# 'dev': {u'git_commit_hash': u'4ada53f318f69a38276e82d0e841e685aa0c2362',
#         u'git_commit_message': u'added some basic things',
#         u'narrative_methods': [u'test_method_1'],
#         u'timestamp': 1445888811416L,
#         u'version': u'0.0.1'},
# 'git_url': u'https://github.com/kbaseIncubator/catalog_test_module',
# 'language': u'python',
# 'module_name': u'CatalogTestModule',
# 'owners': [u'wstester1'],
# 'release': None}


    def test_module_with_bad_spec(self):

        # (1) register the test repo
        giturl = self.cUtil.get_test_repo_1()
        githash = 'ca3d7ae05af24cd1c5d21ec9e0e4c52c52695300' # branch fail_method_spec_1
        registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
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
        log = self.catalog.get_build_log(self.cUtil.anonymous_ctx(),registration_id)[0]
        self.assertTrue(log is not None)
        self.assertTrue('param0_that_is_not_defined_in_yaml' in log)



    def test_active_inactive_remove_module(self):

        # we cannot delete modules unles we are an admin user
        with self.assertRaises(ValueError) as e:
            self.catalog.delete_module(self.cUtil.user_ctx(),
                {'module_name':'registration_error'})
        self.assertEqual(str(e.exception),
            'Only Admin users can delete modules.');

        method_list = self.nms.list_methods({'tag':'dev'})

        # this should work: register a repo, make sure it appears
        giturl = self.cUtil.get_test_repo_2()
        githash = 'a2b66a4668548bbabc54ee937ac91f9237874a96' # branch simple_good_repo2 

        registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash})[0]
        timestamp = int(registration_id.split('_')[0])
        start = time()
        timeout = 60 #seconds
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]
            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build exceeded timeout of '+str(timeout)+'s')
        self.assertEqual(state['registration'],'complete')

        self.assertEqual(self.catalog.is_registered({},{'module_name':'CatalogTestModule2'})[0],1)
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']=='CatalogTestModule2/test_method_1' and meth['namespace']=='CatalogTestModule2':
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS')


        # next make sure we get an error if we are not an admin if we try to make the repo active or inactive
        params = { 'git_url':giturl }
        with self.assertRaises(ValueError) as e:
            self.catalog.set_to_active(self.cUtil.user_ctx(),params)
        self.assertEqual(str(e.exception),
            'Only Admin users can set a module to be active/inactive.');
        with self.assertRaises(ValueError) as e:
            self.catalog.set_to_inactive(self.cUtil.user_ctx(),params)
        self.assertEqual(str(e.exception),
            'Only Admin users can set a module to be active/inactive.');

        # module should start as active, but it should be fine to set it again
        state = self.catalog.get_module_state(self.cUtil.admin_ctx(),params)[0]
        self.assertEqual(state['active'],1)
        self.catalog.set_to_active(self.cUtil.admin_ctx(),params)
        state = self.catalog.get_module_state(self.cUtil.admin_ctx(),params)[0]
        self.assertEqual(state['active'],1)
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']=='CatalogTestModule2/test_method_1' and meth['namespace']=='CatalogTestModule2':
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS')

        # make it inactive (calling twice should be ok and shouldn't change anything)
        self.catalog.set_to_inactive(self.cUtil.admin_ctx(),params)
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),params)[0]
        self.assertEqual(state['active'],0)
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']=='CatalogTestModule2/test_method_1' and meth['namespace']=='CatalogTestModule2':
                foundMeth = True
        self.assertFalse(foundMeth,'Make sure we did not find the method in NMS')

        self.catalog.set_to_inactive(self.cUtil.admin_ctx(),params)
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),params)[0]
        self.assertEqual(state['active'],0)
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']=='CatalogTestModule2/test_method_1' and meth['namespace']=='CatalogTestModule2':
                foundMeth = True
        self.assertFalse(foundMeth,'Make sure we did not find the method in NMS again')


        # these still shouldn't work
        with self.assertRaises(ValueError) as e:
            self.catalog.set_to_active(self.cUtil.user_ctx(),params)
        self.assertEqual(str(e.exception),
            'Only Admin users can set a module to be active/inactive.');
        with self.assertRaises(ValueError) as e:
            self.catalog.set_to_inactive(self.cUtil.user_ctx(),params)
        self.assertEqual(str(e.exception),
            'Only Admin users can set a module to be active/inactive.');

        # make it active one more time and make sure the method specs reappear
        self.catalog.set_to_active(self.cUtil.admin_ctx(),params)
        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),params)[0]
        self.assertEqual(state['active'],1)
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']=='CatalogTestModule2/test_method_1' and meth['namespace']=='CatalogTestModule2':
                foundMeth = True
        self.assertTrue(foundMeth,'Make sure we found the method in NMS after reactivation')


        # delete it.
        self.catalog.delete_module(self.cUtil.admin_ctx(),
                {'module_name':'CatalogTestModule2'})

        # make sure it is gone
        self.assertEqual(self.catalog.is_registered({},{'module_name':'CatalogTestModule2'})[0],0)
        method_list = self.nms.list_methods({'tag':'dev'})
        foundMeth = False
        for meth in method_list:
            if meth['id']=='CatalogTestModule2/test_method_1' and meth['namespace']=='CatalogTestModule2':
                foundMeth = True
        self.assertFalse(foundMeth,'Make sure we did not find the method in NMS')


        # we cannot remove modules that have been released
        self.assertEqual(self.catalog.is_registered({},{'module_name':'onerepotest'})[0],1)
        with self.assertRaises(ValueError) as e:
            self.catalog.delete_module(self.cUtil.admin_ctx(),
                {'module_name':'onerepotest'})
        self.assertEqual(self.catalog.is_registered({},{'module_name':'onerepotest'})[0],1)
        self.assertEqual(str(e.exception),
            'Cannot delete module that has been released.  Make it inactive instead.');
        self.assertEqual(self.catalog.is_registered({},{'git_url':'https://github.com/kbaseIncubator/release_history'})[0],1)

        with self.assertRaises(ValueError) as e:
            self.catalog.delete_module(self.cUtil.admin_ctx(),
                {'git_url':'https://github.com/kbaseIncubator/release_history'})
        self.assertEqual(self.catalog.is_registered({},{'git_url':'https://github.com/kbaseIncubator/release_history'})[0],1)
        self.assertEqual(str(e.exception),
            'Cannot delete module that has been released.  Make it inactive instead.');



    @classmethod
    def setUpClass(cls):

        print('++++++++++++ RUNNING core_registration_test.py +++++++++++')

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




