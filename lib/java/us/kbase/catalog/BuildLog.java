
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
 * <p>Original spec-file type: BuildLog</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "log"
})
public class BuildLog {

    @JsonProperty("log")
    private List<BuildLogLine> log;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("log")
    public List<BuildLogLine> getLog() {
        return log;
    }

    @JsonProperty("log")
    public void setLog(List<BuildLogLine> log) {
        this.log = log;
    }

    public BuildLog withLog(List<BuildLogLine> log) {
        this.log = log;
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
        return ((((("BuildLog"+" [log=")+ log)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
