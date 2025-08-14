package toyproject.controller.dto;;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@AllArgsConstructor
public class ProductResponseDto {
    private Integer productID;
    private String brandName;
    private String productName;
    private String productIMG;
    private String sailo;
    private String gender;
    private String material;
    private String color;
    private int    productScore;
    private String productInfo;
    private int    productPrice;
}