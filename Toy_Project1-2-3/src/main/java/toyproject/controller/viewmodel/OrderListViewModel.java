package toyproject.controller.viewmodel;

import lombok.Builder;
import lombok.Data;
import toyproject.controller.dto.OrderResponseDto;

import java.util.List;

@Data
@Builder
public class OrderListViewModel {
    private List<OrderResponseDto> orderList;
}