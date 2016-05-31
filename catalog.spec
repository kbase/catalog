/*
    Service for managing, registering, and building KBase Modules using the KBase SDK.
*/
module Catalog {

    /* @range [0,1] */
    typedef int boolean;

    /* Get the version of the deployed catalog service endpoint. */
    funcdef version() returns (string version);

    /*
        Describes how to find a single module/repository.
        module_name - name of module defined in kbase.yaml file;
        git_url - the url used to register the module
    */
    typedef structure {
        string module_name;
        string git_url;
    } SelectOneModuleParams;

    /* returns true (1) if the module exists, false (2) otherwise */
    funcdef is_registered(SelectOneModuleParams params) returns (boolean);

    typedef structure {
        string git_url;
        string git_commit_hash;
    } RegisterRepoParams;

    /* allow/require developer to supply git branch/git commit tag? 
    if this is a new module, creates the initial registration with the authenticated user as
    the sole owner, then launches a build to update the dev version of the module.  You can check
    the state of this build with the 'get_module_state' method passing in the git_url.  If the module
    already exists, then you must be an owner to reregister.  That will immediately overwrite your
    dev version of the module (old dev versions are not stored, but you can always reregister an old
    version from the repo) and start a build.
    */
    funcdef register_repo(RegisterRepoParams params) returns (string registration_id) authentication required;

    /* immediately updates the beta tag to what is currently in dev, whatever is currently in beta
    is discarded.  Will fail if a release request is active and has not been approved/denied */
    funcdef push_dev_to_beta(SelectOneModuleParams params) returns () authentication required;

    /* requests a push from beta to release version; must be approved be a kbase Admin */
    funcdef request_release(SelectOneModuleParams params) returns () authentication required;

    typedef structure {
        string module_name;
        string git_url;
        string git_commit_hash;
        string git_commit_message;
        int timestamp;
        list <string> owners;
    } RequestedReleaseInfo;

    funcdef list_requested_releases() returns (list<RequestedReleaseInfo> requested_releases);


    /*
        decision - approved | denied
        review_message - 
    */
    typedef structure {
        string module_name;
        string git_url;
        string decision;
        string review_message;
    } ReleaseReview;

    funcdef review_release_request(ReleaseReview review) returns () authentication required;


    /*
        Describes how to filter repositories.
        include_released - optional flag indicated modules that are released are included (default:true)
        include_unreleased - optional flag indicated modules that are not released are included (default:false)
        with_disabled - optional flag indicating disabled repos should be included (default:false).
        include_modules_with_no_name_set - default to 0, if set return modules that were never
                                            registered successfully (first registration failed, never
                                            got a module name, but there is a git_url)
    */
    typedef structure {
        list <string> owners;
        boolean include_released;
        boolean include_unreleased;
        boolean include_disabled;
        boolean include_modules_with_no_name_set;
    } ListModuleParams;

    typedef structure {
        string module_name;
        string git_url;
    } BasicModuleInfo;
    /*
    To Add:
        string brief_description;
        list <string> owners;
        boolean is_released;
    */

    /* */
    funcdef list_basic_module_info(ListModuleParams params) returns (list<BasicModuleInfo> info_list);


    /* FAVORITES!! */

    typedef structure {
        string module_name;
        string id;
    } FavoriteItem;

    funcdef add_favorite(FavoriteItem params) returns () authentication required;
    funcdef remove_favorite(FavoriteItem params) returns () authentication required;

    funcdef list_favorites(string username) returns(list<FavoriteItem> favorites);

    typedef structure {
        string username;
        string timestamp;
    } FavoriteUser;

    funcdef list_app_favorites(FavoriteItem item) returns(list<FavoriteUser> users);

    /* if favorite item is given, will return stars just for that item.  If a module
    name is given, will return stars for all methods in that module.  If none of
    those are given, then will return stars for every method that there is info on 

    parameters to add:
        list<FavoriteItem> items;
    */
    typedef structure {
        list<string> modules;
    } ListFavoriteCounts;

    typedef structure {
        string module_name;
        string app_id;
        int count;
    } FavoriteCount;

    funcdef list_favorite_counts(ListFavoriteCounts params) returns (list<FavoriteCount> counts);


    typedef structure {
        int start_line;
        int end_line;
    } FunctionPlace;

    typedef structure {
        string type;
        string comment;
    } Parameter;

    typedef structure {
        string name;
        string comment;
        FunctionPlace place;
        list<Parameter> input;
        list<Parameter> output;
    } Function;

    typedef structure {
        string file_name;
        string content;
        boolean is_main;
    } SpecFile;

    typedef structure {
        string module_name;
        string sdk_version;
        string sdk_git_commit;
        string impl_file_path;
        mapping<string, FunctionPlace> function_places;
        mapping<string, Function> functions;
        list<SpecFile> spec_files;
    } CompilationReport;

    /*
        data_folder - optional field representing unique module name (like <module_name> transformed to
            lower cases) used for reference data purposes (see description for data_version field). This
            value will be treated as part of file system path relative to the base that comes from the 
            config (currently base is supposed to be "/kb/data" defined in "ref-data-base" parameter).
        data_version - optional field, reflects version of data defined in kbase.yml (see "data-version" 
            key). In case this field is set data folder with path "/kb/data/<data_folder>/<data_version>"
            should be initialized by running docker image with "init" target from catalog. And later when
            async methods are run it should be mounted on AWE worker machine into "/data" folder inside 
            docker container by execution engine.
    */
    typedef structure {
        int timestamp;
        string registration_id;
        string version;
        string git_commit_hash;
        string git_commit_message;
        boolean dynamic_service;
        list<string> narrative_method_ids;
        list<string> local_function_ids;
        string docker_img_name;
        string data_folder;
        string data_version;
        CompilationReport compilation_report;
    } ModuleVersionInfo;

    typedef structure {
        string module_name;
        string git_url;

        string description;
        string language;

        list <string> owners;

        ModuleVersionInfo release;
        ModuleVersionInfo beta;
        ModuleVersionInfo dev;
    } ModuleInfo;

    funcdef get_module_info(SelectOneModuleParams selection) returns (ModuleInfo info);


    /*
        only required: module_name or git_url, the rest are optional selectors
        If no selectors given, returns current release version
        version is one of: release | beta | dev
        old release versions can only be retrieved individually by timestamp or git_commit_hash

        Note: this method isn't particularly smart or effecient yet, because it pulls the info for a particular
        module first, then searches in code for matches to the relevant query.  Instead, this should be
        performed on the database side through queries.  Will optimize when this becomes an issue.

        In the future, this will be extended so that you can retrieve version info by only
        timestamp, git commit, etc, but the necessary indicies have not been setup yet.  In general, we will
        need to add better search capabilities
    */
    typedef structure {
        string module_name;
        string git_url;
        int timestamp;
        string git_commit_hash;
        string version;
    } SelectModuleVersionParams;

    /* DEPRECATED!!!  use get_module_version */
    funcdef get_version_info(SelectModuleVersionParams params) returns (ModuleVersionInfo version);

    funcdef list_released_module_versions(SelectOneModuleParams params) returns (list<ModuleVersionInfo> versions);





    /*
        module_name            - the name of the module
        module_description     - (optionally returned) html description in KBase YAML of this module
        git_url                - the git url of the source for this module

        released               - 1 if this version has been released, 0 otherwise
        release_tags           - list of strings of: 'dev', 'beta', or 'release', or empty list
                                 this is a list because the same commit version may be the version in multiple release states
        release_timestamp      - time in ms since epoch when this module was approved and moved to release, null otherwise
                                 note that a module was released before v1.0.0, the release timestamp may not have been
                                 recorded and will default to the registration timestamp

        timestamp              - time in ms since epoch when the registration for this version was started
        registration_id        - id of the last registration for this version, used for fetching registration logs and state

        version                - validated semantic version number as indicated in the KBase YAML of this version
                                 semantic versions are unique among released versions of this module

        git_commit_hash        - the full git commit hash of the source for this module
        git_commit_message     - the message attached to this git commit

        dynamic_service        - 1 if this version is available as a web service, 0 otherwise

        narrative_app_ids      - list of Narrative App ids registered with this module version
        local_function_ids     - list of Local Function ids registered with this module version

        docker_img_name        - name of the docker image for this module created on registration
        data_folder            - name of the data folder used 

        compilation_report     - (optionally returned) summary of the KIDL specification compilation
    */
    typedef structure {
        string module_name;
        string module_description;
        string git_url;

        boolean released;
        list<string> release_tags;

        int timestamp;
        string registration_id;

        string version;
        string git_commit_hash;
        string git_commit_message;

        boolean dynamic_service;

        list<string> narrative_app_ids;

        list<string> local_function_ids;

        string docker_img_name;
        string data_folder;
        string data_version;

        CompilationReport compilation_report;

    } ModuleVersion;


    /*
        Get a specific module version.

        Requires either a module_name or git_url.  If both are provided, they both must match.

        If no other options are specified, then the latest 'release' version is returned.  If
        the module has not been released, then the latest 'beta' or 'dev' version is returned.
        You can check in the returned object if the version has been released (see is_released)
        and what release tags are pointing to this version (see release_tags).

        Optionally, a 'version' parameter can be provided that can be either:
            1) release tag: 'dev' | 'beta' | 'release'

            2) specific semantic version of a released version (you cannot pull dev/beta or other
               unreleased versions by semantic version)
                - e.g. 2.0.1

            3) semantic version requirement specification, see: https://pypi.python.org/pypi/semantic_version/
               which will return the latest released version that matches the criteria.  You cannot pull
               dev/beta or other unreleased versions this way.
                - e.g.:
                    - '>1.0.0'
                    - '>=2.1.1,<3.3.0'
                    - '!=0.2.4-alpha,<0.3.0'

            4) specific full git commit hash

        include_module_description - set to 1 to include the module description in the YAML file of this version;
                                     default is 0
        include_compilation_report - set to 1 to include the module compilation report, default is 0


    */
    typedef structure {
        string module_name;
        string git_url;

        string version;

        boolean include_module_description;
        boolean include_compilation_report;
    } SelectModuleVersion;

    funcdef get_module_version(SelectModuleVersion selection) returns (ModuleVersion version);




    /* Local Function Listing Support */



    typedef structure {
        list<string> file_types;
        list<string> kb_types;
    } IOTags;

    typedef structure {
        list <string> categories;
        IOTags input;
        IOTags output;
    } LocalFunctionTags;

    /* todo: switch release_tag to release_tags */
    typedef structure {
        string module_name;
        string function_id;
        string git_commit_hash;

        string version;
        list<string> release_tag;

        string name;
        string short_description;

        LocalFunctionTags tags;
    } LocalFunctionInfo;



    typedef structure {
        LocalFunctionInfo info;
        string long_description;
    } LocalFunctionDetails;

    /*
        Allows various ways to filter.
        Release tag = dev/beta/release, default is release
        module_names = only include modules in the list; if empty or not
                       provided then include everything
    */
    typedef structure {
        string release_tag;
        list<string> module_names;
    } ListLocalFunctionParams;

    funcdef list_local_functions(ListLocalFunctionParams params) returns (list<LocalFunctionInfo> info_list);


    /*
        release_tag = dev | beta | release, if it doesn't exist and git_commit_hash isn't set, we default to release
                      and will not return anything if the function is not released
    */
    typedef structure {
        string module_name;
        string function_id;
        string release_tag;
        string git_commit_hash;
    } SelectOneLocalFunction;

    typedef structure {
        list<SelectOneLocalFunction> functions;
    } GetLocalFunctionDetails;

    funcdef get_local_function_details(GetLocalFunctionDetails params) returns (list<LocalFunctionDetails> detail_list);

    /* End local function listing support */


    /*  DYNAMIC SERVICES SUPPORT Methods */

    typedef structure {
        string module_name;
        string version;
        string git_commit_hash;
        string docker_img_name;
    } BasicModuleVersionInfo;

    /*
        module_name - required for module lookup
        lookup - a lookup string, if empty will get the latest released module
                    1) version tag = dev | beta | release
                    2) semantic version match identifiier
                    not supported yet: 3) exact commit hash
                    not supported yet: 4) exact timestamp
        only_service_versions - 1/0, default is 1
    */
    typedef structure {
        string module_name;
        string lookup;
        boolean only_service_versions;
    } ModuleVersionLookupParams;

    funcdef module_version_lookup(ModuleVersionLookupParams selection) returns (BasicModuleVersionInfo);

    /*
        tag = dev | beta | release
        if tag is not set, all release versions are returned
    */
    typedef structure {
        string tag;
    } ListServiceModuleParams;

    funcdef list_service_modules(ListServiceModuleParams filter) returns (list<BasicModuleVersionInfo> service_modules);


    /*  End Dynamic Services Support Methods */


    typedef structure {
        string module_name;
        string git_url;
        string registration_state;
        string error_message;
    } SetRegistrationStateParams;

    funcdef set_registration_state(SetRegistrationStateParams params) returns () authentication required;

    /*
        active: True | False,
        release_approval: approved | denied | under_review | not_requested, (all releases require approval)
        review_message: str, (optional)
        registration: complete | error | (build state status),
        error_message: str (optional)
    */
    typedef structure {
        boolean active;
        boolean released;
        string release_approval;
        string review_message;
        string registration;
        string error_message;
    } ModuleState;

    /* */
    funcdef get_module_state(SelectOneModuleParams params) returns (ModuleState state);


    /* must specify skip & limit, or first_n, or last_n.  If none given, this gets last 5000 lines */
    typedef structure {
        string registration_id;
        int skip;
        int limit;
        int first_n;
        int last_n;
    } GetBuildLogParams;

    typedef structure {
        string content;
        boolean error;
    } BuildLogLine;


    typedef structure {
        string registration_id;
        string timestamp;
        string module_name_lc;
        string git_url;
        string error;
        string registration;
        list <BuildLogLine> log;
    } BuildLog;

    funcdef get_build_log(string registration_id) returns (string);

    /*
        given the registration_id returned from the register method, you can check the build log with this method
    */
    funcdef get_parsed_build_log(GetBuildLogParams params) returns (BuildLog build_log);


    typedef structure {
        string timestamp;
        string registration_id;
        string registration;
        string error_message;
        string module_name_lc;
        string git_url;
    } BuildInfo;

    /*
        Always sorted by time, oldest builds are last.

        only one of these can be set to true:
            only_running - if true, only show running builds
            only_error - if true, only show builds that ended in an error
            only_complete - if true, only show builds that are complete
        skip - skip these first n records, default 0
        limit - limit result to the most recent n records, default 1000

        modules - only include builds from these modules based on names/git_urls
    */
    typedef structure {
        boolean only_runnning;
        boolean only_error;
        boolean only_complete;

        int skip;
        int limit;

        list <SelectOneModuleParams> modules;

    } ListBuildParams;

    funcdef list_builds(ListBuildParams params) returns (list<BuildInfo> builds);

    

    /* all fields are required to make sure you update the right one */
    typedef structure {
        string module_name;
        string current_git_url;
        string new_git_url;
    } UpdateGitUrlParams;


    /* admin method to delete a module, will only work if the module has not been released */
    funcdef delete_module(SelectOneModuleParams params) returns () authentication required;

    /* admin method to move the git url for a module, should only be used if the exact same code has migrated to
    a new URL.  It should not be used as a way to change ownership, get updates from a new source, or get a new
    module name for an existing git url because old versions are retained and git commits saved will no longer
    be correct. */
    funcdef migrate_module_to_new_git_url(UpdateGitUrlParams params) returns () authentication required;


    /* admin methods to turn on/off modules */
    funcdef set_to_active(SelectOneModuleParams params) returns () authentication required;
    funcdef set_to_inactive(SelectOneModuleParams params) returns () authentication required;

    /* temporary developer approval, should be moved to more mature user profile service */
    funcdef is_approved_developer(list<string>usernames) returns (list<boolean> is_approved);
    funcdef list_approved_developers() returns (list<string> usernames);
    funcdef approve_developer(string username) returns () authentication required;
    funcdef revoke_developer(string username) returns () authentication required;

    /*
        user_id - GlobusOnline login of invoker,
        app_module_name - optional module name of registered repo (could be absent of null for
            old fashioned services) where app_id comes from,
        app_id - optional method-spec id without module_name prefix (could be absent or null
            in case original execution was started through API call without app ID defined),
        func_module_name - optional module name of registered repo (could be absent of null for
            old fashioned services) where func_name comes from,
        func_name - name of function in KIDL-spec without module_name prefix,
        git_commit_hash - optional service version (in case of dynamically registered repo),
        creation_time, exec_start_time and finish_time - defined in seconds since Epoch (POSIX),
        is_error - indicates whether execution was finished with error or not.
    */
    typedef structure {
        string user_id;
        string app_module_name;
        string app_id;
        string func_module_name;
        string func_name;
        string git_commit_hash;
        float creation_time;
        float exec_start_time;
        float finish_time;
        boolean is_error;
    } LogExecStatsParams;

    /*
        Request from Execution Engine for adding statistics about each method run. It could be done
        using catalog admin credentials only.
    */
    funcdef log_exec_stats(LogExecStatsParams params) returns () authentication required;

    /*
        full_app_ids - list of fully qualified app IDs (including module_name prefix followed by
            slash in case of dynamically registered repo).
        per_week - optional flag switching results to weekly data rather than one row per app for 
            all time (default value is false)
    */
    typedef structure {
        list<string> full_app_ids;
        boolean per_week;
    } GetExecAggrStatsParams;

    /*
        full_app_id - optional fully qualified method-spec id including module_name prefix followed
            by slash in case of dynamically registered repo (it could be absent or null in case
            original execution was started through API call without app ID defined),
        time_range - one of supported time ranges (currently it could be either '*' for all time
            or ISO-encoded week like "2016-W01")
        total_queue_time - summarized time difference between exec_start_time and creation_time moments
            defined in seconds since Epoch (POSIX),
        total_exec_time - summarized time difference between finish_time and exec_start_time moments 
            defined in seconds since Epoch (POSIX).
    */
    typedef structure {
        string full_app_id;
        string time_range;
        int number_of_calls;
        int number_of_errors;
        float total_queue_time;
        float total_exec_time;
    } ExecAggrStats;

    funcdef get_exec_aggr_stats(GetExecAggrStatsParams params) returns (list<ExecAggrStats>);



    /*
        Get aggregated usage metrics; available only to Admins.
    */
    typedef structure {
        int begin;
        int end;
    } ExecAggrTableParams;

    funcdef get_exec_aggr_table(ExecAggrTableParams params) returns (UnspecifiedObject table) authentication required;


    /*
        Get raw usage metrics; available only to Admins.
    */
    typedef structure {
        int begin;
        int end;
    } GetExecRawStatsParams;

    funcdef get_exec_raw_stats(GetExecRawStatsParams params) returns (list<UnspecifiedObject> records) authentication required;


    /* Temporary set of methods to dynamically set client groups for specific methods.  These methods
       will likely go away after the execution engine has been refactored/extended.  Only admins can
       run these methods.
    */


    /* app_id = full app id; if module name is used it will be case insensitive 
        this will overwrite all existing client groups (it won't just push what's on the list)
        If client_groups is empty or set to null, then the client_group mapping will be removed.
    */
    typedef structure {
        string app_id;
        list<string> client_groups;
    } AppClientGroup;

    funcdef set_client_group(AppClientGroup group) returns () authentication required;

    /* if app_ids is empty or null, all client groups are returned */
    typedef structure {
        list<string> app_ids;
    } GetClientGroupParams;

    funcdef get_client_groups(GetClientGroupParams params) returns (list<AppClientGroup> groups);

    /* returns true (1) if the user is an admin, false (0) otherwise */
    funcdef is_admin(string username) returns (boolean); 

};
