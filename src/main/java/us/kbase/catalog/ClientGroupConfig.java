
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
 * <p>Original spec-file type: ClientGroupConfig</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "function_name",
    "client_groups"
})
public class ClientGroupConfig {

    @JsonProperty("module_name")
    private java.lang.String moduleName;
    @JsonProperty("function_name")
    private java.lang.String functionName;
    @JsonProperty("client_groups")
    private List<String> clientGroups;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("module_name")
    public java.lang.String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(java.lang.String moduleName) {
        this.moduleName = moduleName;
    }

    public ClientGroupConfig withModuleName(java.lang.String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("function_name")
    public java.lang.String getFunctionName() {
        return functionName;
    }

    @JsonProperty("function_name")
    public void setFunctionName(java.lang.String functionName) {
        this.functionName = functionName;
    }

    public ClientGroupConfig withFunctionName(java.lang.String functionName) {
        this.functionName = functionName;
        return this;
    }

    @JsonProperty("client_groups")
    public List<String> getClientGroups() {
        return clientGroups;
    }

    @JsonProperty("client_groups")
    public void setClientGroups(List<String> clientGroups) {
        this.clientGroups = clientGroups;
    }

    public ClientGroupConfig withClientGroups(List<String> clientGroups) {
        this.clientGroups = clientGroups;
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
        return ((((((((("ClientGroupConfig"+" [moduleName=")+ moduleName)+", functionName=")+ functionName)+", clientGroups=")+ clientGroups)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
