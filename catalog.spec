/*


*/
module Catalog {

    /* @range [0,1] */
    typedef int boolean;

    /* Get the version of the deployed catalog service endpoint. */
    funcdef version() returns (string version);

    /*
        Describes how to find module/repository details.
        module_name - name of module defined in kbase.yaml file;
        git_url - the url used to register the module
        include_disabled - optional flag, set to true to include disabled repos
    */
    typedef structure {
        string module_name;
        string git_url;
        boolean include_disabled;
    } SelectModuleParams;

    funcdef is_registered(SelectModuleParams params) returns (boolean);

    /* */
    funcdef get_repo_last_timestamp(SelectModuleParams params) returns (int timestamp);

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
    funcdef push_dev_to_beta(SelectModuleParams params) returns () authentication required;

    /* requests a push from beta to release version; must be approved be a kbase Admin */
    funcdef request_release(SelectModuleParams params) returns () authentication required;

    typedef structure {
        string module_name;
        string git_url;
        string git_commit_hash;
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
        string decision;
        string review_message;
    } ReleaseReview;

    funcdef review_release_request(ReleaseReview review) returns () authentication required;


    /*
        Describes how to filter repositories.
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        boolean include_disabled;
    } ListModuleParams;


    typedef structure {
        string module_name;
        string git_url;
    } BasicModuleInfo;

    funcdef list_basic_module_info(ListModuleParams params) returns (list<BasicModuleInfo> info_list);


    /*
        method_ids - list of method ids (each id is fully qualified, i.e. contains module
            name prefix followed by slash);
        widget_ids - list of widget ids (each id is name of JavaScript file stored in
            repo's 'ui/widgets' folder).
    */
    typedef structure {
        string module_name;
        string git_url;
        string git_commit_hash;
        string version;
        string module_description;
        string service_language;
        list<string> owners;
        string readme;
        list<string> method_ids;
        list<string> widget_ids;
    } RepoDetails;

    /*
        Describes how to find repository details (including old versions). In case neither of
            version and git_commit_hash is specified last version is returned.
        module_name - name of module defined in kbase.yaml file;
        timestamp - optional parameter limiting search by certain version timestamp;
        git_commit_hash - optional parameter limiting search by certain git commit hash;
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        string module_name;
        int timestamp;
        string git_commit_hash;
        boolean include_disabled;
    } HistoryRepoParams;

    funcdef get_repo_details(HistoryRepoParams params) returns (RepoDetails);

    /* timestamp will be epoch time */
    typedef structure {
        int timestamp;
        string git_commit_hash;
        boolean include_disabled;
    } RepoVersion;

    funcdef list_repo_versions(SelectModuleParams params) returns (list<RepoVersion>
        versions);

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
    funcdef get_module_state(SelectModuleParams params) returns (ModuleState state);

};
