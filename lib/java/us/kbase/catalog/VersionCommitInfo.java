
package us.kbase.catalog;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: VersionCommitInfo</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "git_commit_hash"
})
public class VersionCommitInfo {

    @JsonProperty("git_commit_hash")
    private String gitCommitHash;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("git_commit_hash")
    public String getGitCommitHash() {
        return gitCommitHash;
    }

    @JsonProperty("git_commit_hash")
    public void setGitCommitHash(String gitCommitHash) {
        this.gitCommitHash = gitCommitHash;
    }

    public VersionCommitInfo withGitCommitHash(String gitCommitHash) {
        this.gitCommitHash = gitCommitHash;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((("VersionCommitInfo"+" [gitCommitHash=")+ gitCommitHash)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
