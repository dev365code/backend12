package toyproject.controller.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class OrderResponseDto {
    private int    productId;
    private String productImg;
    private String productName;
    private int    size;
    private int    quantity;
    private int    productPrice;
}