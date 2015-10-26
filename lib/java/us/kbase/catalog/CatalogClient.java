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
 * Service for managing, registering, and building KBase Modules.
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
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @return   instance of original type "boolean" (@range [0,1])
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public Long isRegistered(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<Long>> retType = new TypeReference<List<Long>>() {};
        List<Long> res = caller.jsonrpcCall("Catalog.is_registered", args, retType, true, false, jsonRpcContext);
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
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void pushDevToBeta(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
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
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void requestRelease(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
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
     * <p>Original spec-file function name: get_module_info</p>
     * <pre>
     * </pre>
     * @param   selection   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @return   parameter "info" of type {@link us.kbase.catalog.ModuleInfo ModuleInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ModuleInfo getModuleInfo(SelectOneModuleParams selection, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(selection);
        TypeReference<List<ModuleInfo>> retType = new TypeReference<List<ModuleInfo>>() {};
        List<ModuleInfo> res = caller.jsonrpcCall("Catalog.get_module_info", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_version_info</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectModuleVersionParams SelectModuleVersionParams}
     * @return   parameter "version" of type {@link us.kbase.catalog.ModuleVersionInfo ModuleVersionInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ModuleVersionInfo getVersionInfo(SelectModuleVersionParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<ModuleVersionInfo>> retType = new TypeReference<List<ModuleVersionInfo>>() {};
        List<ModuleVersionInfo> res = caller.jsonrpcCall("Catalog.get_version_info", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_released_module_versions</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @return   parameter "versions" of list of type {@link us.kbase.catalog.ModuleVersionInfo ModuleVersionInfo}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<ModuleVersionInfo> listReleasedModuleVersions(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<List<ModuleVersionInfo>>> retType = new TypeReference<List<List<ModuleVersionInfo>>>() {};
        List<List<ModuleVersionInfo>> res = caller.jsonrpcCall("Catalog.list_released_module_versions", args, retType, true, false, jsonRpcContext);
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
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @return   parameter "state" of type {@link us.kbase.catalog.ModuleState ModuleState}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public ModuleState getModuleState(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<List<ModuleState>> retType = new TypeReference<List<ModuleState>>() {};
        List<ModuleState> res = caller.jsonrpcCall("Catalog.get_module_state", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: get_build_log</p>
     * <pre>
     * given the timestamp returned from the register method, you can check the build log with this method
     * </pre>
     * @param   timestamp   instance of Long
     * @return   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public String getBuildLog(Long timestamp, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(timestamp);
        TypeReference<List<String>> retType = new TypeReference<List<String>>() {};
        List<String> res = caller.jsonrpcCall("Catalog.get_build_log", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: set_to_active</p>
     * <pre>
     * admin methods to turn on/off modules
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void setToActive(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.set_to_active", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: set_to_inactive</p>
     * <pre>
     * </pre>
     * @param   params   instance of type {@link us.kbase.catalog.SelectOneModuleParams SelectOneModuleParams}
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void setToInactive(SelectOneModuleParams params, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(params);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.set_to_inactive", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: is_approved_developer</p>
     * <pre>
     * temporary developer approval, should be moved to more mature user profile service
     * </pre>
     * @param   usernames   instance of list of String
     * @return   parameter "is_approved" of list of original type "boolean" (@range [0,1])
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<Long> isApprovedDeveloper(List<String> usernames, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(usernames);
        TypeReference<List<List<Long>>> retType = new TypeReference<List<List<Long>>>() {};
        List<List<Long>> res = caller.jsonrpcCall("Catalog.is_approved_developer", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: list_approved_developers</p>
     * <pre>
     * </pre>
     * @return   parameter "usernames" of list of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public List<String> listApprovedDevelopers(RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        TypeReference<List<List<String>>> retType = new TypeReference<List<List<String>>>() {};
        List<List<String>> res = caller.jsonrpcCall("Catalog.list_approved_developers", args, retType, true, false, jsonRpcContext);
        return res.get(0);
    }

    /**
     * <p>Original spec-file function name: approve_developer</p>
     * <pre>
     * </pre>
     * @param   username   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void approveDeveloper(String username, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(username);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.approve_developer", args, retType, false, true, jsonRpcContext);
    }

    /**
     * <p>Original spec-file function name: revoke_developer</p>
     * <pre>
     * </pre>
     * @param   username   instance of String
     * @throws IOException if an IO exception occurs
     * @throws JsonClientException if a JSON RPC exception occurs
     */
    public void revokeDeveloper(String username, RpcContext... jsonRpcContext) throws IOException, JsonClientException {
        List<Object> args = new ArrayList<Object>();
        args.add(username);
        TypeReference<Object> retType = new TypeReference<Object>() {};
        caller.jsonrpcCall("Catalog.revoke_developer", args, retType, false, true, jsonRpcContext);
    }
}
