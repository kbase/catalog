/*
    Service for managing, registering, and building KBase Modules.
*/
module Catalog {

    /* @range [0,1] */
    typedef int boolean;

    /* Get the version of the deployed catalog service endpoint. */
    funcdef version() returns (string version);

    /*
        Describes how to find module/repository.
        module_name - name of module defined in kbase.yaml file;
        git_url - the url used to register the module
    */
    typedef structure {
        string module_name;
        string git_url;
    } SelectOneModuleParams;


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
    funcdef register_repo(RegisterRepoParams params) returns (int timestamp) authentication required;

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
        string timestamp;
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
    */
    typedef structure {
        boolean include_released;
        boolean include_unreleased;
        boolean include_disabled;
    } ListModuleParams;

    typedef structure {
        string module_name;
        string git_url;
    } BasicModuleInfo;

    funcdef list_basic_module_info(ListModuleParams params) returns (list<BasicModuleInfo> info_list);



    typedef structure {
        int timestamp;
        string version;
        string git_commit_hash;
        string git_commit_message;
        list<string> narrative_method_ids;
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
        version - release | beta | dev
        owner_version_string - matches on the 'version' set for a version in 'kbase.yaml'
    */
    typedef structure {
        string module_name;
        string git_url;
        int timestamp;
        string git_commit_hash;
        string version;
        string owner_version_string;
    } SelectModuleVersionParams;

    funcdef get_version_info(SelectModuleVersionParams params) returns (ModuleVersionInfo version);

    funcdef list_released_module_versions(SelectOneModuleParams params) returns (list<ModuleVersionInfo> versions);


    /*
        Describes how to find repository details.
        module_name - name of module defined in kbase.yaml file;
        multiple state fields? (approvalState, buildState, versionState)
        state - one of 'pending', 'ready', 'building', 'testing', 'disabled'.
    */
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
        registration: building | complete | error,
        error_message: str (optional)
    */
    typedef structure {
        boolean active;
        string release_approval;
        string review_message;
        string registration;
        string error_message;
    } ModuleState;

    /*
        Get repo state (one of 'pending', 'ready', 'building', 'testing', 'disabled').
    */
    funcdef get_module_state(SelectOneModuleParams params) returns (ModuleState state);


    funcdef get_build_log(int timestamp) returns (string);
};
