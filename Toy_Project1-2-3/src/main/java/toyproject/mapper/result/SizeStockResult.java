package toyproject.mapper.result;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class SizeStockResult {
    private int productId;
    private String productName;
    private int size;
    private int stockQuantity;
}
