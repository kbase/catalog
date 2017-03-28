
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
 * <p>Original spec-file type: ModifyHiddenConfigParamsInput</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "data"
})
public class ModifyHiddenConfigParamsInput {

    @JsonProperty("data")
    private List<HiddenConfigParameter> data;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("data")
    public List<HiddenConfigParameter> getData() {
        return data;
    }

    @JsonProperty("data")
    public void setData(List<HiddenConfigParameter> data) {
        this.data = data;
    }

    public ModifyHiddenConfigParamsInput withData(List<HiddenConfigParameter> data) {
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
        return ((((("ModifyHiddenConfigParamsInput"+" [data=")+ data)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
