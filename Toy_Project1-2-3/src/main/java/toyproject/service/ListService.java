package toyproject.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import toyproject.controller.dto.ProductDto;
import toyproject.mapper.ListMapper;
import toyproject.mapper.ProductOptionMapper;

@Service
public class ListService {

    private final ListMapper listMapper;
    private final ProductOptionMapper productOptionMapper;

    @Autowired
    public ListService(ListMapper listMapper, ProductOptionMapper productOptionMapper) {

        this.listMapper = listMapper;
        this.productOptionMapper = productOptionMapper;
    }
    /** NEW 상품 전체 개수 */
    @Transactional(readOnly = true)
    public int getNewCount() {
        return listMapper.selectNewProductCount();
    }

    /** NEW 상품 페이지 조회 */
    @Transactional(readOnly = true)
    public List<ProductDto> getNewPage(int pageNum, int pageSize, String sort) {
        int offset = (pageNum - 1) * pageSize;
        List<ProductDto> list = listMapper.selectNewProductPage(offset, pageSize, sort);

        // 각 상품마다 옵션 사이즈를 "/"로 합쳐서 DTO에 세팅
        for (ProductDto p : list) {
            List<String> sizes = productOptionMapper.selectSizeByProductId(p.getProductId());
            String joined = sizes.stream().collect(Collectors.joining("/"));
            p.setSize(joined);
        }
        return list;
    }

    /** 브랜드별 전체 개수 */
    @Transactional(readOnly = true)
    public int getBrandCount(int brandId) {
        return listMapper.selectBrandProductCount(brandId);
    }

    /** 브랜드별 페이징 상품 리스트 */
    @Transactional(readOnly = true)
    public List<ProductDto> getBrandPage(int brandId, int pageNum, int pageSize, String sort) {
        int offset = (pageNum - 1) * pageSize;
        List<ProductDto> list = listMapper.selectBrandProductPage(brandId, offset, pageSize, sort);

        // 옵션 사이즈 조립
        for (ProductDto p : list) {
            List<String> sizes = productOptionMapper.selectSizeByProductId(p.getProductId());
            String joined = sizes.stream().collect(Collectors.joining("/"));
            p.setSize(joined);
        }
        return list;
    }

    //중분류 ID로 축구화 상품을 조회
    @Transactional(readOnly = true)
    public List<ProductDto> getByMiddleCategory(Integer midCategoryId, int page, int size, String sort) {
        int offset = (page - 1) * size;
        if(offset < 0){
            offset=0;
        }
        List<ProductDto> list = listMapper.selectByMiddleCategory(midCategoryId, offset, size, sort);
        for (ProductDto p : list) {
            List<String> sizes = productOptionMapper.selectSizeByProductId(p.getProductId());
            String joined = sizes.stream().collect(Collectors.joining("/"));
            p.setSize(joined);
        }
        return listMapper.selectByMiddleCategory(midCategoryId, offset, size, sort);
    }
    public int countByMiddleCategory(Integer midCategoryId) {
        return listMapper.countByMiddleCategory(midCategoryId);
    }

        @Transactional(readOnly = true)
        public List<ProductDto> getByMiddleCategories(List<Integer> midCategoryIds, int page, int size, String sort) {
            int offset = (page - 1) * size;
            List<ProductDto> list = listMapper.selectByMiddleCategories(midCategoryIds, offset, size, sort);
            for (ProductDto p : list) {
                List<String> sizes = productOptionMapper.selectSizeByProductId(p.getProductId());
                String joined = sizes.stream().collect(Collectors.joining("/"));
                p.setSize(joined);
            }
            return listMapper.selectByMiddleCategories(midCategoryIds, offset, size, sort);
        }

        @Transactional(readOnly = true)
        public int countByMiddleCategories(List<Integer> midCategoryIds) {
            return listMapper.countByMiddleCategories(midCategoryIds);
        }

        @Transactional(readOnly = true)
        public List<ProductDto> getByMajorCategory(Integer majorCategoryId, int page, int size, String sort) {
            int offset = (page - 1) * size;
            if(offset < 0){
                offset=0;
            }
            List<ProductDto> list = listMapper.selectPageByMajorCategory(majorCategoryId, offset, size, sort);
            for (ProductDto p : list) {
                String sizes = String.join("/", productOptionMapper.selectSizeByProductId(p.getProductId()));
                p.setSize(sizes);
            }
            return list;
        }
        @Transactional(readOnly = true)
        public int countByMajorCategory(Integer majorCategoryId) {
        return listMapper.selectCountByMajorCategory(majorCategoryId);
        }
}