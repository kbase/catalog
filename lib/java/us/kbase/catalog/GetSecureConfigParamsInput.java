
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
 * version_lookup - a lookup string, if empty will get the latest released module
 *             1) version tag = dev | beta | release
 *             2) semantic version match identifiier
 *             not supported yet: 3) exact commit hash
 *             not supported yet: 4) exact timestamp
 * load_all_versions - flag indicating that all parameter versions should be 
 *             loaded (version_lookup filter is not applied)
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "version_lookup",
    "load_all_versions"
})
public class GetSecureConfigParamsInput {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("version_lookup")
    private String versionLookup;
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

    @JsonProperty("version_lookup")
    public String getVersionLookup() {
        return versionLookup;
    }

    @JsonProperty("version_lookup")
    public void setVersionLookup(String versionLookup) {
        this.versionLookup = versionLookup;
    }

    public GetSecureConfigParamsInput withVersionLookup(String versionLookup) {
        this.versionLookup = versionLookup;
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
        return ((((((((("GetSecureConfigParamsInput"+" [moduleName=")+ moduleName)+", versionLookup=")+ versionLookup)+", loadAllVersions=")+ loadAllVersions)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
