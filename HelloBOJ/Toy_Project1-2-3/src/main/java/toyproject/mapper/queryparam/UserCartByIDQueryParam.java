package toyproject.mapper.queryparam;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserCartByIDQueryParam {
    private String userId;
    private int offset;
    private int size;
}