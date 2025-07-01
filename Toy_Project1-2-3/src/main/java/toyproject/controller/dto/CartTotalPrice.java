package toyproject.controller.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CartTotalPrice {
    private int totalProductCount;
    private int totalPrice;
    private int totalDiscount;

}