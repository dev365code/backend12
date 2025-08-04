package toyproject.mapper.queryparam;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserCartItemQuantityQueryParam {
    private String userId;
    private int productId;
    private int size;
}