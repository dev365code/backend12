package toyproject.controller.dto;

import lombok.Data;

@Data
public class LoginRequestDto {
    // 로그인 요청을 받는 역할
    private String email;
    private String password;
    private String userId;
}