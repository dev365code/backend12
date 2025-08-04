package toyproject.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import toyproject.controller.dto.RegisterRequestDto;
import toyproject.service.UserService;

import java.util.HashMap;
import java.util.Map;

@Controller
@RequiredArgsConstructor  // 자동 생성자 생성
public class RegisterController {

    private final UserService userService;

    @GetMapping("/register")
    public String registerForm() {
        return "register";
    }

    @PostMapping("/register")
    public String register(@ModelAttribute RegisterRequestDto requestDto,
                           RedirectAttributes redirectAttributes) {
        String email = requestDto.getEmail();
        String password = requestDto.getPassword();

        // 이메일 정규식 검사
        if (!email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$")) {
            redirectAttributes.addFlashAttribute("error", "올바른 이메일 형식이 아닙니다.");
            return "redirect:/register";
        }

        // 비밀번호 유효성 검사 (추가)
        if (password.length() < 8 ||
                !password.matches(".*[a-zA-Z].*") ||
                !password.matches(".*\\d.*") ||
                !password.matches(".*[!@#$%^&*(),.?\":{}|<>].*")) {
            redirectAttributes.addFlashAttribute("error", "비밀번호는 8자 이상, 영문/숫자/특수문자를 포함해야 합니다.");
            return "redirect:/register";
        }

        try {
            // USER_ID 생성
            String userId = userService.generateNewUserId();
            requestDto.setUserId(userId);

            // 회원가입 처리
            userService.register(requestDto);

            return "redirect:/login";
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "회원가입 실패: " + e.getMessage());
            return "redirect:/register";
        }
    }

    @PostMapping("/api/check-email")
    @ResponseBody
    public Map<String, Object> checkEmailDuplicate(@RequestBody Map<String, String> request) {
        Map<String, Object> result = new HashMap<>();

        try {
            String email = request.get("email");
            boolean isDuplicate = userService.isEmailDuplicated(email);

            result.put("success", true);
            result.put("isDuplicate", isDuplicate);
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "서버 오류가 발생했습니다.");
        }

        return result;
    }

    @PostMapping("/api/send-verification")
    @ResponseBody
    public Map<String, Object> sendEmailVerification(@RequestBody Map<String, String> request) {
        Map<String, Object> result = new HashMap<>();

        try {
            String email = request.get("email");
            // toyproject용 간단 구현 - 실제로는 이메일 발송하고 토큰 저장
            // 여기서는 그냥 성공 응답만 보냄
            result.put("success", true);
            result.put("message", "인증 메일이 발송되었습니다.");
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "인증 메일 발송 중 오류가 발생했습니다.");
        }

        return result;
    }
}