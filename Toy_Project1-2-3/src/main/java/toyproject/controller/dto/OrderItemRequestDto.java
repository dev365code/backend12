package toyproject.controller.dto;

import lombok.Data;

@Data
public class OrderItemRequestDto {
    private int productId;
    private int size;
    private int quantity;
}