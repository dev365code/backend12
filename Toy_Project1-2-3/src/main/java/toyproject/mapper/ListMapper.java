package toyproject.mapper;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import toyproject.controller.dto.ProductDto;

@Mapper
public interface ListMapper {
    // NEW
    int selectNewProductCount(); //NEW 상품 전체개수
    List<ProductDto> selectNewProductPage(@Param("offset") int offset,
                                          @Param("pageSize") int pageSize,
                                          @Param("sort") String sort);

    //Brand
    int selectBrandProductCount(@Param("brandId")int brandId);
    List<ProductDto> selectBrandProductPage(@Param("brandId") int brandId,
                                            @Param("offset")   int offset,
                                            @Param("pageSize") int pageSize,
                                            @Param("sort") String sort);

    List<ProductDto> selectByMiddleCategory(@Param("midCategoryId") Integer midCategoryId
    ,@Param("offset") int offset, @Param("limit") int limit, @Param("sort") String sort);

    int countByMiddleCategory(@Param("midCategoryId") Integer midCategoryId);

    List<ProductDto> selectByMiddleCategories(
            @Param("midCategoryIds") List<Integer> midCategoryIds,
            @Param("offset") int offset, @Param("pageSize") int limit, @Param("sort") String sort
    );
    int countByMiddleCategories(@Param("midCategoryIds") List<Integer> midCategoryIds);

    List<ProductDto> selectPageByMajorCategory(
            @Param("majorCategoryId") int majorCategoryId,
            @Param("offset")          int offset, @Param("pageSize") int limit, @Param("sort") String sort
    );
    int selectCountByMajorCategory(@Param("majorCategoryId") int majorCategoryId);
}