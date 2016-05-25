

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


# tests all the basic get methods
class BasicCatalogTest(unittest.TestCase):


    def test_version(self):
        self.assertEqual(self.catalog.version(self.cUtil.anonymous_ctx()),['2.0.0'])


    def test_is_registered(self):
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'}),
            [1])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/onerepotest'}),
            [1])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest','git_url':'https://github.com/kbaseIncubator/onerepotest'}),
            [1])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'wrong_name'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'wrong_name','git_url':'https://github.com/kbaseIncubator/onerepotest'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest','git_url':'wrong_url'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {'git_url':'wrong_url'}),
            [0])
        self.assertEqual(self.catalog.is_registered(self.cUtil.anonymous_ctx(),
            {}),
            [0])


    def test_list_requested_releases(self):
        requested_releases = self.catalog.list_requested_releases(self.cUtil.anonymous_ctx())[0]
        found_modules = []
        for r in requested_releases:
            self.assertIn('module_name',r)
            found_modules.append(r['module_name'])
            self.assertIn('owners',r)
            self.assertIn('timestamp',r)
            self.assertIn('git_url',r)
            self.assertIn('git_commit_message',r)
            self.assertIn('git_commit_hash',r)
            if r['module_name'] == 'pending_first_release' :
                self.assertEqual(r['git_commit_hash'],    'b843888e962642d665a3b0bd701ee630c01835e6')
                self.assertEqual(r['git_commit_message'], 'update for testing')
                self.assertEqual(r['git_url'],            'https://github.com/kbaseIncubator/pending_Release')
                self.assertEqual(r['timestamp'],          1445023985597)
                self.assertIn('kbasetest',r['owners'])
            if r['module_name'] == 'pending_second_release' :
                self.assertEqual(r['git_url'],            'https://github.com/kbaseIncubator/pending_second_release')
                self.assertIn('rsutormin',r['owners'])
                self.assertIn('wstester1',r['owners'])

        self.assertIn('pending_first_release',found_modules)
        self.assertIn('pending_second_release',found_modules)



    def test_list_basic_module_info(self):

        # default should include all modules that are released
        default = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {})[0]
        module_names = []
        for m in default:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(['DynamicService','DynamicService2','onerepotest','pending_second_release','release_history'])
            )

        # all released and unreleased
        include_unreleased = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_unreleased':1})[0]
        module_names = []
        for m in include_unreleased:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(sorted(['DynamicService','DynamicService2','denied_release','onerepotest','pending_first_release','pending_second_release',
                'registration_error','registration_in_progress','release_history']))
            )

        # no released and no unreleased
        include_nothing = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_released':0})[0]
        module_names = []
        for m in include_nothing:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join([])
            )

        #only unreleased modules
        only_unreleased = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_released':0, 'include_unreleased':1})[0]
        module_names = []
        for m in only_unreleased:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(sorted(['denied_release','pending_first_release','registration_error',
                'registration_in_progress']))
            )

        inactive = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'include_disabled':1,'include_released':0,'include_unreleased':1})[0]
        module_names = []
        for m in inactive:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(sorted(['inactive_module','denied_release','pending_first_release','registration_error',
                'registration_in_progress']))
            )

        # check for owner search
        shortlist = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'owners':['kbasetest'],'include_unreleased':0})[0]
        module_names = []
        for m in shortlist:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join([])
            )
        shortlist = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'owners':['kbasetest'],'include_unreleased':1})[0]
        module_names = []
        for m in shortlist:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(['pending_first_release'])
            )
        shortlist = self.catalog.list_basic_module_info(self.cUtil.anonymous_ctx(),
            {'owners':['kbasetest', 'wstester1'],'include_unreleased':1})[0]
        module_names = []
        for m in shortlist:
            module_names.append(m['module_name'])
        self.assertEqual(
            ",".join(sorted(module_names)),
            ",".join(['denied_release','onerepotest','pending_first_release','pending_second_release','registration_error','registration_in_progress'])
            )


    def test_get_module_state(self):
        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'})[0]
        self.assertEqual(state['active'],1)
        self.assertEqual(state['release_approval'],'approved')
        self.assertEqual(state['review_message'],'')
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['error_message'],'')

        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'module_name':'inactive_module'})[0]
        self.assertEqual(state['active'],0)
        self.assertEqual(state['release_approval'],'not_requested')
        self.assertEqual(state['review_message'],'')
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['error_message'],'')

        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/registration_in_progress'})[0]
        self.assertEqual(state['active'],1)
        self.assertEqual(state['release_approval'],'not_requested')
        self.assertEqual(state['review_message'],'')
        self.assertEqual(state['registration'],'building: doing stuff')
        self.assertEqual(state['error_message'],'')

        state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/pending_second_release'})[0]
        self.assertEqual(state['active'],1)
        self.assertEqual(state['release_approval'],'under_review')
        self.assertEqual(state['review_message'],'')
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['error_message'],'')

        # test various fail cases where a module does not exist
        with self.assertRaises(ValueError) as e:
            self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'module_name':'not_a_module'})
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');
        with self.assertRaises(ValueError) as e:
            self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'git_url':'not_a_giturl'})
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');
        with self.assertRaises(ValueError) as e:
            self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {})
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');
        with self.assertRaises(ValueError) as e:
            self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'module_name':'not_a_module','git_url':'https://github.com/kbaseIncubator/registration_in_progress'})
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');
        with self.assertRaises(ValueError) as e:
            self.catalog.get_module_state(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest','git_url':'not_a_url'})
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');


    def test_get_module_info(self):
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'})[0]
        self.assertEqual(info['module_name'],'onerepotest')
        self.assertEqual(info['git_url'],'https://github.com/kbaseIncubator/onerepotest')
        self.assertEqual(info['description'],'KBase module for integration tests of docker-based service/async method calls')
        self.assertEqual(info['owners'],['rsutormin','wstester1'])
        self.assertEqual(info['language'],'python')

        self.assertEqual(info['release']['git_commit_hash'],'49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(info['release']['timestamp'],1445022818884)
        self.assertEqual(info['release']['git_commit_message'],'added username for testing')
        self.assertEqual(info['release']['version'],'0.0.1')
        self.assertEqual(info['release']['narrative_methods'],['send_data'])

        self.assertEqual(info['beta']['git_commit_hash'],'b843888e962642d665a3b0bd701ee630c01835e6')
        self.assertEqual(info['beta']['timestamp'],1445023985597)
        self.assertEqual(info['beta']['git_commit_message'],'update for testing')
        self.assertEqual(info['beta']['version'],'0.0.1')
        self.assertEqual(info['beta']['narrative_methods'],['send_data'])

        self.assertEqual(info['dev']['git_commit_hash'],'b06c5f9daf603a4d206071787c3f6184000bf128')
        self.assertEqual(info['dev']['timestamp'],1445024094055)
        self.assertEqual(info['dev']['git_commit_message'],'another change')
        self.assertEqual(info['dev']['version'],'0.0.1')
        self.assertEqual(info['dev']['narrative_methods'],['send_data'])


        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/pending_Release'})[0]

        self.assertEqual(info['module_name'],'pending_first_release')
        self.assertEqual(info['git_url'],'https://github.com/kbaseIncubator/pending_Release')
        self.assertEqual(info['description'],' something')
        self.assertEqual(info['owners'],['kbasetest'])
        self.assertEqual(info['language'],'perl')
        self.assertTrue(info['release'] is None)



    def test_get_module_version(self):

        # fetch without version info, should return latest release version
        version = self.catalog.get_module_version(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history'})[0]

        self.assertEqual(version['timestamp'],1445022818884)
        self.assertEqual(version['version'],"0.0.3")
        self.assertEqual(version['narrative_methods'],['send_data'])
        self.assertEqual(version['local_functions'],[])
        self.assertEqual(version['module_language'],'python')
        self.assertEqual(version['module_name'],'release_history')
        self.assertEqual(version['notes'],'')
        self.assertEqual(version['registration_id'],'1445022818884_4123')
        self.assertEqual(version['release_tags'],['release'])
        self.assertEqual(version['release_timestamp'], 1445022818884)
        self.assertEqual(version['docker_img_name'],'dockerhub-ci.kbase.us/kbase:release_history.49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(version['dynamic_service'],0)
        self.assertEqual(version['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(version['git_commit_message'],"added username for testing")
        self.assertEqual(version['git_url'],"https://github.com/kbaseIncubator/release_history")


        # get a specific tag
        version = self.catalog.get_module_version(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'dev', 'include_module_description':0, 'include_compilation_report':0})[0]

        self.assertEqual(version['timestamp'],1445024094055)
        self.assertEqual(version['version'],"0.0.5")
        self.assertEqual(version['narrative_methods'],['send_data2'])
        self.assertEqual(version['local_functions'],[])
        self.assertEqual(version['module_language'],'python')
        self.assertEqual(version['module_name'],'release_history')
        self.assertEqual(version['notes'],'')
        self.assertEqual(version['registration_id'],'1445024094055_4123')
        self.assertEqual(version['release_tags'],['dev'])
        self.assertEqual(version['release_timestamp'], None)
        self.assertEqual(version['docker_img_name'],'dockerhub-ci.kbase.us/kbase:release_history.b06c5f9daf603a4d206071787c3f6184000bf128')
        self.assertEqual(version['dynamic_service'],0)
        self.assertEqual(version['git_commit_hash'],"b06c5f9daf603a4d206071787c3f6184000bf128")
        self.assertEqual(version['git_commit_message'],"another change")
        self.assertEqual(version['git_url'],"https://github.com/kbaseIncubator/release_history")

        # get by git commit hash
        version = self.catalog.get_module_version(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'49dc505febb8f4cccb2078c58ded0de3320534d7', 'include_module_description':0, 'include_compilation_report':0})[0]

        self.assertEqual(version['timestamp'],1445022818884)
        self.assertEqual(version['version'],"0.0.3")
        self.assertEqual(version['narrative_methods'],['send_data'])
        self.assertEqual(version['local_functions'],[])
        self.assertEqual(version['module_language'],'python')
        self.assertEqual(version['module_name'],'release_history')
        self.assertEqual(version['notes'],'')
        self.assertEqual(version['registration_id'],'1445022818884_4123')
        self.assertEqual(version['release_tags'],['release'])
        self.assertEqual(version['release_timestamp'], 1445022818884)
        self.assertEqual(version['docker_img_name'],'dockerhub-ci.kbase.us/kbase:release_history.49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(version['dynamic_service'],0)
        self.assertEqual(version['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(version['git_commit_message'],"added username for testing")
        self.assertEqual(version['git_url'],"https://github.com/kbaseIncubator/release_history")

        # get by exact semantic version
        version = self.catalog.get_module_version(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'0.0.3', 'include_module_description':0, 'include_compilation_report':0})[0]

        self.assertEqual(version['timestamp'],1445022818884)
        self.assertEqual(version['version'],"0.0.3")
        self.assertEqual(version['narrative_methods'],['send_data'])
        self.assertEqual(version['local_functions'],[])
        self.assertEqual(version['module_language'],'python')
        self.assertEqual(version['module_name'],'release_history')
        self.assertEqual(version['notes'],'')
        self.assertEqual(version['registration_id'],'1445022818884_4123')
        self.assertEqual(version['release_tags'],['release'])
        self.assertEqual(version['release_timestamp'], 1445022818884)
        self.assertEqual(version['docker_img_name'],'dockerhub-ci.kbase.us/kbase:release_history.49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(version['dynamic_service'],0)
        self.assertEqual(version['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(version['git_commit_message'],"added username for testing")
        self.assertEqual(version['git_url'],"https://github.com/kbaseIncubator/release_history")


        # get by semantic version spec
        version = self.catalog.get_module_version(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'>0.0.1', 'include_module_description':0, 'include_compilation_report':0})[0]

        self.assertEqual(version['timestamp'],1445022818884)
        self.assertEqual(version['version'],"0.0.3")
        self.assertEqual(version['narrative_methods'],['send_data'])
        self.assertEqual(version['local_functions'],[])
        self.assertEqual(version['module_language'],'python')
        self.assertEqual(version['module_name'],'release_history')
        self.assertEqual(version['notes'],'')
        self.assertEqual(version['registration_id'],'1445022818884_4123')
        self.assertEqual(version['release_tags'],['release'])
        self.assertEqual(version['release_timestamp'], 1445022818884)
        self.assertEqual(version['docker_img_name'],'dockerhub-ci.kbase.us/kbase:release_history.49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(version['dynamic_service'],0)
        self.assertEqual(version['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(version['git_commit_message'],"added username for testing")
        self.assertEqual(version['git_url'],"https://github.com/kbaseIncubator/release_history")


    def test_get_version_info(self):

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'dev'})[0]
        self.assertEqual(vinfo['git_commit_hash'],"b06c5f9daf603a4d206071787c3f6184000bf128")
        self.assertEqual(vinfo['timestamp'],1445024094055)
        self.assertEqual(vinfo['git_commit_message'],"another change")
        self.assertEqual(vinfo['version'],"0.0.5")
        self.assertEqual(vinfo['narrative_methods'],['send_data2'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'beta'})[0]
        self.assertEqual(vinfo['git_commit_hash'],"b843888e962642d665a3b0bd701ee630c01835e6")
        self.assertEqual(vinfo['timestamp'],1445023985597)
        self.assertEqual(vinfo['git_commit_message'],"update for testing")
        self.assertEqual(vinfo['version'],"0.0.4")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history', 'version':'release'})[0]
        self.assertEqual(vinfo['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(vinfo['timestamp'],1445022818884)
        self.assertEqual(vinfo['git_commit_message'],"added username for testing")
        self.assertEqual(vinfo['version'],"0.0.3")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'version':'release',
                'git_commit_hash':'49dc505febb8f4cccb2078c58ded0de3320534d7'})[0]
        self.assertEqual(vinfo['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(vinfo['timestamp'],1445022818884)
        self.assertEqual(vinfo['git_commit_message'],"added username for testing")
        self.assertEqual(vinfo['version'],"0.0.3")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'version':'release',
                'timestamp':1445022818884})[0]
        self.assertEqual(vinfo['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(vinfo['timestamp'],1445022818884)
        self.assertEqual(vinfo['git_commit_message'],"added username for testing")
        self.assertEqual(vinfo['version'],"0.0.3")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'version':'release',
                'git_commit_hash':'49dc505febb8f4cccb2078c58ded0de3320534d7',
                'timestamp':1445022818884})[0]
        self.assertEqual(vinfo['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(vinfo['timestamp'],1445022818884)
        self.assertEqual(vinfo['git_commit_message'],"added username for testing")
        self.assertEqual(vinfo['version'],"0.0.3")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        # wrong version set
        with self.assertRaises(ValueError) as e:
            self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'version':'not_a_Version'})
        self.assertEqual(str(e.exception),
            'invalid version selection, valid versions are: "dev" | "beta" | "release"');
        # test wrong git commit hash
        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 'version':'release',
                    'git_commit_hash':'b06c5f9daf603a4d206071787c3f6184000bf128'})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');
        # test wrong timestamp
        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 'version':'release',
                    'timestamp':1445024094055})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');
        # right git commit, wrong timestamp
        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 'version':'release',
                    'git_commit_hash':'b06c5f9daf603a4d206071787c3f6184000bf128',
                    'timestamp':1445024094055})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');
        # right timestamp, wrong git commit hash
        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 'version':'release',
                    'git_commit_hash':'b843888e962642d665a3b0bd701ee630c01835e6',
                    'timestamp':1445022818884})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');

        #########
        # now we test with a timestamp retrieval, first from one of the currents
        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'timestamp':1445022818884})[0]
        self.assertEqual(vinfo['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(vinfo['timestamp'],1445022818884)
        self.assertEqual(vinfo['git_commit_message'],"added username for testing")
        self.assertEqual(vinfo['version'],"0.0.3")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'timestamp':1445022818884,
                'git_commit_hash':"49dc505febb8f4cccb2078c58ded0de3320534d7"})[0]
        self.assertEqual(vinfo['git_commit_hash'],"49dc505febb8f4cccb2078c58ded0de3320534d7")
        self.assertEqual(vinfo['timestamp'],1445022818884)
        self.assertEqual(vinfo['git_commit_message'],"added username for testing")
        self.assertEqual(vinfo['version'],"0.0.3")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 'timestamp':1445022818884,
                    'git_commit_hash':"49dc505febb8f4cccb2078c51ded0de3320534d7"})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');

        # now with something in the history
        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'timestamp':1445022818000})[0]
        self.assertEqual(vinfo['git_commit_hash'],"d6cd1e2bd19e03a81132a23b2025920577f84e37")
        self.assertEqual(vinfo['timestamp'],1445022818000)
        self.assertEqual(vinfo['git_commit_message'],"something else")
        self.assertEqual(vinfo['version'],"0.0.2")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'timestamp':1445022818000,
                'git_commit_hash':"d6cd1e2bd19e03a81132a23b2025920577f84e37"})[0]
        self.assertEqual(vinfo['git_commit_hash'],"d6cd1e2bd19e03a81132a23b2025920577f84e37")
        self.assertEqual(vinfo['timestamp'],1445022818000)
        self.assertEqual(vinfo['git_commit_message'],"something else")
        self.assertEqual(vinfo['version'],"0.0.2")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        # test wrong timestamp
        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history',
                    'timestamp':1445024094078})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');

        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 'timestamp':1445022818000, 
                    'git_commit_hash':"49dc505febb8f4cccb2078c51ded0de3320534d7"})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');



        #########
        # now we test with a git commit hash retrieval, first from one of the currents
        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'git_commit_hash':'b843888e962642d665a3b0bd701ee630c01835e6'})[0]
        self.assertEqual(vinfo['git_commit_hash'],"b843888e962642d665a3b0bd701ee630c01835e6")
        self.assertEqual(vinfo['timestamp'],1445023985597)
        self.assertEqual(vinfo['git_commit_message'],"update for testing")
        self.assertEqual(vinfo['version'],"0.0.4")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        # next from something in the history
        vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                {'module_name':'release_history', 'git_commit_hash':'9bedf67800b2923982bdf60c89c57ce6fd2d9a1c'})[0]
        self.assertEqual(vinfo['git_commit_hash'],"9bedf67800b2923982bdf60c89c57ce6fd2d9a1c")
        self.assertEqual(vinfo['timestamp'],1445022815000)
        self.assertEqual(vinfo['git_commit_message'],"and another thing")
        self.assertEqual(vinfo['version'],"0.0.1")
        self.assertEqual(vinfo['narrative_methods'],['send_data'])

        # test wrong git commit hash
        with self.assertRaises(ValueError) as e:
            vinfo = self.catalog.get_version_info(self.cUtil.anonymous_ctx(),
                    {'module_name':'release_history', 
                    'git_commit_hash':'b06c5f9daf603a4d202071787c3f6184000bf128'})[0]
        self.assertEqual(str(e.exception),
            'No version found that matches all your criteria!');



    def test_list_released_module_versions(self):
        # history should return versions sorted by timestamp
        history = self.catalog.list_released_module_versions(self.cUtil.anonymous_ctx(),
            {'module_name':'release_history'})[0]
        self.assertTrue(len(history) == 3)
        self.assertEqual(history[0]['git_commit_hash'], '9bedf67800b2923982bdf60c89c57ce6fd2d9a1c')
        self.assertEqual(history[0]['timestamp'], 1445022815000)
        self.assertEqual(history[0]['version'], '0.0.1')
        self.assertEqual(history[0]['narrative_methods'],['send_data'])
        self.assertEqual(history[1]['git_commit_hash'], 'd6cd1e2bd19e03a81132a23b2025920577f84e37')
        self.assertEqual(history[1]['timestamp'], 1445022818000)
        self.assertEqual(history[1]['version'], '0.0.2')
        self.assertEqual(history[2]['git_commit_hash'], '49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(history[2]['timestamp'], 1445022818884)
        self.assertEqual(history[2]['version'], '0.0.3')

        history = self.catalog.list_released_module_versions(self.cUtil.anonymous_ctx(),
            {'module_name':'onerepotest'})[0]
        self.assertTrue(len(history) == 1)
        self.assertEqual(history[0]['git_commit_hash'], '49dc505febb8f4cccb2078c58ded0de3320534d7')
        self.assertEqual(history[0]['git_commit_message'], 'added username for testing')
        self.assertEqual(history[0]['timestamp'], 1445022818884)
        self.assertEqual(history[0]['version'], '0.0.1')
        self.assertEqual(history[0]['narrative_methods'],['send_data'])

        history = self.catalog.list_released_module_versions(self.cUtil.anonymous_ctx(),
            {'git_url':'https://github.com/kbaseIncubator/pending_Release'})[0]
        self.assertEqual(history,[])

    

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING basic_catalog_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




