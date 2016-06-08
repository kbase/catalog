
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
 * <p>Original spec-file type: VolumeMount</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "host_dir",
    "container_dir",
    "read_only"
})
public class VolumeMount {

    @JsonProperty("host_dir")
    private String hostDir;
    @JsonProperty("container_dir")
    private String containerDir;
    @JsonProperty("read_only")
    private Long readOnly;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("host_dir")
    public String getHostDir() {
        return hostDir;
    }

    @JsonProperty("host_dir")
    public void setHostDir(String hostDir) {
        this.hostDir = hostDir;
    }

    public VolumeMount withHostDir(String hostDir) {
        this.hostDir = hostDir;
        return this;
    }

    @JsonProperty("container_dir")
    public String getContainerDir() {
        return containerDir;
    }

    @JsonProperty("container_dir")
    public void setContainerDir(String containerDir) {
        this.containerDir = containerDir;
    }

    public VolumeMount withContainerDir(String containerDir) {
        this.containerDir = containerDir;
        return this;
    }

    @JsonProperty("read_only")
    public Long getReadOnly() {
        return readOnly;
    }

    @JsonProperty("read_only")
    public void setReadOnly(Long readOnly) {
        this.readOnly = readOnly;
    }

    public VolumeMount withReadOnly(Long readOnly) {
        this.readOnly = readOnly;
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
        return ((((((((("VolumeMount"+" [hostDir=")+ hostDir)+", containerDir=")+ containerDir)+", readOnly=")+ readOnly)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
