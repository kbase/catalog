
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
 * <p>Original spec-file type: AppInfo</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "id",
    "stars",
    "runs"
})
public class AppInfo {

    @JsonProperty("id")
    private String id;
    @JsonProperty("stars")
    private Long stars;
    @JsonProperty("runs")
    private Long runs;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("id")
    public String getId() {
        return id;
    }

    @JsonProperty("id")
    public void setId(String id) {
        this.id = id;
    }

    public AppInfo withId(String id) {
        this.id = id;
        return this;
    }

    @JsonProperty("stars")
    public Long getStars() {
        return stars;
    }

    @JsonProperty("stars")
    public void setStars(Long stars) {
        this.stars = stars;
    }

    public AppInfo withStars(Long stars) {
        this.stars = stars;
        return this;
    }

    @JsonProperty("runs")
    public Long getRuns() {
        return runs;
    }

    @JsonProperty("runs")
    public void setRuns(Long runs) {
        this.runs = runs;
    }

    public AppInfo withRuns(Long runs) {
        this.runs = runs;
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
        return ((((((((("AppInfo"+" [id=")+ id)+", stars=")+ stars)+", runs=")+ runs)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
