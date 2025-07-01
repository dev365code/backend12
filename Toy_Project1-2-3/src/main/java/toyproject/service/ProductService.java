package toyproject.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import toyproject.controller.dto.ProductResponseDto;
import toyproject.mapper.ProductMapper;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ProductService {
    private final ProductMapper productMapper;

    public ProductResponseDto productDetail(ProductResponseDto productResponseDto) {

        ProductResponseDto productDetail = productMapper.selectProductDetail(productResponseDto.getProductID());

        return productDetail;
    }
    public List<Map<String,Object>> productSize(ProductResponseDto productResponseDto) {
        List<Map<String,Object>> productSize = productMapper.productSize(productResponseDto.getProductID());

        return productSize;
    }
}