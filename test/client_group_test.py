

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



    def test_volume_mount_configs(self):

        userCtx = self.cUtil.user_ctx()
        adminCtx = self.cUtil.admin_ctx()

        # mere users cannot list, set, or remove mounts
        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(userCtx, {})
        self.assertEqual(str(e.exception),
            'You do not have permission to set volume mounts.');

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_volume_mount(userCtx, {})
        self.assertEqual(str(e.exception),
            'You do not have permission to remove volume mounts.');

        with self.assertRaises(ValueError) as e:
            self.catalog.list_volume_mounts(userCtx, {})
        self.assertEqual(str(e.exception),
            'You do not have permission to view volume mounts.');

        # basic filter should return the preloaded mounts, of which there are 4
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),4)

        # try some other filters, make sure we get the right number of things
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, { 'module_name':'VolmountModTest1' })[0]
        self.assertEqual(len(vol_mounts),1)
        self.assertEqual(vol_mounts[0]['module_name'],'VolMountModTest1')
        self.assertEqual(vol_mounts[0]['app_id'],'func1')
        self.assertEqual(vol_mounts[0]['client_group'],'G1')
        self.assertEqual(len(vol_mounts[0]['volume_mounts']), 2)
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['host_dir'], '/home/wstester1')
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['container_dir'], '/mnt/tmp')
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['read_only'], 1)

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, { 'module_name':'VolMountModTest2' })[0]
        self.assertEqual(len(vol_mounts),3)

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, { 'app_id':'func1' })[0]
        self.assertEqual(len(vol_mounts),3)

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, { 'client_group':'G3' })[0]
        self.assertEqual(len(vol_mounts),2)

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, { 'module_name':'VolMountModTest2', 'app_id':'func1' })[0]
        self.assertEqual(len(vol_mounts),2)

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, { 'module_name':'VolMountModTest2', 'app_id':'func1', 'client_group':'G2' })[0]
        self.assertEqual(len(vol_mounts),1)
        self.assertEqual(vol_mounts[0]['module_name'],'VolMountModTest2')
        self.assertEqual(vol_mounts[0]['app_id'],'func1')
        self.assertEqual(vol_mounts[0]['client_group'],'G2')
        self.assertEqual(len(vol_mounts[0]['volume_mounts']), 1)
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['host_dir'], '/home/wstester1')
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['container_dir'], '/mnt/tmp2')
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['read_only'], 0)

        with self.assertRaises(ValueError) as e:
            self.catalog.list_volume_mounts(adminCtx, { 'module_name': [] })
        self.assertEqual(str(e.exception),
            'module_name parameter field must be a string');

        with self.assertRaises(ValueError) as e:
            self.catalog.list_volume_mounts(adminCtx, { 'app_id': [] })
        self.assertEqual(str(e.exception),
            'app_id parameter field must be a string');

        with self.assertRaises(ValueError) as e:
            self.catalog.list_volume_mounts(adminCtx, { 'client_group': [] })
        self.assertEqual(str(e.exception),
            'client_group parameter field must be a string');



        # try to add a volume mount, keep adding things till we get a success
        volume_mount_config = {}
        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'module_name parameter field is required');

        volume_mount_config['module_name'] = []
        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'module_name parameter field must be a string');
        volume_mount_config['module_name'] = 'Tester2'

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'app_id parameter field is required');

        volume_mount_config['app_id'] = []
        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'app_id parameter field must be a string');
        volume_mount_config['app_id'] = 'my_app'

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'client_group parameter field is required');

        volume_mount_config['client_group'] = []
        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'client_group parameter field must be a string');
        volume_mount_config['client_group'] = 'g23123'

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'volume_mounts parameter field is required');

        volume_mount_config['volume_mounts'] = 'hello'
        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'volume_mounts parameter field must be a list');
        volume_mount_config['volume_mounts'] = [{
                'host_dir' : '/tmp',
                'container_dir' : '/tmp/asdf',
                'read_only': 1
            }, {}]

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'host_dir parameter field is required in all volume_mount configurations');

        volume_mount_config['volume_mounts'] = [{
                'host_dir' : '/tmp',
                'read_only': 1
            }]

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'container_dir parameter field is required in all volume_mount configurations');

        volume_mount_config['volume_mounts'] = [{
                'host_dir' : '/tmp',
                'container_dir' : '/tmp/asdf'
            }]

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'read_only parameter field is required in all volume_mount configurations');

        volume_mount_config['volume_mounts'] = [{
                'host_dir' : '/tmp',
                'container_dir' : '/tmp/asdf',
                'read_only':2
            }]

        with self.assertRaises(ValueError) as e:
            self.catalog.set_volume_mount(adminCtx, volume_mount_config)
        self.assertEqual(str(e.exception),
            'read_only parameter field in volume_mount list must be either 1 (true) or 0 (false)');

        volume_mount_config = {
            'module_name': 'tester2',
            'app_id':'my_app',
            'client_group':'g23123',
            'volume_mounts' : [
            {
                'host_dir' : '/tmp',
                'container_dir' : '/tmp/asdf',
                'read_only': 1
            }
            ]
        }
        self.catalog.set_volume_mount(adminCtx, volume_mount_config)


        filter = { 'module_name' : 'tester2' }
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, filter)[0]
        self.assertEqual(len(vol_mounts),1)
        self.assertEqual(vol_mounts[0]['module_name'],'tester2')
        self.assertEqual(vol_mounts[0]['app_id'],'my_app')
        self.assertEqual(vol_mounts[0]['client_group'],'g23123')
        self.assertEqual(len(vol_mounts[0]['volume_mounts']), 1)
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['host_dir'], '/tmp')
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['container_dir'], '/tmp/asdf')
        self.assertEqual(vol_mounts[0]['volume_mounts'][0]['read_only'], 1)


        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),5)

        volume_mount_config = {
            'module_name': 'tester2',
            'app_id':'my_app',
            'client_group':'g23123',
            'volume_mounts' : []
        }
        self.catalog.set_volume_mount(adminCtx, volume_mount_config)

        filter = { 'module_name' : 'tester2' }
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, filter)[0]
        self.assertEqual(len(vol_mounts),1)
        self.assertEqual(vol_mounts[0]['module_name'],'tester2')
        self.assertEqual(vol_mounts[0]['app_id'],'my_app')
        self.assertEqual(vol_mounts[0]['client_group'],'g23123')
        self.assertEqual(len(vol_mounts[0]['volume_mounts']), 0)

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),5)


        # Finally test removal
        with self.assertRaises(ValueError) as e:
            self.catalog.remove_volume_mount(adminCtx, {})
        self.assertEqual(str(e.exception),
            'module_name parameter field is required');
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),5)

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_volume_mount(adminCtx, {'module_name':'Tester2'})
        self.assertEqual(str(e.exception),
            'app_id parameter field is required');
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),5)

        with self.assertRaises(ValueError) as e:
            self.catalog.remove_volume_mount(adminCtx, {'module_name':'Tester2', 'app_id':'my_app'})
        self.assertEqual(str(e.exception),
            'client_group parameter field is required');
        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),5)

        self.catalog.remove_volume_mount(adminCtx, {'module_name':'Tester2', 'app_id':'my_app', 'client_group':'g23123'})

        vol_mounts = self.catalog.list_volume_mounts(adminCtx, {})[0]
        self.assertEqual(len(vol_mounts),4)

        return




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




