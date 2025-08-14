package toyproject.mapper.result;

import lombok.Data;

@Data
public class StockCheckResult {
    private int productId;
    private String productName;
    private int size;
    private int stock;
}