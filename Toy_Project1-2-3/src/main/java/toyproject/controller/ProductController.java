package toyproject.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import toyproject.controller.dto.ProductResponseDto;
import toyproject.service.ProductService;

import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/product")
@RequiredArgsConstructor
public class ProductController {
    private final ProductService productService;

    @GetMapping("/detail") // 네이밍 직관적으로 변경하기위해 /read -> /detail로 수정 by 홍성훈
    public String detail(Integer productID, Model m) {
        System.out.println("controller");
        try {
            ProductResponseDto paramDto = ProductResponseDto.builder()
                    .productID(productID)
                    .build();

//            System.out.println("넘어온 productID = " + productID);

            ProductResponseDto productDto = productService.productDetail(paramDto);
            List<Map<String, Object>> sizeList = productService.productSize(paramDto);
//            System.out.println("가져온 productDto = " + productDto);
            m.addAttribute("productDto", productDto);
            m.addAttribute("sizeList", sizeList);

//            System.out.println(">> sizeList = " + sizeList);
//            System.out.println(">> productDto = " + productDto);

        } catch (Exception e) {
            e.printStackTrace();
        }
        return "product_detail";
    }
}