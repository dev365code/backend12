package toyproject.mapper;

import java.util.List;
import toyproject.controller.dto.BigCategoryDto;
import toyproject.controller.dto.MiddleCategoryDto;
import toyproject.controller.dto.SmallCategoryDto;

public interface CategoryMapper {
    List<BigCategoryDto> selectAllBig();
    List<MiddleCategoryDto> selectMiddleByBigId(int majorCategoryId);
    List<SmallCategoryDto>  selectSmallByMiddleId(int midCategoryId);
    List<MiddleCategoryDto> selectAllMiddle();
    List<SmallCategoryDto>  selectSmall();
}