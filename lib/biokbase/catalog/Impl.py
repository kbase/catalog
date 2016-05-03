#BEGIN_HEADER
from pprint import pprint
from biokbase.catalog.controller import CatalogController
#END_HEADER


class Catalog:
    '''
    Module Name:
    Catalog

    Module Description:
    Service for managing, registering, and building KBase Modules using the KBase SDK.
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbase/catalog"
    GIT_COMMIT_HASH = "2680a67555978f68a050dc52ee7791bae2b89220"
    
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        print('Starting the Catalog service.  Service configuration:')
        for c in config:
            if c == 'nms-admin-psswd':
                print('  '+c+'=****')
                continue
            print('  '+c+'='+config[c])
        print('Initializing the Catalog Controller...')
        self.cc = CatalogController(config);
        print('Initialization complete.')
        #END_CONSTRUCTOR
        pass
    

    def version(self, ctx):
        # ctx is the context object
        # return variables are: version
        #BEGIN version
        version = self.cc.version()
        #END version

        # At some point might do deeper type checking...
        if not isinstance(version, basestring):
            raise ValueError('Method version return value ' +
                             'version is not type basestring as required.')
        # return the results
        return [version]

    def is_registered(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN is_registered
        returnVal = 0
        is_registered = self.cc.is_registered(params)
        if is_registered:
            returnVal = 1
        #END is_registered

        # At some point might do deeper type checking...
        if not isinstance(returnVal, int):
            raise ValueError('Method is_registered return value ' +
                             'returnVal is not type int as required.')
        # return the results
        return [returnVal]

    def register_repo(self, ctx, params):
        # ctx is the context object
        # return variables are: registration_id
        #BEGIN register_repo
        registration_id = self.cc.register_repo(params, ctx['user_id'], ctx['token'])
        #END register_repo

        # At some point might do deeper type checking...
        if not isinstance(registration_id, basestring):
            raise ValueError('Method register_repo return value ' +
                             'registration_id is not type basestring as required.')
        # return the results
        return [registration_id]

    def push_dev_to_beta(self, ctx, params):
        # ctx is the context object
        #BEGIN push_dev_to_beta
        self.cc.push_dev_to_beta(params,ctx['user_id'])
        #END push_dev_to_beta
        pass

    def request_release(self, ctx, params):
        # ctx is the context object
        #BEGIN request_release
        self.cc.request_release(params,ctx['user_id'])
        #END request_release
        pass

    def list_requested_releases(self, ctx):
        # ctx is the context object
        # return variables are: requested_releases
        #BEGIN list_requested_releases
        requested_releases = self.cc.list_requested_releases()
        #END list_requested_releases

        # At some point might do deeper type checking...
        if not isinstance(requested_releases, list):
            raise ValueError('Method list_requested_releases return value ' +
                             'requested_releases is not type list as required.')
        # return the results
        return [requested_releases]

    def review_release_request(self, ctx, review):
        # ctx is the context object
        #BEGIN review_release_request
        self.cc.review_release_request(review, ctx['user_id'])
        #END review_release_request
        pass

    def list_basic_module_info(self, ctx, params):
        # ctx is the context object
        # return variables are: info_list
        #BEGIN list_basic_module_info
        info_list = self.cc.list_basic_module_info(params)
        #END list_basic_module_info

        # At some point might do deeper type checking...
        if not isinstance(info_list, list):
            raise ValueError('Method list_basic_module_info return value ' +
                             'info_list is not type list as required.')
        # return the results
        return [info_list]

    def add_favorite(self, ctx, params):
        # ctx is the context object
        #BEGIN add_favorite
        self.cc.add_favorite(params,ctx['user_id'])
        #END add_favorite
        pass

    def remove_favorite(self, ctx, params):
        # ctx is the context object
        #BEGIN remove_favorite
        self.cc.remove_favorite(params,ctx['user_id'])
        #END remove_favorite
        pass

    def list_favorites(self, ctx, username):
        # ctx is the context object
        # return variables are: favorites
        #BEGIN list_favorites
        favorites = self.cc.list_user_favorites(username)
        #END list_favorites

        # At some point might do deeper type checking...
        if not isinstance(favorites, list):
            raise ValueError('Method list_favorites return value ' +
                             'favorites is not type list as required.')
        # return the results
        return [favorites]

    def list_app_favorites(self, ctx, item):
        # ctx is the context object
        # return variables are: users
        #BEGIN list_app_favorites
        users = self.cc.list_app_favorites(item)
        #END list_app_favorites

        # At some point might do deeper type checking...
        if not isinstance(users, list):
            raise ValueError('Method list_app_favorites return value ' +
                             'users is not type list as required.')
        # return the results
        return [users]

    def list_favorite_counts(self, ctx, params):
        # ctx is the context object
        # return variables are: counts
        #BEGIN list_favorite_counts
        counts = self.cc.aggregate_favorites_over_apps(params)
        #END list_favorite_counts

        # At some point might do deeper type checking...
        if not isinstance(counts, list):
            raise ValueError('Method list_favorite_counts return value ' +
                             'counts is not type list as required.')
        # return the results
        return [counts]

    def get_module_info(self, ctx, selection):
        # ctx is the context object
        # return variables are: info
        #BEGIN get_module_info
        info = self.cc.get_module_info(selection);
        #END get_module_info

        # At some point might do deeper type checking...
        if not isinstance(info, dict):
            raise ValueError('Method get_module_info return value ' +
                             'info is not type dict as required.')
        # return the results
        return [info]

    def get_version_info(self, ctx, params):
        # ctx is the context object
        # return variables are: version
        #BEGIN get_version_info
        version = self.cc.get_version_info(params)
        if version is None:
            raise ValueError("No version found that matches all your criteria!")
        #END get_version_info

        # At some point might do deeper type checking...
        if not isinstance(version, dict):
            raise ValueError('Method get_version_info return value ' +
                             'version is not type dict as required.')
        # return the results
        return [version]

    def list_released_module_versions(self, ctx, params):
        # ctx is the context object
        # return variables are: versions
        #BEGIN list_released_module_versions
        versions = self.cc.list_released_versions(params)
        #END list_released_module_versions

        # At some point might do deeper type checking...
        if not isinstance(versions, list):
            raise ValueError('Method list_released_module_versions return value ' +
                             'versions is not type list as required.')
        # return the results
        return [versions]

    def module_version_lookup(self, ctx, selection):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN module_version_lookup
        returnVal = self.cc.module_version_lookup(selection)
        #END module_version_lookup

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method module_version_lookup return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def list_service_modules(self, ctx, filter):
        # ctx is the context object
        # return variables are: service_modules
        #BEGIN list_service_modules
        service_modules = self.cc.list_service_modules(filter)
        #END list_service_modules

        # At some point might do deeper type checking...
        if not isinstance(service_modules, list):
            raise ValueError('Method list_service_modules return value ' +
                             'service_modules is not type list as required.')
        # return the results
        return [service_modules]

    def set_registration_state(self, ctx, params):
        # ctx is the context object
        #BEGIN set_registration_state
        self.cc.set_registration_state(params, ctx['user_id'])
        #END set_registration_state
        pass

    def get_module_state(self, ctx, params):
        # ctx is the context object
        # return variables are: state
        #BEGIN get_module_state
        state = self.cc.get_module_state(params)
        # make sure booleans are converted to numeric values for KBase compatibility
        if state['active']:
            state['active']=1
        else:
            state['active']=0
        if 'released' in state:
            if state['released']:
                state['released']=1
            else:
                state['released']=0
        else:
            state['released']=0
        #END get_module_state

        # At some point might do deeper type checking...
        if not isinstance(state, dict):
            raise ValueError('Method get_module_state return value ' +
                             'state is not type dict as required.')
        # return the results
        return [state]

    def get_build_log(self, ctx, registration_id):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_build_log
        returnVal = self.cc.get_build_log(registration_id)
        #END get_build_log

        # At some point might do deeper type checking...
        if not isinstance(returnVal, basestring):
            raise ValueError('Method get_build_log return value ' +
                             'returnVal is not type basestring as required.')
        # return the results
        return [returnVal]

    def get_parsed_build_log(self, ctx, params):
        # ctx is the context object
        # return variables are: build_log
        #BEGIN get_parsed_build_log
        build_log = self.cc.get_parsed_build_log(params)
        #END get_parsed_build_log

        # At some point might do deeper type checking...
        if not isinstance(build_log, dict):
            raise ValueError('Method get_parsed_build_log return value ' +
                             'build_log is not type dict as required.')
        # return the results
        return [build_log]

    def list_builds(self, ctx, params):
        # ctx is the context object
        # return variables are: builds
        #BEGIN list_builds
        builds = self.cc.list_builds(params)
        #END list_builds

        # At some point might do deeper type checking...
        if not isinstance(builds, list):
            raise ValueError('Method list_builds return value ' +
                             'builds is not type list as required.')
        # return the results
        return [builds]

    def delete_module(self, ctx, params):
        # ctx is the context object
        #BEGIN delete_module
        self.cc.delete_module(params,ctx['user_id'])
        #END delete_module
        pass

    def migrate_module_to_new_git_url(self, ctx, params):
        # ctx is the context object
        #BEGIN migrate_module_to_new_git_url
        self.cc.migrate_module_to_new_git_url(params,ctx['user_id'])
        #END migrate_module_to_new_git_url
        pass

    def set_to_active(self, ctx, params):
        # ctx is the context object
        #BEGIN set_to_active
        self.cc.set_module_active_state(True, params, ctx['user_id'])
        #END set_to_active
        pass

    def set_to_inactive(self, ctx, params):
        # ctx is the context object
        #BEGIN set_to_inactive
        self.cc.set_module_active_state(False, params, ctx['user_id'])
        #END set_to_inactive
        pass

    def is_approved_developer(self, ctx, usernames):
        # ctx is the context object
        # return variables are: is_approved
        #BEGIN is_approved_developer
        is_approved_bool = self.cc.is_approved_developer(usernames)
        is_approved = [] # convert to longs for correct RPC mapping
        for k in is_approved_bool:
            if(k):
                is_approved.append(1)
            else:
                is_approved.append(0)
        #END is_approved_developer

        # At some point might do deeper type checking...
        if not isinstance(is_approved, list):
            raise ValueError('Method is_approved_developer return value ' +
                             'is_approved is not type list as required.')
        # return the results
        return [is_approved]

    def list_approved_developers(self, ctx):
        # ctx is the context object
        # return variables are: usernames
        #BEGIN list_approved_developers
        usernames = self.cc.list_approved_developers()
        #END list_approved_developers

        # At some point might do deeper type checking...
        if not isinstance(usernames, list):
            raise ValueError('Method list_approved_developers return value ' +
                             'usernames is not type list as required.')
        # return the results
        return [usernames]

    def approve_developer(self, ctx, username):
        # ctx is the context object
        #BEGIN approve_developer
        usernames = self.cc.approve_developer(username, ctx['user_id'])
        #END approve_developer
        pass

    def revoke_developer(self, ctx, username):
        # ctx is the context object
        #BEGIN revoke_developer
        usernames = self.cc.revoke_developer(username, ctx['user_id'])
        #END revoke_developer
        pass

    def log_exec_stats(self, ctx, params):
        # ctx is the context object
        #BEGIN log_exec_stats
        admin_user_id = ctx['user_id']
        if not self.cc.is_admin(admin_user_id):
            raise ValueError('You do not have permission to log execution statistics.')
        user_id = params['user_id']
        app_module_name = None if 'app_module_name' not in params else params['app_module_name']
        app_id = None if 'app_id' not in params else params['app_id']
        func_module_name = None if 'func_module_name' not in params else params['func_module_name']
        func_name = params['func_name']
        git_commit_hash = None if 'git_commit_hash' not in params else params['git_commit_hash']
        creation_time = params['creation_time']
        exec_start_time = params['exec_start_time']
        finish_time = params['finish_time']
        is_error = params['is_error'] != 0
        self.cc.log_exec_stats(admin_user_id, user_id, app_module_name, app_id, func_module_name,
                               func_name, git_commit_hash, creation_time, exec_start_time, 
                               finish_time, is_error)
        #END log_exec_stats
        pass

    def get_exec_aggr_stats(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_exec_aggr_stats
        full_app_ids = None if 'full_app_ids' not in params else params['full_app_ids']
        per_week = False if 'per_week' not in params else params['per_week'] != 0
        returnVal = self.cc.get_exec_aggr_stats(full_app_ids, per_week)
        #END get_exec_aggr_stats

        # At some point might do deeper type checking...
        if not isinstance(returnVal, list):
            raise ValueError('Method get_exec_aggr_stats return value ' +
                             'returnVal is not type list as required.')
        # return the results
        return [returnVal]

    def get_exec_aggr_table(self, ctx, params):
        # ctx is the context object
        # return variables are: table
        #BEGIN get_exec_aggr_table
        table = self.cc.get_exec_aggr_table(ctx['user_id'], params)
        #END get_exec_aggr_table

        # At some point might do deeper type checking...
        if not isinstance(table, object):
            raise ValueError('Method get_exec_aggr_table return value ' +
                             'table is not type object as required.')
        # return the results
        return [table]

    def get_exec_raw_stats(self, ctx, params):
        # ctx is the context object
        # return variables are: records
        #BEGIN get_exec_raw_stats
        records = self.cc.get_exec_raw_stats(ctx['user_id'], params)
        #END get_exec_raw_stats

        # At some point might do deeper type checking...
        if not isinstance(records, list):
            raise ValueError('Method get_exec_raw_stats return value ' +
                             'records is not type list as required.')
        # return the results
        return [records]

    def set_client_group(self, ctx, group):
        # ctx is the context object
        #BEGIN set_client_group
        self.cc.set_client_group(ctx['user_id'], group)
        #END set_client_group
        pass

    def get_client_groups(self, ctx, params):
        # ctx is the context object
        # return variables are: groups
        #BEGIN get_client_groups
        groups = self.cc.get_client_groups(params)
        #END get_client_groups

        # At some point might do deeper type checking...
        if not isinstance(groups, list):
            raise ValueError('Method get_client_groups return value ' +
                             'groups is not type list as required.')
        # return the results
        return [groups]

    def is_admin(self, ctx, username):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN is_admin
        returnVal = 0
        if username:
            if self.cc.is_admin(username):
                returnVal = 1
        #END is_admin

        # At some point might do deeper type checking...
        if not isinstance(returnVal, int):
            raise ValueError('Method is_admin return value ' +
                             'returnVal is not type int as required.')
        # return the results
        return [returnVal]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
