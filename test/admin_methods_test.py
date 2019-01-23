import unittest

from biokbase.catalog.Impl import Catalog
from catalog_test_util import CatalogTestUtil


class AdminMethodsTest(unittest.TestCase):


    def test_is_admin(self):

        madeUpName = 'asdfasdf'
        userName = self.cUtil.user_ctx()['user_id']
        adminName = self.cUtil.admin_ctx()['user_id']

        ctx = self.cUtil.anonymous_ctx()

        self.assertEqual(self.catalog.is_admin(ctx, madeUpName)[0],0)
        self.assertEqual(self.catalog.is_admin(ctx, userName)[0],0)
        self.assertEqual(self.catalog.is_admin(ctx, adminName)[0],1)


    # assumes no developers have been added yet
    def test_add_remove_developers(self):

        # nothing there yet
        devs = self.catalog.list_approved_developers(self.cUtil.anonymous_ctx())[0]
        self.assertEqual(devs,[])
        is_approved = self.catalog.is_approved_developer([],self.cUtil.anonymous_ctx())[0]
        self.assertEqual(is_approved,[])
        is_approved = self.catalog.is_approved_developer(self.cUtil.anonymous_ctx(),
            ['somebody','otherperson'])[0]
        self.assertEqual(is_approved,[0,0])

        # add somebody fails without admin user
        with self.assertRaises(ValueError) as e:
            self.catalog.approve_developer(self.cUtil.user_ctx(),'alice')
        self.assertEqual(str(e.exception),
            'Only Admin users can approve or revoke developers.');
        with self.assertRaises(ValueError) as e:
            # should fail if we specified something empty
            self.catalog.approve_developer(self.cUtil.admin_ctx(),' ')
        self.assertEqual(str(e.exception),
            'No username provided');

        # add some users
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'eve')
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'alice')
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'bob')
        self.catalog.approve_developer(self.cUtil.admin_ctx(),'bob') # should be able to add again without error
        devs = self.catalog.list_approved_developers(self.cUtil.anonymous_ctx())[0]
        self.assertEqual(devs,['alice','bob','eve']) # should be sorted
        is_approved = self.catalog.is_approved_developer(self.cUtil.anonymous_ctx(),
            ['somebody','alice','otherperson','bob','bob'])[0]
        self.assertEqual(is_approved,[0,1,0,1,1])

        # remove some
        with self.assertRaises(ValueError) as e:
            # should fail, only admins can revoke users
            self.catalog.revoke_developer(self.cUtil.user_ctx(),'alice')
        self.assertEqual(str(e.exception),
            'Only Admin users can approve or revoke developers.');
        with self.assertRaises(ValueError) as e:
            # should fail if we misspelled a name
            self.catalog.revoke_developer(self.cUtil.admin_ctx(),'b0b')
        self.assertEqual(str(e.exception),
            'Cannot revoke "b0b", that developer was not found.');
        with self.assertRaises(ValueError) as e:
            # should fail if we specified something empty
            self.catalog.revoke_developer(self.cUtil.admin_ctx(),' ')
        self.assertEqual(str(e.exception),
            'No username provided');
        self.catalog.revoke_developer(self.cUtil.admin_ctx(),'alice')

        # should have truncated list
        devs = self.catalog.list_approved_developers(self.cUtil.anonymous_ctx())[0]
        self.assertEqual(devs,['bob','eve']) # should be sorted
        is_approved = self.catalog.is_approved_developer(self.cUtil.anonymous_ctx(),
            ['somebody','alice','otherperson','bob','bob'])[0]
        self.assertEqual(is_approved,[0,0,0,1,1])

        # should block registration for non-developers
        with self.assertRaises(ValueError) as e:
            self.catalog.register_repo(self.cUtil.user_ctx(),
                {'git_url':self.cUtil.get_test_repo_1()})
        self.assertEqual(str(e.exception),
            'You are not an approved developer.  Contact us via http://kbase.us/contact-us/ to request approval.');

        # after the developer is added, should be allowed to start now (give a bogus url so if finishes registration
        # right away with an error
        self.catalog.approve_developer(self.cUtil.admin_ctx(),self.cUtil.test_user_1)
        self.catalog.register_repo(self.cUtil.user_ctx(),{'git_url':self.cUtil.get_test_repo_1(),'commit_hash':'0760f1927f74a'})
        while True:
            state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),{'git_url':self.cUtil.get_test_repo_1()})[0]
            if state['registration'] in ['complete','error']:
                break


    def test_migrate_module_to_new_git_url(self):

        params = {
            'module_name':"release_history",
            'current_git_url':"https://github.com/kbaseIncubator/release_history",
            'new_git_url':"https://github.com/kbase/release_history"
        }
        # first make sure we can find a module with this name and url
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':params['module_name'],
             'git_url':params['current_git_url']})[0]
        self.assertEqual(info['module_name'],params['module_name'])
        self.assertEqual(info['git_url'],params['current_git_url'])
        self.assertEqual(info['language'],'python')

        # next make sure we get an error if we are not an admin
        with self.assertRaises(ValueError) as e:
            self.catalog.migrate_module_to_new_git_url(self.cUtil.user_ctx(),params)
        self.assertEqual(str(e.exception),
            'Only Admin users can migrate module git urls.');

        # if we are an admin, then it should work
        self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)

        # the old record should not be retrievable by that url anymore
        with self.assertRaises(ValueError) as e:
            self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
                {'module_name':params['module_name'],
                 'git_url':params['current_git_url']})[0]
        self.assertEqual(str(e.exception),
            'Operation failed - module/repo is not registered.');
        # but the new url should work
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':params['module_name'],
             'git_url':params['new_git_url']})[0]
        self.assertEqual(info['module_name'],params['module_name'])
        self.assertEqual(info['git_url'],params['new_git_url'])
        self.assertEqual(info['language'],'python')

        # things should fail if we just try again
        with self.assertRaises(ValueError) as e:
            self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)
        self.assertEqual(str(e.exception),
            'Cannot migrate git_url, no module found with the given name and current url.');
        # or if the new url is not valid
        params['current_git_url'] = params['new_git_url']
        params['new_git_url'] = "http:not_a_url"
        with self.assertRaises(ValueError) as e:
            self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)
        self.assertEqual(str(e.exception),
            'The new git url is not a valid URL.');

        # but we should be able to switch back
        params['new_git_url'] = "https://github.com/kbaseIncubator/release_history"
        self.catalog.migrate_module_to_new_git_url(self.cUtil.admin_ctx(),params)
        info = self.catalog.get_module_info(self.cUtil.anonymous_ctx(),
            {'module_name':params['module_name']})[0]
        self.assertEqual(info['module_name'],params['module_name'])
        self.assertEqual(info['git_url'],params['new_git_url'])
        self.assertEqual(info['language'],'python')


    # Method migrated to core registration test, as this needs a fresh registration to test with NMS
    # def test_active_inactive_setting(self):

    #     # next make sure we get an error if we are not an admin
    #     params = { 'module_name':"release_history" }
    #     with self.assertRaises(ValueError) as e:
    #         self.catalog.set_to_active(self.cUtil.user_ctx(),params)
    #     self.assertEqual(str(e.exception),
    #         'Only Admin users can set a module to be active/inactive.');
    #     with self.assertRaises(ValueError) as e:
    #         self.catalog.set_to_inactive(self.cUtil.user_ctx(),params)
    #     self.assertEqual(str(e.exception),
    #         'Only Admin users can set a module to be active/inactive.');

    #     # release_history module is active, but it should be fine to set it again
    #     self.catalog.set_to_active(self.cUtil.admin_ctx(),params)
    #     state = self.catalog.get_module_state(self.cUtil.admin_ctx(),params)[0]
    #     self.assertEqual(state['active'],1)

    #     # make it inactive (calling twice should be ok and shouldn't change anything)
    #     self.catalog.set_to_inactive(self.cUtil.admin_ctx(),params)
    #     state = self.catalog.get_module_state(self.cUtil.user_ctx(),params)[0]
    #     self.assertEqual(state['active'],0)

    #     self.catalog.set_to_inactive(self.cUtil.admin_ctx(),params)
    #     state = self.catalog.get_module_state(self.cUtil.user_ctx(),params)[0]
    #     self.assertEqual(state['active'],0)

    #     # these still shouldn't work
    #     with self.assertRaises(ValueError) as e:
    #         self.catalog.set_to_active(self.cUtil.user_ctx(),params)
    #     self.assertEqual(str(e.exception),
    #         'Only Admin users can set a module to be active/inactive.');
    #     with self.assertRaises(ValueError) as e:
    #         self.catalog.set_to_inactive(self.cUtil.user_ctx(),params)
    #     self.assertEqual(str(e.exception),
    #         'Only Admin users can set a module to be active/inactive.');

    #     # make it active one more time for kicks
    #     self.catalog.set_to_active(self.cUtil.admin_ctx(),params)
    #     state = self.catalog.get_module_state(self.cUtil.anonymous_ctx(),params)[0]
    #     self.assertEqual(state['active'],1)



    def test_set_registration_state(self):

        # first make sure the state is what we expect
        repoSelectionParam = { 'module_name' : 'registration_in_progress' }
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),repoSelectionParam)[0]
        self.assertEqual(state['registration'],'building: doing stuff')
        self.assertEqual(state['error_message'],'')

        # throw an error- users should not be able to update state
        params = { 'module_name' : 'registration_in_progress', 'registration_state':'complete' }
        with self.assertRaises(ValueError) as e:
            self.catalog.set_registration_state(self.cUtil.user_ctx(),params)
        self.assertEqual(str(e.exception),
            'You do not have permission to modify the registration state of this module/repo.');

        # state should still be the same
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),repoSelectionParam)[0]
        self.assertEqual(state['registration'],'building: doing stuff')
        self.assertEqual(state['error_message'],'')

        # admin can update the registration state to complete
        self.catalog.set_registration_state(self.cUtil.admin_ctx(),params)
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),repoSelectionParam)[0]
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['error_message'],'')

        # admin cannot set the state to error without an error message
        params = { 'module_name' : 'registration_in_progress', 'registration_state':'error' }
        with self.assertRaises(ValueError) as e:
            self.catalog.set_registration_state(self.cUtil.admin_ctx(),params)
        self.assertEqual(str(e.exception),
            'Update failed - if state is "error", you must also set an "error_message".');
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),repoSelectionParam)[0]
        self.assertEqual(state['registration'],'complete')
        self.assertEqual(state['error_message'],'')

        params = { 'module_name' : 'registration_in_progress', 'registration_state':'error', 'error_message':'something' }
        self.catalog.set_registration_state(self.cUtil.admin_ctx(),params)
        state = self.catalog.get_module_state(self.cUtil.user_ctx(),repoSelectionParam)[0]
        self.assertEqual(state['registration'],'error')
        self.assertEqual(state['error_message'],'something')


    @classmethod
    def setUpClass(cls):
        print('++++++++++++ RUNNING admin_methods_test.py +++++++++++')
        cls.cUtil = CatalogTestUtil('.') # TODO: pass in test directory from outside
        cls.cUtil.setUp()
        cls.catalog = Catalog(cls.cUtil.getCatalogConfig())
        print('ready')

    @classmethod
    def tearDownClass(cls):
        cls.cUtil.tearDown()




