module Catalog {

    /* @range [0,1] */
    typedef int boolean;

    /* Get the version of the deployed catalog service endpoint. */
    funcdef version() returns (string version);

    /*
        Describes how to find module/repository details.
        module_name - name of module defined in kbase.yaml file;
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        string module_name;
        string git_url;
        boolean with_disabled;
    } SelectModuleParams;

    funcdef is_repo_registered(SelectModuleParams params) returns (boolean);

    typedef structure {
        string git_url;
        string git_commit_hash;
    } RegisterRepoParams;

    /* allow/require developer to supply git branch/git commit tag? */
    funcdef register_repo(RegisterRepoParams params) returns (int timestamp)
        authentication required;

    funcdef get_repo_last_timestamp(SelectModuleParams params) returns (int timestamp);


    /*
        Describes how to filter repositories.
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        boolean with_disabled;
    } ListReposParams;

    funcdef list_module_names(ListReposParams params) returns (list<string>);

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
        boolean with_disabled;
    } HistoryRepoParams;

    funcdef get_repo_details(HistoryRepoParams params) returns (RepoDetails);

    /* timestamp will be epoch time */
    typedef structure {
        int timestamp;
        string git_commit_hash;
        boolean with_disabled;
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
