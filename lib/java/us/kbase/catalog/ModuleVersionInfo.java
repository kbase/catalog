
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
 * <p>Original spec-file type: ModuleVersionInfo</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "timestamp",
    "registration_id",
    "version",
    "git_commit_hash",
    "git_commit_message",
    "narrative_method_ids",
    "docker_img_name"
})
public class ModuleVersionInfo {

    @JsonProperty("timestamp")
    private Long timestamp;
    @JsonProperty("registration_id")
    private java.lang.String registrationId;
    @JsonProperty("version")
    private java.lang.String version;
    @JsonProperty("git_commit_hash")
    private java.lang.String gitCommitHash;
    @JsonProperty("git_commit_message")
    private java.lang.String gitCommitMessage;
    @JsonProperty("narrative_method_ids")
    private List<String> narrativeMethodIds;
    @JsonProperty("docker_img_name")
    private java.lang.String dockerImgName;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("timestamp")
    public Long getTimestamp() {
        return timestamp;
    }

    @JsonProperty("timestamp")
    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    public ModuleVersionInfo withTimestamp(Long timestamp) {
        this.timestamp = timestamp;
        return this;
    }

    @JsonProperty("registration_id")
    public java.lang.String getRegistrationId() {
        return registrationId;
    }

    @JsonProperty("registration_id")
    public void setRegistrationId(java.lang.String registrationId) {
        this.registrationId = registrationId;
    }

    public ModuleVersionInfo withRegistrationId(java.lang.String registrationId) {
        this.registrationId = registrationId;
        return this;
    }

    @JsonProperty("version")
    public java.lang.String getVersion() {
        return version;
    }

    @JsonProperty("version")
    public void setVersion(java.lang.String version) {
        this.version = version;
    }

    public ModuleVersionInfo withVersion(java.lang.String version) {
        this.version = version;
        return this;
    }

    @JsonProperty("git_commit_hash")
    public java.lang.String getGitCommitHash() {
        return gitCommitHash;
    }

    @JsonProperty("git_commit_hash")
    public void setGitCommitHash(java.lang.String gitCommitHash) {
        this.gitCommitHash = gitCommitHash;
    }

    public ModuleVersionInfo withGitCommitHash(java.lang.String gitCommitHash) {
        this.gitCommitHash = gitCommitHash;
        return this;
    }

    @JsonProperty("git_commit_message")
    public java.lang.String getGitCommitMessage() {
        return gitCommitMessage;
    }

    @JsonProperty("git_commit_message")
    public void setGitCommitMessage(java.lang.String gitCommitMessage) {
        this.gitCommitMessage = gitCommitMessage;
    }

    public ModuleVersionInfo withGitCommitMessage(java.lang.String gitCommitMessage) {
        this.gitCommitMessage = gitCommitMessage;
        return this;
    }

    @JsonProperty("narrative_method_ids")
    public List<String> getNarrativeMethodIds() {
        return narrativeMethodIds;
    }

    @JsonProperty("narrative_method_ids")
    public void setNarrativeMethodIds(List<String> narrativeMethodIds) {
        this.narrativeMethodIds = narrativeMethodIds;
    }

    public ModuleVersionInfo withNarrativeMethodIds(List<String> narrativeMethodIds) {
        this.narrativeMethodIds = narrativeMethodIds;
        return this;
    }

    @JsonProperty("docker_img_name")
    public java.lang.String getDockerImgName() {
        return dockerImgName;
    }

    @JsonProperty("docker_img_name")
    public void setDockerImgName(java.lang.String dockerImgName) {
        this.dockerImgName = dockerImgName;
    }

    public ModuleVersionInfo withDockerImgName(java.lang.String dockerImgName) {
        this.dockerImgName = dockerImgName;
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
        return ((((((((((((((((("ModuleVersionInfo"+" [timestamp=")+ timestamp)+", registrationId=")+ registrationId)+", version=")+ version)+", gitCommitHash=")+ gitCommitHash)+", gitCommitMessage=")+ gitCommitMessage)+", narrativeMethodIds=")+ narrativeMethodIds)+", dockerImgName=")+ dockerImgName)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
