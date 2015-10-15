package us.kbase.catalog;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import us.kbase.auth.AuthToken;
import us.kbase.common.service.JsonClientCaller;
import us.kbase.common.service.JsonClientException;
import us.kbase.common.service.RpcContext;
import us.kbase.common.service.UnauthorizedException;

/**
 * <p>Original spec-file module name: Catalog</p>
 * <pre>
 * </pre>
 */
public class CatalogClient {
    private JsonClientCaller caller;


    /** Constructs a client with a custom URL and no user credentials.
     * @param url the URL of the service.
     */
    public CatalogClient(URL url) {
        caller = new JsonClientCaller(url);
    }
    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param token the user's authorization token.
     * @throws UnauthorizedException if the token is not valid.
     * @throws IOException if an IOException occurs when checking the token's
     * validity.
     */
    public CatalogClient(URL url, AuthToken token) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, token);
    }

    /** Constructs a client with a custom URL.
     * @param url the URL of the service.
     * @param user the user name.
     * @param password the password for the user name.
     * @throws UnauthorizedException if the credentials are not valid.
     * @throws IOException if an IOException occurs when checking the user's
     * credentials.
     */
    public CatalogClient(URL url, String user, String password) throws UnauthorizedException, IOException {
        caller = new JsonClientCaller(url, user, password);
    }

    /** Get the token this client uses to communicate with the server.
     * @return the authorization token.
     */
    public AuthToken getToken() {
        return caller.getToken();
    }

    /** Get the URL of the service with which this client communicates.
     * @return the service URL.
     */
    public URL getURL() {
        return caller.getURL();
    }

    /** Set the timeout between establishing a connection to a server and
     * receiving a response. A value of zero or null implies no timeout.
     * @param milliseconds the milliseconds to wait before timing out when
     * attempting to read from a server.
     */
    public void setConnectionReadTimeOut(Integer milliseconds) {
        this.caller.setConnectionReadTimeOut(milliseconds);
    }

    /** Check if this client allows insecure http (vs https) connections.
     * @return true if insecure connections are allowed.
     */
    public boolean isInsecureHttpConnectionAllowed() {
        return caller.isInsecureHttpConnectionAllowed();
    }

    /** Deprecated. Use isInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public boolean isAuthAllowedForHttp() {
        return caller.isAuthAllowedForHttp();
    }

    /** Set whether insecure http (vs https) connections should be allowed by
     * this client.
     * @param allowed true to allow insecure connections. Default false
     */
    public void setIsInsecureHttpConnectionAllowed(boolean allowed) {
        caller.setInsecureHttpConnectionAllowed(allowed);
    }

    /** Deprecated. Use setIsInsecureHttpConnectionAllowed().
     * @deprecated
     */
    public void setAuthAllowedForHttp(boolean isAuthAllowedForHttp) {
        caller.setAuthAllowedForHttp(isAuthAllowedForHttp);
    }

    /** Set whether all SSL certificates, including self-signed certificates,
     * should be trusted.
     * @param trustAll true to trust all certificates. Default false.
     */
    public void setAllSSLCertificatesTrusted(final boolean trustAll) {
        caller.setAllSSLCertificatesTrusted(trustAll);
    }
    
    /** Check if this client trusts all SSL certificates, including
     * self-signed certificates.
     * @return true if all certificates are trusted.
     */
    public boolean isAllSSLCertificatesTrusted() {
        return caller.isAllSSLCertificatesTrusted();
    }
    /** Sets streaming mode on. In this case, the data will be streamed to
     * the server in chunks as it is read from disk rather than buffered in
     * memory. Many servers are not compatible with this feature.
     * @param streamRequest true to set streaming mode on, false otherwise.
     */
    public void setStreamingModeOn(boolean streamRequest) {
        caller.setStreamingModeOn(streamRequest);
    }

    /** Returns true if streaming mode is on.
     * @return true if streaming mode is on.
     */
    public boolean isStreamingModeOn() {
        return caller.isStreamingModeOn();
    }

    public void _setFileForNextRpcResponse(File f) {
        caller.setFileForNextRpcResponse(f);
    }

    /**
     * <p>Original spec-file function name: version</p>
     * <pre>
     * Get the version of the deployed catalog service endpoint.
     * </pre>
     * @return   parameter "version" of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String version(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("Catalog.version", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: is_registered</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleParams SelectModuleParams}
     * @return   instance of original type "boolean" (@range [0,1])
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long isRegistered(SelectModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("Catalog.is_registered", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_repo_last_timestamp</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleParams SelectModuleParams}
     * @return   parameter "timestamp" of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long getRepoLastTimestamp(SelectModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("Catalog.get_repo_last_timestamp", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: register_repo</p>
     * <pre>
     * allow/require developer to supply git branch/git commit tag? 
     * if this is a new module, creates the initial registration with the authenticated user as
     * the sole owner, then launches a build to update the dev version of the module.  You can check
     * the state of this build with the 'get_module_state' method passing in the git_url.  If the module
     * already exists, then you must be an owner to reregister.  That will immediately overwrite your
     * dev version of the module (old dev versions are not stored, but you can always reregister an old
     * version from the repo) and start a build.
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.RegisterRepoParams RegisterRepoParams}
     * @return   parameter "timestamp" of Long
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long registerRepo(RegisterRepoParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("Catalog.register_repo", args, retType, true, true, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: push_dev_to_beta</p>
     * <pre>
     * immediately updates the beta tag to what is currently in dev, whatever is currently in beta
     * is discarded.  Will fail if a release request is active and has not been approved/denied
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleParams SelectModuleParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void pushDevToBeta(SelectModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.push_dev_to_beta", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: request_release</p>
     * <pre>
     * requests a push from beta to release version; must be approved be a kbase Admin
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleParams SelectModuleParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void requestRelease(SelectModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.request_release", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: list_requested_releases</p>
     * <pre>
     * </pre>
     * @return   parameter "requested_releases" of list of type {@link us.kbase.catalog.RequestedReleaseInfo RequestedReleaseInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<RequestedReleaseInfo> listRequestedReleases(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<List<RequestedReleaseInfo>>> retType = new TypeReference<List<List<RequestedReleaseInfo>>>() {};
        List<List<RequestedReleaseInfo>> res = caller.jsonrpcCall("Catalog.list_requested_releases", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: review_release_request</p>
     * <pre>
     * </pre>
     * @param   review   instance of type {@link us.kbase.catalog.ReleaseReview ReleaseReview}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void reviewReleaseRequest(ReleaseReview review, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(review);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.review_release_request", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: list_basic_module_info</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.ListModuleParams ListModuleParams}
     * @return   parameter "info_list" of list of type {@link us.kbase.catalog.BasicModuleInfo BasicModuleInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<BasicModuleInfo> listBasicModuleInfo(ListModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<BasicModuleInfo>>> retType = new TypeReference<List<List<BasicModuleInfo>>>() {};
        List<List<BasicModuleInfo>> res = caller.jsonrpcCall("Catalog.list_basic_module_info", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_repo_details</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.HistoryRepoParams HistoryRepoParams}
     * @return   instance of type {@link us.kbase.catalog.RepoDetails RepoDetails}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public RepoDetails getRepoDetails(HistoryRepoParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<RepoDetails>> retType = new TypeReference<List<RepoDetails>>() {};
        List<RepoDetails> res = caller.jsonrpcCall("Catalog.get_repo_details", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_repo_versions</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleParams SelectModuleParams}
     * @return   parameter "versions" of list of type {@link us.kbase.catalog.RepoVersion RepoVersion}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<RepoVersion> listRepoVersions(SelectModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<RepoVersion>>> retType = new TypeReference<List<List<RepoVersion>>>() {};
        List<List<RepoVersion>> res = caller.jsonrpcCall("Catalog.list_repo_versions", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: set_registration_state</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SetRegistrationStateParams SetRegistrationStateParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void setRegistrationState(SetRegistrationStateParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.set_registration_state", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: get_module_state</p>
     * <pre>
     * Get repo state (one of 'pending', 'ready', 'building', 'testing', 'disabled').
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleParams SelectModuleParams}
     * @return   parameter "state" of type {@link us.kbase.catalog.ModuleState ModuleState}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ModuleState getModuleState(SelectModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<ModuleState>> retType = new TypeReference<List<ModuleState>>() {};
        List<ModuleState> res = caller.jsonrpcCall("Catalog.get_module_state", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }
}
