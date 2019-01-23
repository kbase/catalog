import random
import unittest

from biokbase.catalog.Impl import Catalog
from catalog_test_util import CatalogTestUtil


# tests all the basic get methods
class BasicCatalogTest(unittest.TestCase):
    def test_stats_permissions(self):
        # tests to make sure normal users cannot log stats nor get raw stats
        
        usrCtx = self.cUtil.user_ctx()

        with self.assertRaises(ValueError) as e:
            self.catalog.log_exec_stats(usrCtx, {})
        self.assertEqual(str(e.exception),
            'You do not have permission to log execution statistics.');

        with self.assertRaises(ValueError) as e:
            self.catalog.get_exec_raw_stats(usrCtx, {})
        self.assertEqual(str(e.exception),
            'You do not have permission to view this data.');

        with self.assertRaises(ValueError) as e:
            self.catalog.get_exec_aggr_table(usrCtx, {})
        self.assertEqual(str(e.exception),
            'You do not have permission to view this data.');

    def test_stats(self):

        usrCtx = self.cUtil.user_ctx()
        adminCtx = self.cUtil.admin_ctx()

        # load a bunch of stats
        runs = [
            {
                'app_module_name': 'FBA',
                'app_id': 'run_stuff',
                'func_module_name': 'FBA',
                'func_name': 'run_fba',
                'git_commit_hash': 'bad08fca768099aa5313162f05f49b5b39b478f1'
            },
            {
                'app_module_name': 'FBA',
                'app_id': 'run_other_stuff',
                'func_module_name': 'FBA',
                'func_name': 'run_fba',
                'git_commit_hash': '2842af53c7c411bc2a3833c1e35a4b005304f1c7'
            },
            {
                'app_module_name': 'Megahit',
                'app_id': 'run_megahit',
                'func_module_name': 'Megahit',
                'func_name': 'run_megahit',
                'git_commit_hash': '5f0b15618aa7735bd32250713943fc3371335c43'
            },
            {
                'app_module_name': '',
                'app_id': '',
                'func_module_name': 'GenomeUtil',
                'func_name': 'map_genes',
                'git_commit_hash': 'be4576c47fbe85930309fb9010c378ebb5bfc930'
            },
            {
                'app_module_name': 'GenomeUtil',
                'app_id': 'map_genes',
                'func_module_name': 'GenomeUtil',
                'func_name': 'map_genes',
                'git_commit_hash': 'be4576c47fbe85930309fb9010c378ebb5bfc930'
            },
            {
                'app_module_name': 'Clustal',
                'app_id': 'run_clustal',
                'func_module_name': 'Clustal',
                'func_name': 'run_clustal',
                'git_commit_hash': 'ed1a4382d47d9c9bc1c2b7acf287ee95a08509ce'
            }
        ]

        # random name generator!
        users = ['randel', 'seth', 'jimmie', 'maranda', 'tresa', 'ezra', 'emil', 'anita', 'melissa', 'anna'] 

        # records: each row generates a certain number of runs per user/run started between start and end
        # u= user index, r=run index, n=number, s=first start time, e=last start time
        stats_to_add = [
            {'u':0, 'r':0, 'n_success': 50, 'n_error':5, 's':1461177126, 'e':1461349950},
            {'u':0, 'r':1, 'n_success': 10, 'n_error':1, 's':1461177126, 'e':1461349950},
            {'u':0, 'r':2, 'n_success': 120,'n_error':0, 's':1461177126, 'e':1461349950},
            {'u':0, 'r':4, 'n_success': 2,  'n_error':8, 's':1461177126, 'e':1461349950},
            {'u':0, 'r':5, 'n_success': 20, 'n_error':1, 's':1461177126, 'e':1461349950},
            {'u':1, 'r':3, 'n_success': 20, 'n_error':0, 's':1461170000, 'e':1461170100}
        ]

        start_delay = 50
        end_delay = 500

        total_success = 0
        total_error = 0
        weird_job_id = "test_job_12345"
        for s in stats_to_add:
            #typedef structure {
            #    string user_id;
            #    string app_module_name;
            #    string app_id;
            #    string func_module_name;
            #    string func_name;
            #    string git_commit_hash;
            #    float creation_time;
            #    float exec_start_time;
            #    float finish_time;
            #    boolean is_error;
            #} LogExecStatsParams;
            record = {
                'user_id': users[s['u']],
                'app_module_name': runs[s['r']]['app_module_name'],
                'app_id': runs[s['r']]['app_id'],
                'func_module_name': runs[s['r']]['func_module_name'],
                'func_name': runs[s['r']]['func_name'],
                'git_commit_hash': runs[s['r']]['git_commit_hash']
            }
            total_success += s['n_success']
            for n in range(0,s['n_success']):
                record['is_error'] = 0
                record['creation_time'] = random.randint(s['s'], s['e'])
                record['exec_start_time'] = record['creation_time'] + start_delay
                record['finish_time'] = record['exec_start_time'] + end_delay
                if s['s'] > 1461169999 and s['s'] < 1461170101:
                    record['job_id'] = weird_job_id
                self.catalog.log_exec_stats(adminCtx, record)
            total_error += s['n_error']
            for n in range(0,s['n_error']):
                record['is_error'] = 1
                record['creation_time'] = random.randint(s['s'], s['e'])
                record['exec_start_time'] = record['creation_time'] + start_delay
                record['finish_time'] = record['exec_start_time'] + end_delay
                self.catalog.log_exec_stats(adminCtx, record)

        # make sure we get the correct results
        # make sure all the stats we added appear in the raw stats:
        all_stats = self.catalog.get_exec_raw_stats(adminCtx, {})[0]
        self.assertEqual(len(all_stats), total_success + total_error)

        e_count = 0
        s_count = 0
        for s in all_stats:
            if s['is_error']:
                e_count+=1
            else:
                s_count+=1

        self.assertEqual(e_count, total_error)
        self.assertEqual(s_count, total_success)

        restricted_stats = self.catalog.get_exec_raw_stats(adminCtx, {'begin': 1461169999, 'end': 1461170101})[0]
        self.assertEqual(len(restricted_stats), 20)
        for row in restricted_stats:
            self.assertTrue('job_id' in row)
            self.assertEqual(row['job_id'], weird_job_id)

        # make sure we can get aggregations of things
        stats = self.catalog.get_exec_aggr_stats({}, {})[0]
        self.assertEqual(len(stats), 5)
        foundRunStuff = False
        for s in stats:
            if s['full_app_id'] == 'FBA/run_stuff':
                foundRunStuff = True
                self.assertEqual(s['module_name'], 'FBA')
                self.assertEqual(s['number_of_calls'], 55)
                self.assertEqual(s['number_of_errors'], 5)
                self.assertEqual(s['time_range'], '*')
                self.assertEqual(s['total_exec_time'], 27500)
                self.assertEqual(s['total_queue_time'], 2750)
                self.assertEqual(s['type'], 'a')

        self.assertTrue(foundRunStuff)

        stats = self.catalog.get_exec_aggr_table(adminCtx,{})[0]
        self.assertEqual(len(stats), 6)
        foundRandelClustalRuns = True
        for s in stats:
            if s['app'] == 'Clustal/run_clustal' and s['user'] == 'randel':
                self.assertEqual(s['n'],21)
                foundRandelClustalRuns = True
        self.assertTrue(foundRandelClustalRuns)

    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING execution_stats_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




