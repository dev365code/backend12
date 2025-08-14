package toyproject.mapper;

import toyproject.controller.dto.ProductResponseDto;

import java.util.List;
import java.util.Map;

public interface ProductMapper {
    public ProductResponseDto selectProductDetail(int productID);
    public List<Map<String,Object>> productSize(int productID);
}