
package us.kbase.catalog;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: ListFavoriteCounts</p>
 * <pre>
 * if favorite item is given, will return stars just for that item.  If a module
 * name is given, will return stars for all methods in that module.  If none of
 * those are given, then will return stars for every method that there is info on 
 * parameters to add:
 *     list<FavoriteItem> items;
 *     list<string> module_names;
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({

})
public class ListFavoriteCounts {

    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

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
        return ((("ListFavoriteCounts"+" [additionalProperties=")+ additionalProperties)+"]");
    }

}
