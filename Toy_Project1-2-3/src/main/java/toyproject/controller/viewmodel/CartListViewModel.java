package toyproject.controller.viewmodel;

import lombok.Builder;
import lombok.Data;
import toyproject.controller.dto.CartInfoDto;

import java.util.List;

@Data
@Builder
public class CartListViewModel {
    List<CartInfoDto> cartList;
}