package toyproject.controller;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import toyproject.controller.dto.CartInsertDto;
import toyproject.controller.dto.LoginUserDto;
import toyproject.controller.dto.OrderRequestDto;
import toyproject.controller.dto.PreLoginAction;
import toyproject.service.CartService;
import toyproject.service.UserService;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.util.List;

@Controller
@RequiredArgsConstructor
public class LoginController {

    private final UserService userService;
    private final CartService cartService;

    // 8080에서 main으로 포워딩
    @GetMapping("/")
    public String mainHomePage() {
        return "redirect:/main";
    }

    // 로그인 폼 화면
    @GetMapping("/login")
    public String loginForm() {
        return "user_login";  // /WEB-INF/views/user_login.jsp
    }

    // 로그인 처리
    @PostMapping("/login")
    public String login(@RequestParam String email,
                        @RequestParam String password,
                        HttpServletRequest request,
                        RedirectAttributes redirectAttributes) {

        // 이메일 정규식 : 서버단에서 이메일 형식 유효성 검증 - js에서 검증 및 서버 체크
        if (!email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$")) {
            redirectAttributes.addFlashAttribute("error", "올바른 이메일 형식이 아닙니다.");
            return "redirect:/login";
        }
        try {
            LoginUserDto user = userService.login(email, password);
            HttpSession session = request.getSession(true);
            session.setAttribute("loginUser", user);

            PreLoginAction action = (PreLoginAction) session.getAttribute("preLoginAction");
            if (action != null) {
                session.removeAttribute("preLoginAction");

                if ("ADD_TO_CART".equals(action.getType())) {

                    ObjectMapper objectMapper = new ObjectMapper();
                    List<CartInsertDto> items = objectMapper.convertValue(
                            action.getPayload(),
                            new TypeReference<List<CartInsertDto>>() {
                            }
                    );

                    for (CartInsertDto item : items) {
                        item.setUserId(user.getUserId());
                        cartService.insertCartItem(item);
                    }
                    return "redirect:/cart";
                }

                if ("BUY_NOW".equals(action.getType())) {
                    ObjectMapper objectMapper = new ObjectMapper();
                    OrderRequestDto orderRequest = objectMapper.convertValue(
                            action.getPayload(),
                            OrderRequestDto.class
                    );
                    session.setAttribute("orderRequestDto", orderRequest);
                    return "redirect:/order";
                }
            }

            // 일반 리다이렉션 처리 (Interceptor에 의해 저장된 URL)
            String redirectUri = (String) session.getAttribute("redirectAfterLogin");
            if (redirectUri != null) {
                session.removeAttribute("redirectAfterLogin");
                return "redirect:" + redirectUri;
            }

            return "redirect:/main"; // 기본 리다이렉트

        } catch (IllegalArgumentException e) {
            // 일반 로그인 실패 처리 (비밀번호 틀림 등)
            redirectAttributes.addFlashAttribute("error", e.getMessage());
            return "redirect:/login";
        } catch (RuntimeException e) {
            // 계정 잠금 등의 기타 RuntimeException 처리
            redirectAttributes.addFlashAttribute("error", e.getMessage());
            return "redirect:/login";
        }
    }

    // 메인페이지 이동
    @GetMapping("/main")
    public String home(Model model) {
        model.addAttribute("contentPage", "rolling.jsp");
        return "main";
    }

    // 로그아웃 처리
    @GetMapping("/logout")
    public String logout(HttpServletRequest request) {
        request.getSession().invalidate(); // 세션 완전 초기화
        return "redirect:/main"; // 로그아웃 후 메인으로 이동
    }

    @PostMapping("/prelogin/store")
    @ResponseBody
    public ResponseEntity<Void> storePreLoginAction(@RequestBody PreLoginAction action, HttpSession session) {
        session.setAttribute("preLoginAction", action);
        return ResponseEntity.ok().build();
    }
}