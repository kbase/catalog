module Catalog {

    /* @range [0,1] */
    typedef int boolean;

    /*
        Describes how to find repository details.
        module_name - name of module defined in kbase.yaml file;
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        string module_name;
        boolean with_disabled;
    } CurrentRepoParams;

    funcdef is_repo_registered(CurrentRepoParams params) returns (boolean);

    typedef structure {
        string git_url;
    } RegisterRepoParams;

/* allow developer to supply git branch/git commit tag? */
    funcdef register_repo(RegisterRepoParams params) returns (int version)
        authentication required;

    funcdef get_repo_last_version(CurrentRepoParams params) returns (int version);

    /*
        Describes how to filter repositories.
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        boolean with_disabled;
    } ListReposParams;

    funcdef list_repo_module_names(ListReposParams params) returns (list<string>);

    /*
        method_ids - list of method ids (each id is fully qualified, i.e. contains module
            name prefix followed by slash);
        widget_ids - list of widget ids (each id is name of JavaScript file stored in
            repo's 'ui/widgets' folder).
    */
    typedef structure {
        string module_name;
        string git_url;
        string git_branch;
        string git_commit_hash;
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
        version - optional parameter limiting search by certain version timestamp;
        git_commit_hash - optional parameter limiting search by certain git commit hash;
        with_disabled - optional flag adding disabled repos (default value is false).
    */
    typedef structure {
        string module_name;
        int version;
        string git_commit_hash;
        boolean with_disabled;
    } HistoryRepoParams;

    funcdef get_repo_details(HistoryRepoParams params) returns (RepoDetails);

    typedef structure {
        int version;
        string git_commit_hash;
        boolean with_disabled;
    } RepoVersion;

    funcdef list_repo_versions(CurrentRepoParams params) returns (list<RepoVersion>
        versions);

    /*
        Describes how to find repository details.
        module_name - name of module defined in kbase.yaml file;
        state - one of 'ready', 'building', 'testing', 'disabled'.
    */
    typedef structure {
        string module_name;
        string state;
    } SetRepoStateParams;

    funcdef set_repo_state(SetRepoStateParams params) returns () authentication
        required;

    /*
        Get repo state (one of 'pending', 'ready', 'building', 'testing', 'disabled').
    */
    funcdef get_repo_state(CurrentRepoParams params) returns (string state);

};
