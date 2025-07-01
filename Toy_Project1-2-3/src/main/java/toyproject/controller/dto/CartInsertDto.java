package toyproject.controller.dto;

import lombok.Data;

@Data
public class CartInsertDto {
    private String userId;
    private String productId;
    private int size;
    private int productQuantity;
}