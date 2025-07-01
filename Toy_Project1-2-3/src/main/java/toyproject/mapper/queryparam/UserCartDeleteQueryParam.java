package toyproject.mapper.queryparam;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserCartDeleteQueryParam {
    private String userId;
    private int productId;
    private int size;
    private int quantity;
}