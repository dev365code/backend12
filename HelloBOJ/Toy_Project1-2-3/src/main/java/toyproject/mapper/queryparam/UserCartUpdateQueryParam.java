package toyproject.mapper.queryparam;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserCartUpdateQueryParam {
    private String userId;
    private int productId;
    private int size;
    private int productQuantity;
    public void setQuantityToCartItem(int quantity){
        this.productQuantity = quantity;
    }
}