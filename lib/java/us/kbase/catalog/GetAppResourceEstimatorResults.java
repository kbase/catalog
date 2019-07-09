
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
 * <p>Original spec-file type: GetAppResourceEstimatorResults</p>
 * <pre>
 * estimator_module - module containing the estimator method
 * estimator_method - the estimator method to run
 * tag - release, beta, dev
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "estimator_module",
    "estimator_method",
    "tag"
})
public class GetAppResourceEstimatorResults {

    @JsonProperty("estimator_module")
    private String estimatorModule;
    @JsonProperty("estimator_method")
    private String estimatorMethod;
    @JsonProperty("tag")
    private String tag;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("estimator_module")
    public String getEstimatorModule() {
        return estimatorModule;
    }

    @JsonProperty("estimator_module")
    public void setEstimatorModule(String estimatorModule) {
        this.estimatorModule = estimatorModule;
    }

    public GetAppResourceEstimatorResults withEstimatorModule(String estimatorModule) {
        this.estimatorModule = estimatorModule;
        return this;
    }

    @JsonProperty("estimator_method")
    public String getEstimatorMethod() {
        return estimatorMethod;
    }

    @JsonProperty("estimator_method")
    public void setEstimatorMethod(String estimatorMethod) {
        this.estimatorMethod = estimatorMethod;
    }

    public GetAppResourceEstimatorResults withEstimatorMethod(String estimatorMethod) {
        this.estimatorMethod = estimatorMethod;
        return this;
    }

    @JsonProperty("tag")
    public String getTag() {
        return tag;
    }

    @JsonProperty("tag")
    public void setTag(String tag) {
        this.tag = tag;
    }

    public GetAppResourceEstimatorResults withTag(String tag) {
        this.tag = tag;
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
        return ((((((((("GetAppResourceEstimatorResults"+" [estimatorModule=")+ estimatorModule)+", estimatorMethod=")+ estimatorMethod)+", tag=")+ tag)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
