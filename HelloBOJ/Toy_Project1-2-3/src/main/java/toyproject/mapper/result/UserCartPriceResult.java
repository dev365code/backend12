package toyproject.mapper.result;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserCartPriceResult {
    private int totalProductCount;
    private int totalPrice;
    private int totalDiscount;
}
