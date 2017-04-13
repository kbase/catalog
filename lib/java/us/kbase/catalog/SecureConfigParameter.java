
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
 * <p>Original spec-file type: SecureConfigParameter</p>
 * <pre>
 * version - optional version (commit hash, tag or semantic one) of module, if not set
 *     then default "" value is used which means parameter is applied to any version;
 * is_password - optional flag meaning to hide this parameter's value in UI.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "version",
    "param_name",
    "is_password",
    "param_value"
})
public class SecureConfigParameter {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("version")
    private String version;
    @JsonProperty("param_name")
    private String paramName;
    @JsonProperty("is_password")
    private Long isPassword;
    @JsonProperty("param_value")
    private String paramValue;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public SecureConfigParameter withModuleName(String moduleName) {
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

    public SecureConfigParameter withVersion(String version) {
        this.version = version;
        return this;
    }

    @JsonProperty("param_name")
    public String getParamName() {
        return paramName;
    }

    @JsonProperty("param_name")
    public void setParamName(String paramName) {
        this.paramName = paramName;
    }

    public SecureConfigParameter withParamName(String paramName) {
        this.paramName = paramName;
        return this;
    }

    @JsonProperty("is_password")
    public Long getIsPassword() {
        return isPassword;
    }

    @JsonProperty("is_password")
    public void setIsPassword(Long isPassword) {
        this.isPassword = isPassword;
    }

    public SecureConfigParameter withIsPassword(Long isPassword) {
        this.isPassword = isPassword;
        return this;
    }

    @JsonProperty("param_value")
    public String getParamValue() {
        return paramValue;
    }

    @JsonProperty("param_value")
    public void setParamValue(String paramValue) {
        this.paramValue = paramValue;
    }

    public SecureConfigParameter withParamValue(String paramValue) {
        this.paramValue = paramValue;
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
        return ((((((((((((("SecureConfigParameter"+" [moduleName=")+ moduleName)+", version=")+ version)+", paramName=")+ paramName)+", isPassword=")+ isPassword)+", paramValue=")+ paramValue)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
