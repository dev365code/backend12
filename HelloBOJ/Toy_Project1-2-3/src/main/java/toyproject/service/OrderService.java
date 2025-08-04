package toyproject.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import toyproject.controller.dto.OrderResponseDto;
import toyproject.mapper.OrderMapper;
import toyproject.mapper.result.OrderResult;

import java.util.List;

@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderMapper orderMapper;

    public List<OrderResponseDto> searchProducts(List<Integer> productIds) {
        List<OrderResult> orderResultList = orderMapper.searchProducts(productIds);

        List<OrderResponseDto> orderResponseDtos = orderResultList.stream().map(result -> OrderResponseDto.builder().productId(result.getProductId()).
                productImg(result.getProductImg()).
                productName(result.getProductName()).
                productPrice(result.getProductPrice()).build()).toList();

        return orderResponseDtos;
    }
}