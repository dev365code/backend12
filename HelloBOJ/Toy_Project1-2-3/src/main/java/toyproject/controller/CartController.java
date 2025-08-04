package toyproject.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import toyproject.controller.dto.*;
import toyproject.controller.viewmodel.CartListViewModel;
import toyproject.service.CartService;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.util.List;

@Controller
@Slf4j
@RequestMapping("/cart")
@RequiredArgsConstructor
public class CartController {

    private final CartService cartService;

    @GetMapping("")
    public String cart(HttpServletRequest request, @ModelAttribute PageRequestDto pageRequestDto, Model model) {

        HttpSession session = request.getSession(false); // false → 세션 없으면 null 반환

        if (session == null) {
            // 로그인 안된 상태 처리
            return "redirect:/login";
        }

        LoginUserDto loginUser = (LoginUserDto) session.getAttribute("loginUser");

        if (loginUser == null) {
            // 로그인 안된 상태 처리
            return "redirect:/login";
        }

        CartRequestDto cartRequestDto = CartRequestDto.builder().userId(loginUser.getUserId()).build();

        CartResponseDto cartInfo = cartService.searchCart(cartRequestDto);
        CartListViewModel cartListViewModel = CartListViewModel.builder()
                .cartList(cartInfo.getCartItems())
                .build();

        model.addAttribute("cartListViewModel", cartListViewModel);

        return "cart";
    }

    @GetMapping(value = "/option/size", produces = "application/json")
    @ResponseBody
    public List<SizeResponseDto> getAvailableSizes(@ModelAttribute SizeRequestDto sizeRequestDto) {

        log.info("Cart Controller _ /option/size");

        return cartService.getSizesByProductId(sizeRequestDto);

    }

    @PostMapping("/update")
    @ResponseBody
    public ResponseEntity<Void> updateCart(HttpServletRequest httpServletRequest, @RequestBody CartUpdateRequestDto request) {

        HttpSession session = httpServletRequest.getSession(false); // false → 세션 없으면 null 반환

        LoginUserDto loginUser = (LoginUserDto) session.getAttribute("loginUser");

        log.info("Cart Controller _ /update");
        System.out.println(request.toString());
        cartService.updateCartOption(loginUser.getUserId(), request); // 내부적으로 삭제 후 insert 로직
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/delete")
    @ResponseBody
    public ResponseEntity<Void> deleteSelectedItems(HttpServletRequest httpServletRequest, @RequestBody CartDeleteRequestDto deleteRequestDto) {

        log.info("Cart Controller _ /delete");

        HttpSession session = httpServletRequest.getSession(false); // false → 세션 없으면 null 반환

        LoginUserDto loginUser = (LoginUserDto) session.getAttribute("loginUser");

        cartService.deleteCartItems(loginUser.getUserId(), deleteRequestDto);

        return ResponseEntity.ok().build();
    }

    @PostMapping("/add")
    @ResponseBody
    public ResponseEntity<Void> addToCart(@RequestBody List<CartInsertDto> items) {

        for (CartInsertDto item : items) {
            cartService.insertCartItem(item);
        }
        return ResponseEntity.ok().build();
    }

    @PostMapping("/stock")
    @ResponseBody
    public ResponseEntity<CartStockIssueResponseDto> checkCartStock(
            @RequestBody List<CartStockCheckRequestDto> items) {

        List<CartItemStockInfo> issues = cartService.findStockIssues(items);

        if (issues.isEmpty()) {
            return ResponseEntity.ok().build();
        }

        return ResponseEntity.badRequest().body(
                CartStockIssueResponseDto.builder()
                        .items(issues)
                        .build()
        );
    }
}