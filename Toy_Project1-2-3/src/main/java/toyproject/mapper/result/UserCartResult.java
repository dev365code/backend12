package toyproject.mapper.result;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserCartResult {
    private int productId;
    private String productImg;
    private String productName;
    private int size;
    private int cartProductQuantity;
    private int stockQuantity;
    private int productPrice;
}
