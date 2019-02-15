# -*- coding: utf-8 -*-
#BEGIN_HEADER
from biokbase.catalog.controller import CatalogController
#END_HEADER


class Catalog:
    '''
    Module Name:
    Catalog

    Module Description:
    Service for managing, registering, and building KBase Modules using the KBase SDK.
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbase/catalog.git"
    GIT_COMMIT_HASH = "83fec5967d709dadf8b7592e98e5b49a2b2cc1e9"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        print('Starting the Catalog service.  Service configuration:')
        for c in config:
            if c == 'nms-admin-token':
                print('  '+c+'=****')
                continue
            print('  '+c+'='+config[c])
        print('Initializing the Catalog Controller...')
        self.cc = CatalogController(config);
        print('Initialization complete.')
        #END_CONSTRUCTOR
        pass

    def version(self, ctx):
        """
        Get the version of the deployed catalog service endpoint.
        :returns: instance of String
        """
        # ctx is the context object
        # return variables are: version
        #BEGIN version
        version = self.cc.version()
        #END version

        # At some point might do deeper type checking...
        if not isinstance(version, str):
            raise ValueError('Method version return value ' +
                             'version is not type str as required.')
        # return the results
        return [version]

    def is_registered(self, ctx, params):
        """
        returns true (1) if the module exists, false (2) otherwise
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        :returns: instance of type "boolean" (@range [0,1])
        """
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
        """
        allow/require developer to supply git branch/git commit tag? 
        if this is a new module, creates the initial registration with the authenticated user as
        the sole owner, then launches a build to update the dev version of the module.  You can check
        the state of this build with the 'get_module_state' method passing in the git_url.  If the module
        already exists, then you must be an owner to reregister.  That will immediately overwrite your
        dev version of the module (old dev versions are not stored, but you can always reregister an old
        version from the repo) and start a build.
        :param params: instance of type "RegisterRepoParams" -> structure:
           parameter "git_url" of String, parameter "git_commit_hash" of
           String
        :returns: instance of String
        """
        # ctx is the context object
        # return variables are: registration_id
        #BEGIN register_repo
        registration_id = self.cc.register_repo(params, ctx.get('user_id'), ctx.get('token'))
        #END register_repo

        # At some point might do deeper type checking...
        if not isinstance(registration_id, str):
            raise ValueError('Method register_repo return value ' +
                             'registration_id is not type str as required.')
        # return the results
        return [registration_id]

    def push_dev_to_beta(self, ctx, params):
        """
        immediately updates the beta tag to what is currently in dev, whatever is currently in beta
        is discarded.  Will fail if a release request is active and has not been approved/denied
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        """
        # ctx is the context object
        #BEGIN push_dev_to_beta
        self.cc.push_dev_to_beta(params, ctx.get('user_id'), ctx.get('token'))
        #END push_dev_to_beta
        pass

    def request_release(self, ctx, params):
        """
        requests a push from beta to release version; must be approved be a kbase Admin
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        """
        # ctx is the context object
        #BEGIN request_release
        self.cc.request_release(params, ctx.get('user_id'), ctx.get('token'))
        #END request_release
        pass

    def list_requested_releases(self, ctx):
        """
        :returns: instance of list of type "RequestedReleaseInfo" ->
           structure: parameter "module_name" of String, parameter "git_url"
           of String, parameter "git_commit_hash" of String, parameter
           "git_commit_message" of String, parameter "timestamp" of Long,
           parameter "owners" of list of String
        """
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
        """
        :param review: instance of type "ReleaseReview" (decision - approved
           | denied review_message -) -> structure: parameter "module_name"
           of String, parameter "git_url" of String, parameter "decision" of
           String, parameter "review_message" of String
        """
        # ctx is the context object
        #BEGIN review_release_request
        self.cc.review_release_request(review,  ctx.get('user_id'), ctx.get('token'))
        #END review_release_request
        pass

    def list_basic_module_info(self, ctx, params):
        """
        :param params: instance of type "ListModuleParams" (Describes how to
           filter repositories. include_released - optional flag indicated
           modules that are released are included (default:true)
           include_unreleased - optional flag indicated modules that are not
           released are included (default:false) with_disabled - optional
           flag indicating disabled repos should be included (default:false).
           include_modules_with_no_name_set - default to 0, if set return
           modules that were never registered successfully (first
           registration failed, never got a module name, but there is a
           git_url)) -> structure: parameter "owners" of list of String,
           parameter "include_released" of type "boolean" (@range [0,1]),
           parameter "include_unreleased" of type "boolean" (@range [0,1]),
           parameter "include_disabled" of type "boolean" (@range [0,1]),
           parameter "include_modules_with_no_name_set" of type "boolean"
           (@range [0,1])
        :returns: instance of list of type "BasicModuleInfo" (git_url is
           always returned.  Every other field may or may not exist depending
           on what has been registered or if certain registrations have
           failed) -> structure: parameter "module_name" of String, parameter
           "git_url" of String, parameter "language" of String, parameter
           "dynamic_service" of type "boolean" (@range [0,1]), parameter
           "owners" of list of String, parameter "dev" of type
           "VersionCommitInfo" -> structure: parameter "git_commit_hash" of
           String, parameter "beta" of type "VersionCommitInfo" -> structure:
           parameter "git_commit_hash" of String, parameter "release" of type
           "VersionCommitInfo" -> structure: parameter "git_commit_hash" of
           String, parameter "released_version_list" of list of type
           "VersionCommitInfo" -> structure: parameter "git_commit_hash" of
           String
        """
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
        """
        :param params: instance of type "FavoriteItem" (FAVORITES!!) ->
           structure: parameter "module_name" of String, parameter "id" of
           String
        """
        # ctx is the context object
        #BEGIN add_favorite
        self.cc.add_favorite(params, ctx.get('user_id'), ctx.get('token'))
        #END add_favorite
        pass

    def remove_favorite(self, ctx, params):
        """
        :param params: instance of type "FavoriteItem" (FAVORITES!!) ->
           structure: parameter "module_name" of String, parameter "id" of
           String
        """
        # ctx is the context object
        #BEGIN remove_favorite
        self.cc.remove_favorite(params, ctx.get('user_id'), ctx.get('token'))
        #END remove_favorite
        pass

    def list_favorites(self, ctx, username):
        """
        :param username: instance of String
        :returns: instance of list of type "FavoriteItem" (FAVORITES!!) ->
           structure: parameter "module_name" of String, parameter "id" of
           String
        """
        # ctx is the context object
        # return variables are: favorites
        #BEGIN list_favorites
        favorites = self.cc.list_user_favorites(username, ctx.get('token'))
        #END list_favorites

        # At some point might do deeper type checking...
        if not isinstance(favorites, list):
            raise ValueError('Method list_favorites return value ' +
                             'favorites is not type list as required.')
        # return the results
        return [favorites]

    def list_app_favorites(self, ctx, item):
        """
        :param item: instance of type "FavoriteItem" (FAVORITES!!) ->
           structure: parameter "module_name" of String, parameter "id" of
           String
        :returns: instance of list of type "FavoriteUser" -> structure:
           parameter "username" of String, parameter "timestamp" of String
        """
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
        """
        :param params: instance of type "ListFavoriteCounts" (if favorite
           item is given, will return stars just for that item.  If a module
           name is given, will return stars for all methods in that module. 
           If none of those are given, then will return stars for every
           method that there is info on parameters to add: list<FavoriteItem>
           items;) -> structure: parameter "modules" of list of String
        :returns: instance of list of type "FavoriteCount" -> structure:
           parameter "module_name" of String, parameter "app_id" of String,
           parameter "count" of Long
        """
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
        """
        :param selection: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        :returns: instance of type "ModuleInfo" -> structure: parameter
           "module_name" of String, parameter "git_url" of String, parameter
           "description" of String, parameter "language" of String, parameter
           "owners" of list of String, parameter "release" of type
           "ModuleVersionInfo" (data_folder - optional field representing
           unique module name (like <module_name> transformed to lower cases)
           used for reference data purposes (see description for data_version
           field). This value will be treated as part of file system path
           relative to the base that comes from the config (currently base is
           supposed to be "/kb/data" defined in "ref-data-base" parameter).
           data_version - optional field, reflects version of data defined in
           kbase.yml (see "data-version" key). In case this field is set data
           folder with path "/kb/data/<data_folder>/<data_version>" should be
           initialized by running docker image with "init" target from
           catalog. And later when async methods are run it should be mounted
           on AWE worker machine into "/data" folder inside docker container
           by execution engine.) -> structure: parameter "timestamp" of Long,
           parameter "registration_id" of String, parameter "version" of
           String, parameter "git_commit_hash" of String, parameter
           "git_commit_message" of String, parameter "dynamic_service" of
           type "boolean" (@range [0,1]), parameter "narrative_method_ids" of
           list of String, parameter "local_function_ids" of list of String,
           parameter "docker_img_name" of String, parameter "data_folder" of
           String, parameter "data_version" of String, parameter
           "compilation_report" of type "CompilationReport" -> structure:
           parameter "module_name" of String, parameter "sdk_version" of
           String, parameter "sdk_git_commit" of String, parameter
           "impl_file_path" of String, parameter "function_places" of mapping
           from String to type "FunctionPlace" -> structure: parameter
           "start_line" of Long, parameter "end_line" of Long, parameter
           "functions" of mapping from String to type "Function" ->
           structure: parameter "name" of String, parameter "comment" of
           String, parameter "place" of type "FunctionPlace" -> structure:
           parameter "start_line" of Long, parameter "end_line" of Long,
           parameter "input" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "output" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "spec_files" of list of type "SpecFile" -> structure:
           parameter "file_name" of String, parameter "content" of String,
           parameter "is_main" of type "boolean" (@range [0,1]), parameter
           "beta" of type "ModuleVersionInfo" (data_folder - optional field
           representing unique module name (like <module_name> transformed to
           lower cases) used for reference data purposes (see description for
           data_version field). This value will be treated as part of file
           system path relative to the base that comes from the config
           (currently base is supposed to be "/kb/data" defined in
           "ref-data-base" parameter). data_version - optional field,
           reflects version of data defined in kbase.yml (see "data-version"
           key). In case this field is set data folder with path
           "/kb/data/<data_folder>/<data_version>" should be initialized by
           running docker image with "init" target from catalog. And later
           when async methods are run it should be mounted on AWE worker
           machine into "/data" folder inside docker container by execution
           engine.) -> structure: parameter "timestamp" of Long, parameter
           "registration_id" of String, parameter "version" of String,
           parameter "git_commit_hash" of String, parameter
           "git_commit_message" of String, parameter "dynamic_service" of
           type "boolean" (@range [0,1]), parameter "narrative_method_ids" of
           list of String, parameter "local_function_ids" of list of String,
           parameter "docker_img_name" of String, parameter "data_folder" of
           String, parameter "data_version" of String, parameter
           "compilation_report" of type "CompilationReport" -> structure:
           parameter "module_name" of String, parameter "sdk_version" of
           String, parameter "sdk_git_commit" of String, parameter
           "impl_file_path" of String, parameter "function_places" of mapping
           from String to type "FunctionPlace" -> structure: parameter
           "start_line" of Long, parameter "end_line" of Long, parameter
           "functions" of mapping from String to type "Function" ->
           structure: parameter "name" of String, parameter "comment" of
           String, parameter "place" of type "FunctionPlace" -> structure:
           parameter "start_line" of Long, parameter "end_line" of Long,
           parameter "input" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "output" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "spec_files" of list of type "SpecFile" -> structure:
           parameter "file_name" of String, parameter "content" of String,
           parameter "is_main" of type "boolean" (@range [0,1]), parameter
           "dev" of type "ModuleVersionInfo" (data_folder - optional field
           representing unique module name (like <module_name> transformed to
           lower cases) used for reference data purposes (see description for
           data_version field). This value will be treated as part of file
           system path relative to the base that comes from the config
           (currently base is supposed to be "/kb/data" defined in
           "ref-data-base" parameter). data_version - optional field,
           reflects version of data defined in kbase.yml (see "data-version"
           key). In case this field is set data folder with path
           "/kb/data/<data_folder>/<data_version>" should be initialized by
           running docker image with "init" target from catalog. And later
           when async methods are run it should be mounted on AWE worker
           machine into "/data" folder inside docker container by execution
           engine.) -> structure: parameter "timestamp" of Long, parameter
           "registration_id" of String, parameter "version" of String,
           parameter "git_commit_hash" of String, parameter
           "git_commit_message" of String, parameter "dynamic_service" of
           type "boolean" (@range [0,1]), parameter "narrative_method_ids" of
           list of String, parameter "local_function_ids" of list of String,
           parameter "docker_img_name" of String, parameter "data_folder" of
           String, parameter "data_version" of String, parameter
           "compilation_report" of type "CompilationReport" -> structure:
           parameter "module_name" of String, parameter "sdk_version" of
           String, parameter "sdk_git_commit" of String, parameter
           "impl_file_path" of String, parameter "function_places" of mapping
           from String to type "FunctionPlace" -> structure: parameter
           "start_line" of Long, parameter "end_line" of Long, parameter
           "functions" of mapping from String to type "Function" ->
           structure: parameter "name" of String, parameter "comment" of
           String, parameter "place" of type "FunctionPlace" -> structure:
           parameter "start_line" of Long, parameter "end_line" of Long,
           parameter "input" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "output" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "spec_files" of list of type "SpecFile" -> structure:
           parameter "file_name" of String, parameter "content" of String,
           parameter "is_main" of type "boolean" (@range [0,1])
        """
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
        """
        DEPRECATED!!!  use get_module_version
        :param params: instance of type "SelectModuleVersionParams" (only
           required: module_name or git_url, the rest are optional selectors
           If no selectors given, returns current release version version is
           one of: release | beta | dev old release versions can only be
           retrieved individually by timestamp or git_commit_hash Note: this
           method isn't particularly smart or effecient yet, because it pulls
           the info for a particular module first, then searches in code for
           matches to the relevant query.  Instead, this should be performed
           on the database side through queries.  Will optimize when this
           becomes an issue. In the future, this will be extended so that you
           can retrieve version info by only timestamp, git commit, etc, but
           the necessary indicies have not been setup yet.  In general, we
           will need to add better search capabilities) -> structure:
           parameter "module_name" of String, parameter "git_url" of String,
           parameter "timestamp" of Long, parameter "git_commit_hash" of
           String, parameter "version" of String
        :returns: instance of type "ModuleVersionInfo" (data_folder -
           optional field representing unique module name (like <module_name>
           transformed to lower cases) used for reference data purposes (see
           description for data_version field). This value will be treated as
           part of file system path relative to the base that comes from the
           config (currently base is supposed to be "/kb/data" defined in
           "ref-data-base" parameter). data_version - optional field,
           reflects version of data defined in kbase.yml (see "data-version"
           key). In case this field is set data folder with path
           "/kb/data/<data_folder>/<data_version>" should be initialized by
           running docker image with "init" target from catalog. And later
           when async methods are run it should be mounted on AWE worker
           machine into "/data" folder inside docker container by execution
           engine.) -> structure: parameter "timestamp" of Long, parameter
           "registration_id" of String, parameter "version" of String,
           parameter "git_commit_hash" of String, parameter
           "git_commit_message" of String, parameter "dynamic_service" of
           type "boolean" (@range [0,1]), parameter "narrative_method_ids" of
           list of String, parameter "local_function_ids" of list of String,
           parameter "docker_img_name" of String, parameter "data_folder" of
           String, parameter "data_version" of String, parameter
           "compilation_report" of type "CompilationReport" -> structure:
           parameter "module_name" of String, parameter "sdk_version" of
           String, parameter "sdk_git_commit" of String, parameter
           "impl_file_path" of String, parameter "function_places" of mapping
           from String to type "FunctionPlace" -> structure: parameter
           "start_line" of Long, parameter "end_line" of Long, parameter
           "functions" of mapping from String to type "Function" ->
           structure: parameter "name" of String, parameter "comment" of
           String, parameter "place" of type "FunctionPlace" -> structure:
           parameter "start_line" of Long, parameter "end_line" of Long,
           parameter "input" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "output" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "spec_files" of list of type "SpecFile" -> structure:
           parameter "file_name" of String, parameter "content" of String,
           parameter "is_main" of type "boolean" (@range [0,1])
        """
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
        """
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        :returns: instance of list of type "ModuleVersionInfo" (data_folder -
           optional field representing unique module name (like <module_name>
           transformed to lower cases) used for reference data purposes (see
           description for data_version field). This value will be treated as
           part of file system path relative to the base that comes from the
           config (currently base is supposed to be "/kb/data" defined in
           "ref-data-base" parameter). data_version - optional field,
           reflects version of data defined in kbase.yml (see "data-version"
           key). In case this field is set data folder with path
           "/kb/data/<data_folder>/<data_version>" should be initialized by
           running docker image with "init" target from catalog. And later
           when async methods are run it should be mounted on AWE worker
           machine into "/data" folder inside docker container by execution
           engine.) -> structure: parameter "timestamp" of Long, parameter
           "registration_id" of String, parameter "version" of String,
           parameter "git_commit_hash" of String, parameter
           "git_commit_message" of String, parameter "dynamic_service" of
           type "boolean" (@range [0,1]), parameter "narrative_method_ids" of
           list of String, parameter "local_function_ids" of list of String,
           parameter "docker_img_name" of String, parameter "data_folder" of
           String, parameter "data_version" of String, parameter
           "compilation_report" of type "CompilationReport" -> structure:
           parameter "module_name" of String, parameter "sdk_version" of
           String, parameter "sdk_git_commit" of String, parameter
           "impl_file_path" of String, parameter "function_places" of mapping
           from String to type "FunctionPlace" -> structure: parameter
           "start_line" of Long, parameter "end_line" of Long, parameter
           "functions" of mapping from String to type "Function" ->
           structure: parameter "name" of String, parameter "comment" of
           String, parameter "place" of type "FunctionPlace" -> structure:
           parameter "start_line" of Long, parameter "end_line" of Long,
           parameter "input" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "output" of list of type "Parameter" -> structure:
           parameter "type" of String, parameter "comment" of String,
           parameter "spec_files" of list of type "SpecFile" -> structure:
           parameter "file_name" of String, parameter "content" of String,
           parameter "is_main" of type "boolean" (@range [0,1])
        """
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

    def get_module_version(self, ctx, selection):
        """
        :param selection: instance of type "SelectModuleVersion" (Get a
           specific module version. Requires either a module_name or git_url.
           If both are provided, they both must match. If no other options
           are specified, then the latest 'release' version is returned.  If
           the module has not been released, then the latest 'beta' or 'dev'
           version is returned. You can check in the returned object if the
           version has been released (see is_released) and what release tags
           are pointing to this version (see release_tags). Optionally, a
           'version' parameter can be provided that can be either: 1) release
           tag: 'dev' | 'beta' | 'release' 2) specific semantic version of a
           released version (you cannot pull dev/beta or other unreleased
           versions by semantic version) - e.g. 2.0.1 3) semantic version
           requirement specification, see:
           https://pypi.python.org/pypi/semantic_version/ which will return
           the latest released version that matches the criteria.  You cannot
           pull dev/beta or other unreleased versions this way. - e.g.: -
           '>1.0.0' - '>=2.1.1,<3.3.0' - '!=0.2.4-alpha,<0.3.0' 4) specific
           full git commit hash include_module_description - set to 1 to
           include the module description in the YAML file of this version;
           default is 0 include_compilation_report - set to 1 to include the
           module compilation report, default is 0) -> structure: parameter
           "module_name" of String, parameter "git_url" of String, parameter
           "version" of String, parameter "include_module_description" of
           type "boolean" (@range [0,1]), parameter
           "include_compilation_report" of type "boolean" (@range [0,1])
        :returns: instance of type "ModuleVersion" (module_name            -
           the name of the module module_description     - (optionally
           returned) html description in KBase YAML of this module git_url   
           - the git url of the source for this module released              
           - 1 if this version has been released, 0 otherwise release_tags   
           - list of strings of: 'dev', 'beta', or 'release', or empty list
           this is a list because the same commit version may be the version
           in multiple release states release_timestamp      - time in ms
           since epoch when this module was approved and moved to release,
           null otherwise note that a module was released before v1.0.0, the
           release timestamp may not have been recorded and will default to
           the registration timestamp timestamp              - time in ms
           since epoch when the registration for this version was started
           registration_id        - id of the last registration for this
           version, used for fetching registration logs and state version    
           - validated semantic version number as indicated in the KBase YAML
           of this version semantic versions are unique among released
           versions of this module git_commit_hash        - the full git
           commit hash of the source for this module git_commit_message     -
           the message attached to this git commit dynamic_service        - 1
           if this version is available as a web service, 0 otherwise
           narrative_app_ids      - list of Narrative App ids registered with
           this module version local_function_ids     - list of Local
           Function ids registered with this module version docker_img_name  
           - name of the docker image for this module created on registration
           data_folder            - name of the data folder used
           compilation_report     - (optionally returned) summary of the KIDL
           specification compilation) -> structure: parameter "module_name"
           of String, parameter "module_description" of String, parameter
           "git_url" of String, parameter "released" of type "boolean"
           (@range [0,1]), parameter "release_tags" of list of String,
           parameter "timestamp" of Long, parameter "registration_id" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "git_commit_message" of String, parameter
           "dynamic_service" of type "boolean" (@range [0,1]), parameter
           "narrative_app_ids" of list of String, parameter
           "local_function_ids" of list of String, parameter
           "docker_img_name" of String, parameter "data_folder" of String,
           parameter "data_version" of String, parameter "compilation_report"
           of type "CompilationReport" -> structure: parameter "module_name"
           of String, parameter "sdk_version" of String, parameter
           "sdk_git_commit" of String, parameter "impl_file_path" of String,
           parameter "function_places" of mapping from String to type
           "FunctionPlace" -> structure: parameter "start_line" of Long,
           parameter "end_line" of Long, parameter "functions" of mapping
           from String to type "Function" -> structure: parameter "name" of
           String, parameter "comment" of String, parameter "place" of type
           "FunctionPlace" -> structure: parameter "start_line" of Long,
           parameter "end_line" of Long, parameter "input" of list of type
           "Parameter" -> structure: parameter "type" of String, parameter
           "comment" of String, parameter "output" of list of type
           "Parameter" -> structure: parameter "type" of String, parameter
           "comment" of String, parameter "spec_files" of list of type
           "SpecFile" -> structure: parameter "file_name" of String,
           parameter "content" of String, parameter "is_main" of type
           "boolean" (@range [0,1])
        """
        # ctx is the context object
        # return variables are: version
        #BEGIN get_module_version
        version = self.cc.get_module_version(selection)
        if version is None:
            raise ValueError("No module version found that matches your criteria!")
        #END get_module_version

        # At some point might do deeper type checking...
        if not isinstance(version, dict):
            raise ValueError('Method get_module_version return value ' +
                             'version is not type dict as required.')
        # return the results
        return [version]

    def list_local_functions(self, ctx, params):
        """
        :param params: instance of type "ListLocalFunctionParams" (Allows
           various ways to filter. Release tag = dev/beta/release, default is
           release module_names = only include modules in the list; if empty
           or not provided then include everything) -> structure: parameter
           "release_tag" of String, parameter "module_names" of list of String
        :returns: instance of list of type "LocalFunctionInfo" (todo: switch
           release_tag to release_tags) -> structure: parameter "module_name"
           of String, parameter "function_id" of String, parameter
           "git_commit_hash" of String, parameter "version" of String,
           parameter "release_tag" of list of String, parameter "name" of
           String, parameter "short_description" of String, parameter "tags"
           of type "LocalFunctionTags" -> structure: parameter "categories"
           of list of String, parameter "input" of type "IOTags" (Local
           Function Listing Support) -> structure: parameter "file_types" of
           list of String, parameter "kb_types" of list of String, parameter
           "output" of type "IOTags" (Local Function Listing Support) ->
           structure: parameter "file_types" of list of String, parameter
           "kb_types" of list of String
        """
        # ctx is the context object
        # return variables are: info_list
        #BEGIN list_local_functions
        info_list = self.cc.list_local_functions(params)
        #END list_local_functions

        # At some point might do deeper type checking...
        if not isinstance(info_list, list):
            raise ValueError('Method list_local_functions return value ' +
                             'info_list is not type list as required.')
        # return the results
        return [info_list]

    def get_local_function_details(self, ctx, params):
        """
        :param params: instance of type "GetLocalFunctionDetails" ->
           structure: parameter "functions" of list of type
           "SelectOneLocalFunction" (release_tag = dev | beta | release, if
           it doesn't exist and git_commit_hash isn't set, we default to
           release and will not return anything if the function is not
           released) -> structure: parameter "module_name" of String,
           parameter "function_id" of String, parameter "release_tag" of
           String, parameter "git_commit_hash" of String
        :returns: instance of list of type "LocalFunctionDetails" ->
           structure: parameter "info" of type "LocalFunctionInfo" (todo:
           switch release_tag to release_tags) -> structure: parameter
           "module_name" of String, parameter "function_id" of String,
           parameter "git_commit_hash" of String, parameter "version" of
           String, parameter "release_tag" of list of String, parameter
           "name" of String, parameter "short_description" of String,
           parameter "tags" of type "LocalFunctionTags" -> structure:
           parameter "categories" of list of String, parameter "input" of
           type "IOTags" (Local Function Listing Support) -> structure:
           parameter "file_types" of list of String, parameter "kb_types" of
           list of String, parameter "output" of type "IOTags" (Local
           Function Listing Support) -> structure: parameter "file_types" of
           list of String, parameter "kb_types" of list of String, parameter
           "long_description" of String
        """
        # ctx is the context object
        # return variables are: detail_list
        #BEGIN get_local_function_details
        detail_list = self.cc.get_local_function_details(params)
        #END get_local_function_details

        # At some point might do deeper type checking...
        if not isinstance(detail_list, list):
            raise ValueError('Method get_local_function_details return value ' +
                             'detail_list is not type list as required.')
        # return the results
        return [detail_list]

    def module_version_lookup(self, ctx, selection):
        """
        :param selection: instance of type "ModuleVersionLookupParams"
           (module_name - required for module lookup lookup - a lookup
           string, if empty will get the latest released module 1) version
           tag = dev | beta | release 2) semantic version match identifiier
           not supported yet: 3) exact commit hash not supported yet: 4)
           exact timestamp only_service_versions - 1/0, default is 1) ->
           structure: parameter "module_name" of String, parameter "lookup"
           of String, parameter "only_service_versions" of type "boolean"
           (@range [0,1])
        :returns: instance of type "BasicModuleVersionInfo" (DYNAMIC SERVICES
           SUPPORT Methods) -> structure: parameter "module_name" of String,
           parameter "version" of String, parameter "git_commit_hash" of
           String, parameter "docker_img_name" of String
        """
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
        """
        :param filter: instance of type "ListServiceModuleParams" (tag = dev
           | beta | release if tag is not set, all release versions are
           returned) -> structure: parameter "tag" of String
        :returns: instance of list of type "BasicModuleVersionInfo" (DYNAMIC
           SERVICES SUPPORT Methods) -> structure: parameter "module_name" of
           String, parameter "version" of String, parameter "git_commit_hash"
           of String, parameter "docker_img_name" of String
        """
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
        """
        :param params: instance of type "SetRegistrationStateParams" (End
           Dynamic Services Support Methods) -> structure: parameter
           "module_name" of String, parameter "git_url" of String, parameter
           "registration_state" of String, parameter "error_message" of String
        """
        # ctx is the context object
        #BEGIN set_registration_state
        self.cc.set_registration_state(params,  ctx.get('user_id'), ctx.get('token'))
        #END set_registration_state
        pass

    def get_module_state(self, ctx, params):
        """
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        :returns: instance of type "ModuleState" (active: True | False,
           release_approval: approved | denied | under_review |
           not_requested, (all releases require approval) review_message:
           str, (optional) registration: complete | error | (build state
           status), error_message: str (optional)) -> structure: parameter
           "active" of type "boolean" (@range [0,1]), parameter "released" of
           type "boolean" (@range [0,1]), parameter "release_approval" of
           String, parameter "review_message" of String, parameter
           "registration" of String, parameter "error_message" of String
        """
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
        """
        :param registration_id: instance of String
        :returns: instance of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_build_log
        returnVal = self.cc.get_build_log(registration_id)
        #END get_build_log

        # At some point might do deeper type checking...
        if not isinstance(returnVal, str):
            raise ValueError('Method get_build_log return value ' +
                             'returnVal is not type str as required.')
        # return the results
        return [returnVal]

    def get_parsed_build_log(self, ctx, params):
        """
        given the registration_id returned from the register method, you can check the build log with this method
        :param params: instance of type "GetBuildLogParams" (must specify
           skip & limit, or first_n, or last_n.  If none given, this gets
           last 5000 lines) -> structure: parameter "registration_id" of
           String, parameter "skip" of Long, parameter "limit" of Long,
           parameter "first_n" of Long, parameter "last_n" of Long
        :returns: instance of type "BuildLog" -> structure: parameter
           "registration_id" of String, parameter "timestamp" of String,
           parameter "module_name_lc" of String, parameter "git_url" of
           String, parameter "error" of String, parameter "registration" of
           String, parameter "log" of list of type "BuildLogLine" ->
           structure: parameter "content" of String, parameter "error" of
           type "boolean" (@range [0,1])
        """
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
        """
        :param params: instance of type "ListBuildParams" (Always sorted by
           time, oldest builds are last. only one of these can be set to
           true: only_running - if true, only show running builds only_error
           - if true, only show builds that ended in an error only_complete -
           if true, only show builds that are complete skip - skip these
           first n records, default 0 limit - limit result to the most recent
           n records, default 1000 modules - only include builds from these
           modules based on names/git_urls) -> structure: parameter
           "only_runnning" of type "boolean" (@range [0,1]), parameter
           "only_error" of type "boolean" (@range [0,1]), parameter
           "only_complete" of type "boolean" (@range [0,1]), parameter "skip"
           of Long, parameter "limit" of Long, parameter "modules" of list of
           type "SelectOneModuleParams" (Describes how to find a single
           module/repository. module_name - name of module defined in
           kbase.yaml file; git_url - the url used to register the module) ->
           structure: parameter "module_name" of String, parameter "git_url"
           of String
        :returns: instance of list of type "BuildInfo" -> structure:
           parameter "timestamp" of String, parameter "registration_id" of
           String, parameter "registration" of String, parameter
           "error_message" of String, parameter "module_name_lc" of String,
           parameter "git_url" of String
        """
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
        """
        admin method to delete a module, will only work if the module has not been released
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        """
        # ctx is the context object
        #BEGIN delete_module
        self.cc.delete_module(params, ctx.get('user_id'), ctx.get('token'))
        #END delete_module
        pass

    def migrate_module_to_new_git_url(self, ctx, params):
        """
        admin method to move the git url for a module, should only be used if the exact same code has migrated to
        a new URL.  It should not be used as a way to change ownership, get updates from a new source, or get a new
        module name for an existing git url because old versions are retained and git commits saved will no longer
        be correct.
        :param params: instance of type "UpdateGitUrlParams" (all fields are
           required to make sure you update the right one) -> structure:
           parameter "module_name" of String, parameter "current_git_url" of
           String, parameter "new_git_url" of String
        """
        # ctx is the context object
        #BEGIN migrate_module_to_new_git_url
        self.cc.migrate_module_to_new_git_url(params, ctx.get('user_id'), ctx.get('token'))
        #END migrate_module_to_new_git_url
        pass

    def set_to_active(self, ctx, params):
        """
        admin methods to turn on/off modules
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        """
        # ctx is the context object
        #BEGIN set_to_active
        self.cc.set_module_active_state(True, params,  ctx.get('user_id'), ctx.get('token'))
        #END set_to_active
        pass

    def set_to_inactive(self, ctx, params):
        """
        :param params: instance of type "SelectOneModuleParams" (Describes
           how to find a single module/repository. module_name - name of
           module defined in kbase.yaml file; git_url - the url used to
           register the module) -> structure: parameter "module_name" of
           String, parameter "git_url" of String
        """
        # ctx is the context object
        #BEGIN set_to_inactive
        self.cc.set_module_active_state(False, params,  ctx.get('user_id'), ctx.get('token'))
        #END set_to_inactive
        pass

    def is_approved_developer(self, ctx, usernames):
        """
        temporary developer approval, should be moved to more mature user profile service
        :param usernames: instance of list of String
        :returns: instance of list of type "boolean" (@range [0,1])
        """
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
        """
        :returns: instance of list of String
        """
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
        """
        :param username: instance of String
        """
        # ctx is the context object
        #BEGIN approve_developer
        usernames = self.cc.approve_developer(username,  ctx.get('user_id'), ctx.get('token'))
        #END approve_developer
        pass

    def revoke_developer(self, ctx, username):
        """
        :param username: instance of String
        """
        # ctx is the context object
        #BEGIN revoke_developer
        usernames = self.cc.revoke_developer(username,  ctx.get('user_id'), ctx.get('token'))
        #END revoke_developer
        pass

    def log_exec_stats(self, ctx, params):
        """
        Request from Execution Engine for adding statistics about each method run. It could be done
        using catalog admin credentials only.
        :param params: instance of type "LogExecStatsParams" (user_id -
           GlobusOnline login of invoker, app_module_name - optional module
           name of registered repo (could be absent of null for old fashioned
           services) where app_id comes from, app_id - optional method-spec
           id without module_name prefix (could be absent or null in case
           original execution was started through API call without app ID
           defined), func_module_name - optional module name of registered
           repo (could be absent of null for old fashioned services) where
           func_name comes from, func_name - name of function in KIDL-spec
           without module_name prefix, git_commit_hash - optional service
           version (in case of dynamically registered repo), creation_time,
           exec_start_time and finish_time - defined in seconds since Epoch
           (POSIX), is_error - indicates whether execution was finished with
           error or not.) -> structure: parameter "user_id" of String,
           parameter "app_module_name" of String, parameter "app_id" of
           String, parameter "func_module_name" of String, parameter
           "func_name" of String, parameter "git_commit_hash" of String,
           parameter "creation_time" of Double, parameter "exec_start_time"
           of Double, parameter "finish_time" of Double, parameter "is_error"
           of type "boolean" (@range [0,1]), parameter "job_id" of String
        """
        # ctx is the context object
        #BEGIN log_exec_stats
        admin_user_id = ctx.get('user_id')
        user_id = params.get('user_id')
        app_module_name = params.get('app_module_name')
        app_id = params.get('app_id')
        func_module_name = params.get('func_module_name')
        func_name = params.get('func_name')
        git_commit_hash = params.get('git_commit_hash')
        creation_time = params.get('creation_time')
        exec_start_time = params.get('exec_start_time')
        finish_time = params.get('finish_time')
        is_error = params.get('is_error') != 0
        job_id = params.get('job_id')
        self.cc.log_exec_stats(admin_user_id, ctx.get('token'), user_id, app_module_name, app_id, func_module_name,
                               func_name, git_commit_hash, creation_time, exec_start_time, 
                               finish_time, is_error, job_id)
        #END log_exec_stats
        pass

    def get_exec_aggr_stats(self, ctx, params):
        """
        :param params: instance of type "GetExecAggrStatsParams"
           (full_app_ids - list of fully qualified app IDs (including
           module_name prefix followed by slash in case of dynamically
           registered repo). per_week - optional flag switching results to
           weekly data rather than one row per app for all time (default
           value is false)) -> structure: parameter "full_app_ids" of list of
           String, parameter "per_week" of type "boolean" (@range [0,1])
        :returns: instance of list of type "ExecAggrStats" (full_app_id -
           optional fully qualified method-spec id including module_name
           prefix followed by slash in case of dynamically registered repo
           (it could be absent or null in case original execution was started
           through API call without app ID defined), time_range - one of
           supported time ranges (currently it could be either '*' for all
           time or ISO-encoded week like "2016-W01") total_queue_time -
           summarized time difference between exec_start_time and
           creation_time moments defined in seconds since Epoch (POSIX),
           total_exec_time - summarized time difference between finish_time
           and exec_start_time moments defined in seconds since Epoch
           (POSIX).) -> structure: parameter "full_app_id" of String,
           parameter "time_range" of String, parameter "number_of_calls" of
           Long, parameter "number_of_errors" of Long, parameter
           "total_queue_time" of Double, parameter "total_exec_time" of Double
        """
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
        """
        :param params: instance of type "ExecAggrTableParams" (Get aggregated
           usage metrics; available only to Admins.) -> structure: parameter
           "begin" of Long, parameter "end" of Long
        :returns: instance of unspecified object
        """
        # ctx is the context object
        # return variables are: table
        #BEGIN get_exec_aggr_table
        table = self.cc.get_exec_aggr_table(ctx.get('user_id'), ctx.get('token'), params)
        #END get_exec_aggr_table

        # At some point might do deeper type checking...
        if not isinstance(table, object):
            raise ValueError('Method get_exec_aggr_table return value ' +
                             'table is not type object as required.')
        # return the results
        return [table]

    def get_exec_raw_stats(self, ctx, params):
        """
        :param params: instance of type "GetExecRawStatsParams" (Get raw
           usage metrics; available only to Admins.) -> structure: parameter
           "begin" of Long, parameter "end" of Long
        :returns: instance of list of unspecified object
        """
        # ctx is the context object
        # return variables are: records
        #BEGIN get_exec_raw_stats
        records = self.cc.get_exec_raw_stats(ctx.get('user_id'), ctx.get('token'), params)
        #END get_exec_raw_stats

        # At some point might do deeper type checking...
        if not isinstance(records, list):
            raise ValueError('Method get_exec_raw_stats return value ' +
                             'records is not type list as required.')
        # return the results
        return [records]

    def get_client_groups(self, ctx, params):
        """
        @deprecated list_client_group_configs
        :param params: instance of type "GetClientGroupParams" (if app_ids is
           empty or null, all client groups are returned) -> structure:
        :returns: instance of list of type "AppClientGroup" (app_id = full
           app id; if module name is used it will be case insensitive this
           will overwrite all existing client groups (it won't just push
           what's on the list) If client_groups is empty or set to null, then
           the client_group mapping will be removed.) -> structure: parameter
           "app_id" of String, parameter "client_groups" of list of String
        """
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

    def set_client_group_config(self, ctx, config):
        """
        :param config: instance of type "ClientGroupConfig" -> structure:
           parameter "module_name" of String, parameter "function_name" of
           String, parameter "client_groups" of list of String
        """
        # ctx is the context object
        #BEGIN set_client_group_config
        self.cc.set_client_group_config(ctx.get('user_id'), ctx.get('token'), config)
        #END set_client_group_config
        pass

    def remove_client_group_config(self, ctx, config):
        """
        :param config: instance of type "ClientGroupConfig" -> structure:
           parameter "module_name" of String, parameter "function_name" of
           String, parameter "client_groups" of list of String
        """
        # ctx is the context object
        #BEGIN remove_client_group_config
        self.cc.remove_client_group_config(ctx.get('user_id'), ctx.get('token'), config)
        #END remove_client_group_config
        pass

    def list_client_group_configs(self, ctx, filter):
        """
        :param filter: instance of type "ClientGroupFilter" -> structure:
           parameter "module_name" of String, parameter "function_name" of
           String
        :returns: instance of list of type "ClientGroupConfig" -> structure:
           parameter "module_name" of String, parameter "function_name" of
           String, parameter "client_groups" of list of String
        """
        # ctx is the context object
        # return variables are: groups
        #BEGIN list_client_group_configs
        groups = self.cc.list_client_group_configs(filter)
        #END list_client_group_configs

        # At some point might do deeper type checking...
        if not isinstance(groups, list):
            raise ValueError('Method list_client_group_configs return value ' +
                             'groups is not type list as required.')
        # return the results
        return [groups]

    def set_volume_mount(self, ctx, config):
        """
        must specify all properties of the VolumeMountConfig
        :param config: instance of type "VolumeMountConfig" (for a module,
           function, and client group, set mount configurations) ->
           structure: parameter "module_name" of String, parameter
           "function_name" of String, parameter "client_group" of String,
           parameter "volume_mounts" of list of type "VolumeMount" ->
           structure: parameter "host_dir" of String, parameter
           "container_dir" of String, parameter "read_only" of type "boolean"
           (@range [0,1])
        """
        # ctx is the context object
        #BEGIN set_volume_mount
        self.cc.set_volume_mount(ctx.get('user_id'), ctx.get('token'), config)
        #END set_volume_mount
        pass

    def remove_volume_mount(self, ctx, config):
        """
        must specify module_name, function_name, client_group and this method will delete any configured mounts
        :param config: instance of type "VolumeMountConfig" (for a module,
           function, and client group, set mount configurations) ->
           structure: parameter "module_name" of String, parameter
           "function_name" of String, parameter "client_group" of String,
           parameter "volume_mounts" of list of type "VolumeMount" ->
           structure: parameter "host_dir" of String, parameter
           "container_dir" of String, parameter "read_only" of type "boolean"
           (@range [0,1])
        """
        # ctx is the context object
        #BEGIN remove_volume_mount
        self.cc.remove_volume_mount(ctx.get('user_id'), ctx.get('token'), config)
        #END remove_volume_mount
        pass

    def list_volume_mounts(self, ctx, filter):
        """
        :param filter: instance of type "VolumeMountFilter" (Parameters for
           listing VolumeMountConfigs.  If nothing is set, everything is
           returned.  Otherwise, will return everything that matches all
           fields set.  For instance, if only module_name is set, will return
           everything for that module.  If they are all set, will return the
           specific module/app/client group config.  Returns nothing if no
           matches are found.) -> structure: parameter "module_name" of
           String, parameter "function_name" of String, parameter
           "client_group" of String
        :returns: instance of list of type "VolumeMountConfig" (for a module,
           function, and client group, set mount configurations) ->
           structure: parameter "module_name" of String, parameter
           "function_name" of String, parameter "client_group" of String,
           parameter "volume_mounts" of list of type "VolumeMount" ->
           structure: parameter "host_dir" of String, parameter
           "container_dir" of String, parameter "read_only" of type "boolean"
           (@range [0,1])
        """
        # ctx is the context object
        # return variables are: volume_mount_configs
        #BEGIN list_volume_mounts
        volume_mount_configs = self.cc.list_volume_mounts(ctx.get('user_id'), ctx.get('token'), filter)
        #END list_volume_mounts

        # At some point might do deeper type checking...
        if not isinstance(volume_mount_configs, list):
            raise ValueError('Method list_volume_mounts return value ' +
                             'volume_mount_configs is not type list as required.')
        # return the results
        return [volume_mount_configs]

    def is_admin(self, ctx, username):
        """
        returns true (1) if the user is an admin, false (0) otherwise
        :param username: instance of String
        :returns: instance of type "boolean" (@range [0,1])
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN is_admin
        returnVal = 0
        if username and username != ctx.get('user_id'):
            raise ValueError("Can only check on own admin status")
        if self.cc.is_admin(ctx.get('user_id'), ctx.get('token')):
            returnVal = 1
        #END is_admin

        # At some point might do deeper type checking...
        if not isinstance(returnVal, int):
            raise ValueError('Method is_admin return value ' +
                             'returnVal is not type int as required.')
        # return the results
        return [returnVal]

    def set_secure_config_params(self, ctx, params):
        """
        Only admins can use this function.
        :param params: instance of type "ModifySecureConfigParamsInput" ->
           structure: parameter "data" of list of type
           "SecureConfigParameter" (version - optional version (commit hash,
           tag or semantic one) of module, if not set then default "" value
           is used which means parameter is applied to any version;
           is_password - optional flag meaning to hide this parameter's value
           in UI.) -> structure: parameter "module_name" of String, parameter
           "version" of String, parameter "param_name" of String, parameter
           "is_password" of type "boolean" (@range [0,1]), parameter
           "param_value" of String
        """
        # ctx is the context object
        #BEGIN set_secure_config_params
        self.cc.set_secure_config_params(ctx.get('user_id'), ctx.get('token'), params)
        #END set_secure_config_params
        pass

    def remove_secure_config_params(self, ctx, params):
        """
        Only admins can use this function.
        :param params: instance of type "ModifySecureConfigParamsInput" ->
           structure: parameter "data" of list of type
           "SecureConfigParameter" (version - optional version (commit hash,
           tag or semantic one) of module, if not set then default "" value
           is used which means parameter is applied to any version;
           is_password - optional flag meaning to hide this parameter's value
           in UI.) -> structure: parameter "module_name" of String, parameter
           "version" of String, parameter "param_name" of String, parameter
           "is_password" of type "boolean" (@range [0,1]), parameter
           "param_value" of String
        """
        # ctx is the context object
        #BEGIN remove_secure_config_params
        self.cc.remove_secure_config_params(ctx.get('user_id'), ctx.get('token'), params)
        #END remove_secure_config_params
        pass

    def get_secure_config_params(self, ctx, params):
        """
        Only admins can use this function.
        :param params: instance of type "GetSecureConfigParamsInput" (version
           - optional version (commit hash, tag or semantic one) of module,
           if not set then default "release" value is used; load_all_versions
           - optional flag indicating that all parameter versions should be
           loaded (version filter is not applied), default value is 0.) ->
           structure: parameter "module_name" of String, parameter "version"
           of String, parameter "load_all_versions" of type "boolean" (@range
           [0,1])
        :returns: instance of list of type "SecureConfigParameter" (version -
           optional version (commit hash, tag or semantic one) of module, if
           not set then default "" value is used which means parameter is
           applied to any version; is_password - optional flag meaning to
           hide this parameter's value in UI.) -> structure: parameter
           "module_name" of String, parameter "version" of String, parameter
           "param_name" of String, parameter "is_password" of type "boolean"
           (@range [0,1]), parameter "param_value" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN get_secure_config_params
        returnVal = self.cc.get_secure_config_params(ctx.get('user_id'), ctx.get('token'), params)
        #END get_secure_config_params

        # At some point might do deeper type checking...
        if not isinstance(returnVal, list):
            raise ValueError('Method get_secure_config_params return value ' +
                             'returnVal is not type list as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "", 'version': self.VERSION, 
                     'git_url': self.GIT_URL, 'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
