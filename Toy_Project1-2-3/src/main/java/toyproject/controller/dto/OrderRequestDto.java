package toyproject.controller.dto;

import lombok.Data;

import java.util.List;

@Data
public class OrderRequestDto {
    private List<OrderItemRequestDto> productId;
}