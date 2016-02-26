

import unittest
import os

from pprint import pprint

from catalog_test_util import CatalogTestUtil
from biokbase.catalog.Impl import Catalog


class ClientGroupMethodsTest(unittest.TestCase):


    # assumes no client groups exist
    def test_basics(self):

        userCtx = self.cUtil.user_ctx()
        adminCtx = self.cUtil.admin_ctx()
        anonCtx = self.cUtil.anonymous_ctx()

        # list should be empty
        groups = self.catalog.get_client_groups(anonCtx, {})[0]
        self.assertEqual(groups,[])

        # error if user attempts to set the context
        with self.assertRaises(ValueError) as e:
            self.catalog.set_client_group(userCtx, 
                {'app_id':'mEgaHit/run_Megahit', 'client_groups':['g1']})
        self.assertEqual(str(e.exception),
            'You do not have permission to set execution client groups.');

        # try adding one
        self.catalog.set_client_group(adminCtx, 
            {'app_id':'mEgaHit/run_Megahit', 'client_groups':['g1']})

        groups = self.catalog.get_client_groups(anonCtx, {})[0]
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['app_id'],'megahit/run_Megahit')
        self.assertEqual(groups[0]['client_groups'],['g1'])

        # try adding a few more
        self.catalog.set_client_group(adminCtx, 
            {'app_id':'rna/run_something', 'client_groups':['g1']})
        self.catalog.set_client_group(adminCtx, 
            {'app_id':'rna/run_something2', 'client_groups':['g1','g2']})
        self.catalog.set_client_group(adminCtx, 
            {'app_id':'rna/run_something3', 'client_groups':['g3']})
        self.catalog.set_client_group(adminCtx, 
            {'app_id':'DNA/run_something', 'client_groups':['g2']})

        # check em
        groups = self.catalog.get_client_groups(anonCtx, {})[0]
        self.assertEqual(len(groups),5)
        found_megahit = False
        found_rna = False
        found_dna = False
        found_rna2 = False
        found_rna3 = False

        for g in groups:
            if g['app_id'] == 'megahit/run_Megahit':
                found_megahit = True
                self.assertEqual(g['client_groups'],['g1'])

            elif g['app_id'] == 'rna/run_something':
                found_rna = True
                self.assertEqual(g['client_groups'],['g1'])

            elif g['app_id'] == 'rna/run_something2':
                found_rna2 = True
                #self.assertEqual(groups[0]['client_groups'],['g1', 'g2'])

            elif g['app_id'] == 'rna/run_something3':
                found_rna3 = True
                self.assertEqual(g['client_groups'],['g3'])

            elif g['app_id'] == 'dna/run_something':
                found_dna = True
                self.assertEqual(g['client_groups'],['g2'])

        self.assertTrue(found_megahit, 'Found megahit client group')
        self.assertTrue(found_rna, 'Found rna client group')
        self.assertTrue(found_rna2, 'Found rna2 client group')
        self.assertTrue(found_rna3, 'Found rna3 client group')
        self.assertTrue(found_dna, 'Found dna client group')

        # try just getting selected methods
        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['MegaHit/run_Megahit']})[0]
        self.assertEqual(len(groups),1)

        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['asdf']})[0]
        self.assertEqual(len(groups),0)

        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['dna/run_something', 'MegaHit/run_Megahit']})[0]
        self.assertEqual(len(groups),2)

        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['dna/run_something', 'MegaHit/run_Megahit', 'asdfasd']})[0]
        self.assertEqual(len(groups),2)

        # should give everything
        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':[]})[0]
        self.assertEqual(len(groups),5)

        # finally check that we can update something a few times
        self.catalog.set_client_group(adminCtx, 
            {'app_id':'DNA/run_something', 'client_groups':['new_group']})
        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['dna/run_something']})[0]
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['app_id'],'dna/run_something')
        self.assertEqual(groups[0]['client_groups'],['new_group'])


        self.catalog.set_client_group(adminCtx, 
            {'app_id':'DNA/run_something', 'client_groups':['*']})
        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['dna/run_something']})[0]
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['app_id'],'dna/run_something')
        self.assertEqual(groups[0]['client_groups'],['*'])

        self.catalog.set_client_group(adminCtx, 
            {'app_id':'DNA/run_something', 'client_groups':[]})
        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['dna/run_something']})[0]
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['app_id'],'dna/run_something')
        self.assertEqual(groups[0]['client_groups'],[])


        self.catalog.set_client_group(adminCtx, 
            {'app_id':'DNA/run_something', 'client_groups':['new_g1', 'new_g2', 'new_g3']})
        groups = self.catalog.get_client_groups(anonCtx, {'app_ids':['dna/run_something']})[0]
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]['app_id'],'dna/run_something')
        self.assertEqual(groups[0]['client_groups'],['new_g1', 'new_g2', 'new_g3'])



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




