package toyproject.controller.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class SizeResponseDto {
    private int productId;
    private String productName;
    private int size;
    private int stockQuantity;
}