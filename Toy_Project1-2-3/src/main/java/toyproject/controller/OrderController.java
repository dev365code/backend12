package toyproject.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import toyproject.controller.dto.LoginUserDto;
import toyproject.controller.dto.OrderItemRequestDto;
import toyproject.controller.dto.OrderRequestDto;
import toyproject.controller.dto.OrderResponseDto;
import toyproject.controller.viewmodel.OrderListViewModel;
import toyproject.service.OrderService;

import javax.servlet.http.HttpSession;
import java.util.*;

@Controller
@RequestMapping("/order")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    // 주문 페이지: 세션에 저장된 주문 정보를 기반으로 ViewModel 구성
    @GetMapping("")
    public String order(HttpSession session, Model model) {

        OrderRequestDto orderRequestDto = (OrderRequestDto)
                Optional.ofNullable(session.getAttribute("orderRequestDto"))
                        .orElse(session.getAttribute("orderRequest"));

        System.out.println("🔍 orderRequestDto in session: " + orderRequestDto);

        if (orderRequestDto == null) {
            return "redirect:/main";
        }

        List<Integer> productIdList = orderRequestDto.getProductId().stream()
                .map(OrderItemRequestDto::getProductId)
                .distinct()
                .toList();

        List<OrderResponseDto> orderResponseDtoList = orderService.searchProducts(productIdList);

        Map<Integer, OrderResponseDto> productInfoMap = new HashMap<>();
        for (OrderResponseDto product : orderResponseDtoList) {
            productInfoMap.put(product.getProductId(), product);
        }

        List<OrderResponseDto> finalOrderList = new ArrayList<>();
        for (OrderItemRequestDto sessionItem : orderRequestDto.getProductId()) {
            OrderResponseDto dbProduct = productInfoMap.get(sessionItem.getProductId());

            if (dbProduct != null) {
                OrderResponseDto mergedOrder = OrderResponseDto.builder()
                        .productId(dbProduct.getProductId())
                        .productImg(dbProduct.getProductImg())
                        .productName(dbProduct.getProductName())
                        .productPrice(dbProduct.getProductPrice())
                        .quantity(sessionItem.getQuantity())
                        .size(sessionItem.getSize())
                        .build();
                finalOrderList.add(mergedOrder);
            } else {
                System.out.println("DB에 존재하지 않는 상품ID: " + sessionItem.getProductId());
            }
        }

        OrderListViewModel orderListViewModel = OrderListViewModel.builder()
                .orderList(finalOrderList)
                .build();

        model.addAttribute("orderListViewModel", orderListViewModel);

        LoginUserDto loginUser = (LoginUserDto) session.getAttribute("loginUser");
        if (loginUser != null) {
            model.addAttribute("loginUser", loginUser);
        }

        return "order";
    }

    // 주문 정보 전처리용 엔드포인트: JSON으로 받은 주문 정보를 세션에 저장
    @PostMapping("/prepare")
    public String prepareOrder(@RequestBody OrderRequestDto requestDto, HttpSession session) {
        session.setAttribute("orderRequestDto", requestDto);
        return "redirect:/order"; // GET 요청으로 리디렉션
    }

    @PostMapping("/summary")
    public String orderSummary(HttpSession session, @RequestParam Map<String, String> params, Model model) {
        model.addAttribute("orderSummary", params);

        session.removeAttribute("orderRequestDto");
        session.removeAttribute("orderRequest");

        return "order_summary";
    }
}