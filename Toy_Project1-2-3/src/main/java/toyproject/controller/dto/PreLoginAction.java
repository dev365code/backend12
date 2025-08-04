package toyproject.controller.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class PreLoginAction {
    private String type; // 예: "ADD_TO_CART" or "BUY_NOW"
    private Object payload;
}