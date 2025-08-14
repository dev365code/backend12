package toyproject.mapper;

import toyproject.mapper.result.OrderResult;

import java.util.List;

public interface OrderMapper {
    List<OrderResult> searchProducts(List<Integer> productIds);
}