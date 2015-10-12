#BEGIN_HEADER
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
        #END_CONSTRUCTOR
        pass

    def is_repo_registered(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN is_repo_registered
        #END is_repo_registered

        # At some point might do deeper type checking...
        if not isinstance(returnVal, int):
            raise ValueError('Method is_repo_registered return value ' +
                             'returnVal is not type int as required.')
        # return the results
        return [returnVal]

    def register_repo(self, ctx, params):
        # ctx is the context object
        # return variables are: timestamp
        #BEGIN register_repo
        #END register_repo

        # At some point might do deeper type checking...
        if not isinstance(timestamp, int):
            raise ValueError('Method register_repo return value ' +
                             'timestamp is not type int as required.')
        # return the results
        return [timestamp]

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

    def list_repo_module_names(self, ctx, params):
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN list_repo_module_names
        #END list_repo_module_names

        # At some point might do deeper type checking...
        if not isinstance(returnVal, list):
            raise ValueError('Method list_repo_module_names return value ' +
                             'returnVal is not type list as required.')
        # return the results
        return [returnVal]

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

    def set_repo_state(self, ctx, params):
        # ctx is the context object
        #BEGIN set_repo_state
        #END set_repo_state
        pass

    def get_repo_state(self, ctx, params):
        # ctx is the context object
        # return variables are: state
        #BEGIN get_repo_state
        #END get_repo_state

        # At some point might do deeper type checking...
        if not isinstance(state, basestring):
            raise ValueError('Method get_repo_state return value ' +
                             'state is not type basestring as required.')
        # return the results
        return [state]
