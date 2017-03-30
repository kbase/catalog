
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
 * <p>Original spec-file type: GetSecureConfigParamsInput</p>
 * <pre>
 * version - optional version (commit hash, tag or semantic one) of module, if
 *     not set then default "release" value is used;
 * load_all_versions - optional flag indicating that all parameter versions 
 *     should be loaded (version filter is not applied), default value is 0.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "version",
    "load_all_versions"
})
public class GetSecureConfigParamsInput {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("version")
    private String version;
    @JsonProperty("load_all_versions")
    private Long loadAllVersions;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public GetSecureConfigParamsInput withModuleName(String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("version")
    public String getVersion() {
        return version;
    }

    @JsonProperty("version")
    public void setVersion(String version) {
        this.version = version;
    }

    public GetSecureConfigParamsInput withVersion(String version) {
        this.version = version;
        return this;
    }

    @JsonProperty("load_all_versions")
    public Long getLoadAllVersions() {
        return loadAllVersions;
    }

    @JsonProperty("load_all_versions")
    public void setLoadAllVersions(Long loadAllVersions) {
        this.loadAllVersions = loadAllVersions;
    }

    public GetSecureConfigParamsInput withLoadAllVersions(Long loadAllVersions) {
        this.loadAllVersions = loadAllVersions;
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
        return ((((((((("GetSecureConfigParamsInput"+" [moduleName=")+ moduleName)+", version=")+ version)+", loadAllVersions=")+ loadAllVersions)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
