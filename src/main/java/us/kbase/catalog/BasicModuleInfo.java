
package us.kbase.catalog;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: BasicModuleInfo</p>
 * <pre>
 * git_url is always returned.  Every other field
 * may or may not exist depending on what has been registered or if
 * certain registrations have failed
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "git_url",
    "language",
    "dynamic_service",
    "owners",
    "dev",
    "beta",
    "release",
    "released_version_list"
})
public class BasicModuleInfo {

    @JsonProperty("module_name")
    private java.lang.String moduleName;
    @JsonProperty("git_url")
    private java.lang.String gitUrl;
    @JsonProperty("language")
    private java.lang.String language;
    @JsonProperty("dynamic_service")
    private Long dynamicService;
    @JsonProperty("owners")
    private List<String> owners;
    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("dev")
    private us.kbase.catalog.VersionCommitInfo dev;
    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("beta")
    private us.kbase.catalog.VersionCommitInfo beta;
    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("release")
    private us.kbase.catalog.VersionCommitInfo release;
    @JsonProperty("released_version_list")
    private List<us.kbase.catalog.VersionCommitInfo> releasedVersionList;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("module_name")
    public java.lang.String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(java.lang.String moduleName) {
        this.moduleName = moduleName;
    }

    public BasicModuleInfo withModuleName(java.lang.String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("git_url")
    public java.lang.String getGitUrl() {
        return gitUrl;
    }

    @JsonProperty("git_url")
    public void setGitUrl(java.lang.String gitUrl) {
        this.gitUrl = gitUrl;
    }

    public BasicModuleInfo withGitUrl(java.lang.String gitUrl) {
        this.gitUrl = gitUrl;
        return this;
    }

    @JsonProperty("language")
    public java.lang.String getLanguage() {
        return language;
    }

    @JsonProperty("language")
    public void setLanguage(java.lang.String language) {
        this.language = language;
    }

    public BasicModuleInfo withLanguage(java.lang.String language) {
        this.language = language;
        return this;
    }

    @JsonProperty("dynamic_service")
    public Long getDynamicService() {
        return dynamicService;
    }

    @JsonProperty("dynamic_service")
    public void setDynamicService(Long dynamicService) {
        this.dynamicService = dynamicService;
    }

    public BasicModuleInfo withDynamicService(Long dynamicService) {
        this.dynamicService = dynamicService;
        return this;
    }

    @JsonProperty("owners")
    public List<String> getOwners() {
        return owners;
    }

    @JsonProperty("owners")
    public void setOwners(List<String> owners) {
        this.owners = owners;
    }

    public BasicModuleInfo withOwners(List<String> owners) {
        this.owners = owners;
        return this;
    }

    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("dev")
    public us.kbase.catalog.VersionCommitInfo getDev() {
        return dev;
    }

    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("dev")
    public void setDev(us.kbase.catalog.VersionCommitInfo dev) {
        this.dev = dev;
    }

    public BasicModuleInfo withDev(us.kbase.catalog.VersionCommitInfo dev) {
        this.dev = dev;
        return this;
    }

    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("beta")
    public us.kbase.catalog.VersionCommitInfo getBeta() {
        return beta;
    }

    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("beta")
    public void setBeta(us.kbase.catalog.VersionCommitInfo beta) {
        this.beta = beta;
    }

    public BasicModuleInfo withBeta(us.kbase.catalog.VersionCommitInfo beta) {
        this.beta = beta;
        return this;
    }

    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("release")
    public us.kbase.catalog.VersionCommitInfo getRelease() {
        return release;
    }

    /**
     * <p>Original spec-file type: VersionCommitInfo</p>
     * 
     * 
     */
    @JsonProperty("release")
    public void setRelease(us.kbase.catalog.VersionCommitInfo release) {
        this.release = release;
    }

    public BasicModuleInfo withRelease(us.kbase.catalog.VersionCommitInfo release) {
        this.release = release;
        return this;
    }

    @JsonProperty("released_version_list")
    public List<us.kbase.catalog.VersionCommitInfo> getReleasedVersionList() {
        return releasedVersionList;
    }

    @JsonProperty("released_version_list")
    public void setReleasedVersionList(List<us.kbase.catalog.VersionCommitInfo> releasedVersionList) {
        this.releasedVersionList = releasedVersionList;
    }

    public BasicModuleInfo withReleasedVersionList(List<us.kbase.catalog.VersionCommitInfo> releasedVersionList) {
        this.releasedVersionList = releasedVersionList;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((((((((((((("BasicModuleInfo"+" [moduleName=")+ moduleName)+", gitUrl=")+ gitUrl)+", language=")+ language)+", dynamicService=")+ dynamicService)+", owners=")+ owners)+", dev=")+ dev)+", beta=")+ beta)+", release=")+ release)+", releasedVersionList=")+ releasedVersionList)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
