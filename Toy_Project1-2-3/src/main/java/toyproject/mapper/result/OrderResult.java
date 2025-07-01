package toyproject.mapper.result;

import lombok.Data;

@Data
public class OrderResult {
    private int     productId;
    private String productImg;
    private String productName;
    private int     productPrice;

}
