package toyproject.mapper.queryparam;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class StockCheckParam {
    private int productId;
    private int size;
}