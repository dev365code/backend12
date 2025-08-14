package toyproject.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import toyproject.controller.dto.GeneralBoardDto;
import toyproject.controller.dto.LoginUserDto;
import toyproject.controller.dto.NoticeDto;
import toyproject.service.BoardService;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import java.util.List;

@Controller
@RequiredArgsConstructor
@RequestMapping("/board")
public class BoardController {
    private final BoardService boardService;

    @GetMapping("/notice")
    public String noticePage(@RequestParam(defaultValue = "1") int page,
                             Model model) {
        int size = 10;
        List<NoticeDto> notices = boardService.getNotices(page, size);
        int totalPages = boardService.getTotalPages(size);

        model.addAttribute("notices", notices);
        model.addAttribute("currentPage", page);
        model.addAttribute("totalPages", totalPages);

        return "board_notice";
    }

    @GetMapping("/faq")
    public String faqPage(Model model) {
        model.addAttribute("faqList", boardService.getAllFaqs());
        return "board_faq"; // => /WEB-INF/views/board_faq.jsp
    }

    @GetMapping("/inquiry")
    public String inquiryPage(@RequestParam(defaultValue = "1") int page,
                              @RequestParam(defaultValue = "10") int size,
                              HttpServletRequest request, Model model) {
        HttpSession session = request.getSession();
        LoginUserDto loginUser = (LoginUserDto) session.getAttribute("loginUser");

        if (loginUser == null) {
            // 세션에 현재 요청 URL 저장
            session.setAttribute("redirectAfterLogin", "/board/inquiry?page=" + page);
            return "redirect:/login";
        }

        String userId = loginUser.getUserId();

        List<GeneralBoardDto> inquiries = boardService.getUserInquiries(userId, page, size);
        int total = boardService.countUserInquiries(userId);
        int totalPages = (int) Math.ceil((double) total / size);

        model.addAttribute("questions", inquiries);
        model.addAttribute("page", page);
        model.addAttribute("totalPages", totalPages);

        return "board_inquiry";
    }

    @PostMapping("/inquiry/write")
    public String writeInquiry(@ModelAttribute GeneralBoardDto dto,
                               HttpServletRequest request) {
        HttpSession session = request.getSession(false);
        if (session == null || session.getAttribute("loginUser") == null)
            return "redirect:/login";

        LoginUserDto loginUser = (LoginUserDto) session.getAttribute("loginUser");
        dto.setUserId(loginUser.getUserId()); // 사용자 ID 주입

        boardService.saveInquiry(dto);

        return "redirect:/board/inquiry"; // 저장 후 목록으로 이동
    }
}