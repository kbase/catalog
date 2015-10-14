#BEGIN_HEADER
from pprint import pprint
from biokbase.catalog.controller import CatalogController
#END_HEADER


class Catalog:
    '''
    Module Name:
    Catalog

    Module Description:
    
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        print('Starting the Catalog service.  Service configuration:')
        pprint(config)
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

    def get_repo_last_timestamp(self, ctx, params):
        # ctx is the context object
        # return variables are: timestamp
        #BEGIN get_repo_last_timestamp
        #END get_repo_last_timestamp

        # At some point might do deeper type checking...
        if not isinstance(timestamp, int):
            raise ValueError('Method get_repo_last_timestamp return value ' +
                             'timestamp is not type int as required.')
        # return the results
        return [timestamp]

    def register_repo(self, ctx, params):
        # ctx is the context object
        # return variables are: timestamp
        #BEGIN register_repo
        
        timestamp = self.cc.register_repo(params, ctx['user_id'], ctx['token'])

        #END register_repo

        # At some point might do deeper type checking...
        if not isinstance(timestamp, int):
            raise ValueError('Method register_repo return value ' +
                             'timestamp is not type int as required.')
        # return the results
        return [timestamp]

    def push_dev_to_beta(self, ctx, params):
        # ctx is the context object
        #BEGIN push_dev_to_beta
        #END push_dev_to_beta
        pass

    def request_release(self, ctx, params):
        # ctx is the context object
        #BEGIN request_release
        #END request_release
        pass

    def list_requested_releases(self, ctx):
        # ctx is the context object
        # return variables are: requested_releases
        #BEGIN list_requested_releases
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
        #END review_release_request
        pass

    def list_basic_module_info(self, ctx, params):
        # ctx is the context object
        # return variables are: info_list
        #BEGIN list_basic_module_info
        info_list = self.cc.list_basic_module_info(params)
        print('---')
        pprint(info_list)
        print('+++')
        #END list_basic_module_info

        # At some point might do deeper type checking...
        if not isinstance(info_list, list):
            raise ValueError('Method list_basic_module_info return value ' +
                             'info_list is not type list as required.')
        # return the results
        return [info_list]

    def get_repo_details(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_repo_details
        #END get_repo_details

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method get_repo_details return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]

    def list_repo_versions(self, ctx, params):
        # ctx is the context object
        # return variables are: versions
        #BEGIN list_repo_versions
        #END list_repo_versions

        # At some point might do deeper type checking...
        if not isinstance(versions, list):
            raise ValueError('Method list_repo_versions return value ' +
                             'versions is not type list as required.')
        # return the results
        return [versions]

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

        pprint(state)
        #END get_module_state

        # At some point might do deeper type checking...
        if not isinstance(state, dict):
            raise ValueError('Method get_module_state return value ' +
                             'state is not type dict as required.')
        # return the results
        return [state]
