
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
 * <p>Original spec-file type: GetBuildLogParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "registration_id",
    "line_start",
    "line_end"
})
public class GetBuildLogParams {

    @JsonProperty("registration_id")
    private String registrationId;
    @JsonProperty("line_start")
    private Long lineStart;
    @JsonProperty("line_end")
    private Long lineEnd;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("registration_id")
    public String getRegistrationId() {
        return registrationId;
    }

    @JsonProperty("registration_id")
    public void setRegistrationId(String registrationId) {
        this.registrationId = registrationId;
    }

    public GetBuildLogParams withRegistrationId(String registrationId) {
        this.registrationId = registrationId;
        return this;
    }

    @JsonProperty("line_start")
    public Long getLineStart() {
        return lineStart;
    }

    @JsonProperty("line_start")
    public void setLineStart(Long lineStart) {
        this.lineStart = lineStart;
    }

    public GetBuildLogParams withLineStart(Long lineStart) {
        this.lineStart = lineStart;
        return this;
    }

    @JsonProperty("line_end")
    public Long getLineEnd() {
        return lineEnd;
    }

    @JsonProperty("line_end")
    public void setLineEnd(Long lineEnd) {
        this.lineEnd = lineEnd;
    }

    public GetBuildLogParams withLineEnd(Long lineEnd) {
        this.lineEnd = lineEnd;
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
        return ((((((((("GetBuildLogParams"+" [registrationId=")+ registrationId)+", lineStart=")+ lineStart)+", lineEnd=")+ lineEnd)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
