
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
 * <p>Original spec-file type: VolumeMountConfig</p>
 * <pre>
 * for a module, function, and client group, set mount configurations
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "function_name",
    "client_group",
    "volume_mounts"
})
public class VolumeMountConfig {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("function_name")
    private String functionName;
    @JsonProperty("client_group")
    private String clientGroup;
    @JsonProperty("volume_mounts")
    private List<VolumeMount> volumeMounts;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public VolumeMountConfig withModuleName(String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("function_name")
    public String getFunctionName() {
        return functionName;
    }

    @JsonProperty("function_name")
    public void setFunctionName(String functionName) {
        this.functionName = functionName;
    }

    public VolumeMountConfig withFunctionName(String functionName) {
        this.functionName = functionName;
        return this;
    }

    @JsonProperty("client_group")
    public String getClientGroup() {
        return clientGroup;
    }

    @JsonProperty("client_group")
    public void setClientGroup(String clientGroup) {
        this.clientGroup = clientGroup;
    }

    public VolumeMountConfig withClientGroup(String clientGroup) {
        this.clientGroup = clientGroup;
        return this;
    }

    @JsonProperty("volume_mounts")
    public List<VolumeMount> getVolumeMounts() {
        return volumeMounts;
    }

    @JsonProperty("volume_mounts")
    public void setVolumeMounts(List<VolumeMount> volumeMounts) {
        this.volumeMounts = volumeMounts;
    }

    public VolumeMountConfig withVolumeMounts(List<VolumeMount> volumeMounts) {
        this.volumeMounts = volumeMounts;
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
        return ((((((((((("VolumeMountConfig"+" [moduleName=")+ moduleName)+", functionName=")+ functionName)+", clientGroup=")+ clientGroup)+", volumeMounts=")+ volumeMounts)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
