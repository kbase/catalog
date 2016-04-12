
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
 * <p>Original spec-file type: ListServiceModuleParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "all_versions"
})
public class ListServiceModuleParams {

    @JsonProperty("all_versions")
    private Long allVersions;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("all_versions")
    public Long getAllVersions() {
        return allVersions;
    }

    @JsonProperty("all_versions")
    public void setAllVersions(Long allVersions) {
        this.allVersions = allVersions;
    }

    public ListServiceModuleParams withAllVersions(Long allVersions) {
        this.allVersions = allVersions;
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
        return ((((("ListServiceModuleParams"+" [allVersions=")+ allVersions)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
