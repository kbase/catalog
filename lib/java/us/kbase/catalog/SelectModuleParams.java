
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
 * <p>Original spec-file type: SelectModuleParams</p>
 * <pre>
 * Describes how to find module/repository details.
 * module_name - name of module defined in kbase.yaml file;
 * with_disabled - optional flag adding disabled repos (default value is false).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "git_url",
    "with_disabled"
})
public class SelectModuleParams {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("git_url")
    private String gitUrl;
    @JsonProperty("with_disabled")
    private Long withDisabled;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public SelectModuleParams withModuleName(String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("git_url")
    public String getGitUrl() {
        return gitUrl;
    }

    @JsonProperty("git_url")
    public void setGitUrl(String gitUrl) {
        this.gitUrl = gitUrl;
    }

    public SelectModuleParams withGitUrl(String gitUrl) {
        this.gitUrl = gitUrl;
        return this;
    }

    @JsonProperty("with_disabled")
    public Long getWithDisabled() {
        return withDisabled;
    }

    @JsonProperty("with_disabled")
    public void setWithDisabled(Long withDisabled) {
        this.withDisabled = withDisabled;
    }

    public SelectModuleParams withWithDisabled(Long withDisabled) {
        this.withDisabled = withDisabled;
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
        return ((((((((("SelectModuleParams"+" [moduleName=")+ moduleName)+", gitUrl=")+ gitUrl)+", withDisabled=")+ withDisabled)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
