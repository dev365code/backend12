package toyproject.controller.dto;

import lombok.Data;

@Data
public class CartUpdateRequestDto {
    private int productId;
    private int prevSize;
    private int prevQuantity;
    private int newSize;
    private int newQuantity;

}