
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
 * <p>Original spec-file type: ClientGroupFilter</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "function_name",
    "client_group"
})
public class ClientGroupFilter {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("function_name")
    private String functionName;
    @JsonProperty("client_group")
    private String clientGroup;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public ClientGroupFilter withModuleName(String moduleName) {
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

    public ClientGroupFilter withFunctionName(String functionName) {
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

    public ClientGroupFilter withClientGroup(String clientGroup) {
        this.clientGroup = clientGroup;
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
        return ((((((((("ClientGroupFilter"+" [moduleName=")+ moduleName)+", functionName=")+ functionName)+", clientGroup=")+ clientGroup)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
