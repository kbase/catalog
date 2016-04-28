
from __future__ import print_function

import unittest
import os

from pprint import pprint
from time import time

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog
from biokbase.narrative_method_store.client import NarrativeMethodStore


# tests all the basic get methods
class LocalFunctionModuleTest(unittest.TestCase):


    # assumes no developers have been added yet
    def test_local_function_module(self):

        # TODO: figure out git_commit hash or branch configuration
        # assume test user is already approved as a developer
        # (1) register the test repo
        giturl = self.cUtil.get_test_repo_1()
        githash = '68c045d784142ec91142cfc76448d949604fc4df' # branch local_method_module
        registration_id = self.catalog.register_repo(self.cUtil.user_ctx(),
            {'git_url':giturl, 'git_commit_hash':githash})[0]
        timestamp = int(registration_id.split('_')[0])

        # (2) check state until error or complete, must be complete, and make sure this was relatively fast
        start = time()
        timeout = 6000 #seconds
        last_line = 0;
        while True:
            time.sleep(1)
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':giturl})[0]

            # log line printing:
            parsed_log = parsed_log_subset = self.catalog.get_parsed_build_log(self.cUtil.anonymous_ctx(),
                            {
                                'registration_id':registration_id,
                                'skip':last_line,
                                'limit':1000
                            })[0]
            for l in parsed_log['log']:
                print(l['content'], end='')
                last_line+=1

            if state['registration'] in ['complete','error']:
                break
            self.assertTrue(time()-start < timeout, 'simple registration build exceeded timeout of '+str(timeout)+'s')
       
        pprint(state)
        self.assertEqual(state['registration'],'complete')




    @classmethod
    def setUpClass(cls):

        print('++++++++++++ RUNNING local_function_module_test.py +++++++++++')

        # hack for testing!! remove when docker and NMS components can be tested
        from biokbase.catalog.registrar import Registrar
        Registrar._TEST_WITHOUT_DOCKER = False

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




