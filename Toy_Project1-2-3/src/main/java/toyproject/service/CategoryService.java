// src/main/java/toyproject/service/CategoryService.java
package toyproject.service;

import java.util.List;

import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import toyproject.controller.dto.BigCategoryDto;
import toyproject.controller.dto.MiddleCategoryDto;
import toyproject.controller.dto.SmallCategoryDto;
import toyproject.mapper.CategoryMapper;

@Service
public class CategoryService {
    private final CategoryMapper mapper;

    public CategoryService(CategoryMapper mapper) {
        this.mapper = mapper;
    }

    /** 모든 카테고리를 계층 구조로 조립해서 반환 */
    @Transactional(readOnly = true)
    @Cacheable("categoryTree")
    public List<BigCategoryDto> getFullCategoryTree() {
        System.out.println(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>[Cache MISS] 카테고리 트리 조회<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<");
        List<BigCategoryDto> bigs = mapper.selectAllBig();
        for (BigCategoryDto big : bigs) {
            // 미들
            List<MiddleCategoryDto> middles =
                    mapper.selectMiddleByBigId(big.getMajorCategoryId());
            for (MiddleCategoryDto mid : middles) {
                // 스몰
                List<SmallCategoryDto> smalls =
                        mapper.selectSmallByMiddleId(mid.getMidCategoryId());
                mid.setSmalls(smalls);
            }
            big.setMiddles(middles);
        }
        return bigs;
    }
}