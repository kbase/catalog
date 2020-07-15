
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
 * <p>Original spec-file type: GetAppResourceEstimatorParams</p>
 * <pre>
 * module_name - module with the app of interest
 * app_id - app we're interested in the estimator for
 * tag - release, beta, dev
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "module_name",
    "app_id",
    "tag"
})
public class GetAppResourceEstimatorParams {

    @JsonProperty("module_name")
    private String moduleName;
    @JsonProperty("app_id")
    private String appId;
    @JsonProperty("tag")
    private String tag;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("module_name")
    public String getModuleName() {
        return moduleName;
    }

    @JsonProperty("module_name")
    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }

    public GetAppResourceEstimatorParams withModuleName(String moduleName) {
        this.moduleName = moduleName;
        return this;
    }

    @JsonProperty("app_id")
    public String getAppId() {
        return appId;
    }

    @JsonProperty("app_id")
    public void setAppId(String appId) {
        this.appId = appId;
    }

    public GetAppResourceEstimatorParams withAppId(String appId) {
        this.appId = appId;
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

    public GetAppResourceEstimatorParams withTag(String tag) {
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
        return ((((((((("GetAppResourceEstimatorParams"+" [moduleName=")+ moduleName)+", appId=")+ appId)+", tag=")+ tag)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
