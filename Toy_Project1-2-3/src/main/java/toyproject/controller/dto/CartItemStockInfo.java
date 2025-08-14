package toyproject.controller.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class CartItemStockInfo {
    private int productId;
    private int size;
    private int stock;
    private String productName;
    private IssueType issueType;
}