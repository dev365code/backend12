package toyproject.controller.dto;

import lombok.Data;

@Data
public class CartStockCheckRequestDto {
    private int productId;
    private int size;
    private int quantity;
}