import unittest
from biokbase.catalog.Impl import Catalog
from biokbase.narrative_method_store.client import NarrativeMethodStore
from catalog_test_util import CatalogTestUtil
from biokbase.catalog.baseclient import ServerError

class AppEstimatorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        print('++++++++++++ RUNNING core_registration_test.py +++++++++++')

        cls.cUtil = CatalogTestUtil('.')  # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        # approve developers we will use
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(), cls.cUtil.admin_ctx()['user_id'])
        cls.catalog.approve_developer(cls.cUtil.admin_ctx(), cls.cUtil.user_ctx()['user_id'])

        cls.nms = NarrativeMethodStore(cls.cUtil.getCatalogConfig()['nms-url'])

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()

    def test_get_estimator_null(self):
        app_id = "test_method_1"
        res = self.catalog.get_app_resource_estimator(self.cUtil.user_ctx(), {
            "app_id": app_id
        })[0]
        self.assertIsNone(res.get("estimator_module"))
        self.assertIsNone(res.get("estimator_method"))
        self.assertIsNone(res.get("tag"))

    def test_get_estimator_fail(self):
        app_id = "not_real"
        with self.assertRaises(ValueError) as e:
            self.catalog.get_app_resource_estimator(self.cUtil.user_ctx(), {
                "app_id": app_id
            })
        self.assertIn(f"App {app_id} with tag release doesn't seem to exist.", str(e.exception))

    def test_get_estimator(self):
        app_id = "test_method_11"
        res = self.catalog.get_app_resource_estimator(self.cUtil.user_ctx(), {
            "app_id": app_id
        })[0]
        self.assertEqual(res.get("estimator_module"), "SomeService")
        self.assertEqual(res.get("estimator_method"), "estimator_method")
        self.assertEqual(res.get("tag"), "release")
