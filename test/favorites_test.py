import time
import unittest

from biokbase.catalog.Impl import Catalog
from catalog_test_util import CatalogTestUtil


# tests all the basic get methods
class BasicCatalogTest(unittest.TestCase):

    def test_add_remove_aggregate_favorites(self):

        ctx = self.cUtil.user_ctx()
        user = ctx['user_id']

        # start out with no favorites
        favs = self.catalog.list_favorites(ctx, user)[0]
        self.assertEqual(len(favs), 0)

        # aggregated favorites should not have anything for megahit
        fav_counts = self.catalog.list_favorite_counts({}, {})[0]
        found = False
        for f in fav_counts:
            if f['module_name_lc'] + '/' + f['id'] == 'megahit/run_megahit':
                found = True
        self.assertFalse(found)

        # add a couple and check that they appear correctly
        self.catalog.add_favorite(ctx,
                                  {'module_name': 'MegaHit', 'id': 'run_megahit'})
        favs = self.catalog.list_favorites(ctx, user)[0]
        self.assertEqual(len(favs), 1)
        self.assertEqual(favs[0]['module_name_lc'], 'megahit')
        self.assertEqual(favs[0]['id'], 'run_megahit')
        self.assertIsNotNone(favs[0]['timestamp'])

        time.sleep(1)  # force different timestamps so sort works
        self.catalog.add_favorite(ctx,
                                  {'module_name': 'MegaHit', 'id': 'run_megahit_2'})
        favs2 = self.catalog.list_favorites({}, user)[0]
        favs2.sort(key=lambda x: x['timestamp'], reverse=True)
        self.assertEqual(len(favs2), 2)
        self.assertEqual(favs2[0]['module_name_lc'], 'megahit')
        self.assertEqual(favs2[0]['id'], 'run_megahit_2')
        self.assertIsNotNone(favs2[0]['timestamp'])
        # timestamp must increase
        self.assertTrue(favs2[0]['timestamp'] > favs[0]['timestamp'])
        self.assertEqual(favs2[1]['module_name_lc'], 'megahit')
        self.assertEqual(favs2[1]['id'], 'run_megahit')
        self.assertIsNotNone(favs2[1]['timestamp'])

        # add a third favorite of a legacy method without a module
        self.catalog.add_favorite(ctx,
                                  {'id': 'run_fba'})
        favs3 = self.catalog.list_favorites(ctx, user)[0]
        favs3.sort(key=lambda x: x['timestamp'], reverse=True)
        self.assertEqual(len(favs3), 3)
        self.assertEqual(favs3[0]['module_name_lc'], 'nms.legacy')
        self.assertEqual(favs3[0]['id'], 'run_fba')
        self.assertIsNotNone(favs3[0]['timestamp'])

        # remove the second favorite, then there should be two left in the right order
        self.catalog.remove_favorite(ctx,
                                     {'module_name': 'MegaHit', 'id': 'run_megahit_2'})
        favs4 = self.catalog.list_favorites(ctx, user)[0]
        favs4.sort(key=lambda x: x['timestamp'], reverse=True)
        self.assertEqual(len(favs4), 2)
        self.assertEqual(favs4[0]['module_name_lc'], 'nms.legacy')
        self.assertEqual(favs4[0]['id'], 'run_fba')
        self.assertIsNotNone(favs4[0]['timestamp'])
        self.assertEqual(favs4[1]['module_name_lc'], 'megahit')
        self.assertEqual(favs4[1]['id'], 'run_megahit')
        self.assertIsNotNone(favs4[1]['timestamp'])

        # remove the last favorite, then there be one
        self.catalog.remove_favorite(ctx,
                                     {'id': 'run_fba'})
        favs6 = self.catalog.list_favorites(ctx, user)[0]
        self.assertEqual(len(favs6), 1)
        self.assertEqual(favs6[0]['module_name_lc'], 'megahit')
        self.assertEqual(favs6[0]['id'], 'run_megahit')
        self.assertIsNotNone(favs6[0]['timestamp'])

        # let joe add a favorite for megahit too
        self.catalog.add_favorite({'user_id': 'joe'},
                                  {'module_name': 'MegaHit', 'id': 'run_megahit'})

        # get favorites list for the method
        users = \
        self.catalog.list_app_favorites({}, {'module_name': 'MegaHit', 'id': 'run_megahit'})[0]
        self.assertEqual(len(users), 2)

        fav_counts = self.catalog.list_favorite_counts({}, {})[0]
        found = False
        for f in fav_counts:
            if f['module_name_lc'] + '/' + f['id'] == 'megahit/run_megahit':
                found = True
                self.assertEqual(f['count'], 2)
        self.assertTrue(found)

        # get favorites only for megahit
        fav_counts = self.catalog.list_favorite_counts({}, {'modules': ['megAhit']})[0]
        for f in fav_counts:
            self.assertEqual(f['module_name_lc'], 'megahit')

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING basic_catalog_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.')  # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()
