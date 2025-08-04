package toyproject.interceptor;

import lombok.extern.slf4j.Slf4j;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@Slf4j
public class LoginCheckInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        String requestURI = request.getRequestURI();
        HttpSession session = request.getSession(false);

        // 로그인 안 되어있으면 처리
        if (session == null || session.getAttribute("loginUser") == null) {
            log.info("로그인되지 않은 사용자 요청: {}", requestURI);
            session = request.getSession(true); // 없으면 새로 만듬
            session.setAttribute("redirectAfterLogin", requestURI);
            response.sendRedirect("/login");
            return false;
        }
        return true; // 통과
    }
}