// src/main/java/toyproject/mapper/ProductOptionMapper.java
package toyproject.mapper;

import java.util.List;
import org.apache.ibatis.annotations.Param;

public interface ProductOptionMapper {
    /** 한 상품의 사이즈 리스트 */
    List<String> selectSizeByProductId(@Param("productId") int productId);
}