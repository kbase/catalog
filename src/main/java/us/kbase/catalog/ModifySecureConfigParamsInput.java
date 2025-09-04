
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
 * <p>Original spec-file type: ModifySecureConfigParamsInput</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "data"
})
public class ModifySecureConfigParamsInput {

    @JsonProperty("data")
    private List<SecureConfigParameter> data;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("data")
    public List<SecureConfigParameter> getData() {
        return data;
    }

    @JsonProperty("data")
    public void setData(List<SecureConfigParameter> data) {
        this.data = data;
    }

    public ModifySecureConfigParamsInput withData(List<SecureConfigParameter> data) {
        this.data = data;
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
        return ((((("ModifySecureConfigParamsInput"+" [data=")+ data)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
