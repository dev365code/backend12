package toyproject.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import toyproject.controller.dto.LoginUserDto;
import toyproject.controller.dto.RegisterRequestDto;
import toyproject.mapper.UserMapper;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;

    // 로그인 - 여기서 계정 잠금 설정
    public LoginUserDto login(String email, String password) {
        LoginUserDto user = userMapper.findByEmail(email);
        if (user == null) {
            throw new IllegalArgumentException("존재하지 않는 사용자입니다.");
        }

        // 실패 횟수 체크 (사용자가 존재할 때만)
        int failCount = userMapper.getFailCount(email);
        if (failCount >= 3) {
            throw new RuntimeException("계정이 잠겼습니다. 관리자에게 문의하세요.");
        }

        if (!user.getPassword().equals(password)) {
            userMapper.incrementFailCount(email);

            int newFailCount = userMapper.getFailCount(email);
            if (newFailCount >= 3) {
                throw new RuntimeException("계정이 잠겼습니다. 관리자에게 문의하세요.");
            } else {
                throw new IllegalArgumentException("비밀번호가 일치하지 않습니다. (" + newFailCount + "/3)");
            }
        }

        // 로그인 성공 시 실패 횟수 초기화
        userMapper.resetFailCount(email);
        return user;
    }

    // RegisterController에서... 회원가입
    public void register(RegisterRequestDto requestDto) {
        String userId = generateNewUserId();
        requestDto.setUserId(userId);

        // 주소 합치기
        String fullAddress = requestDto.getZipcode() + " " + requestDto.getDetailAddress();
        requestDto.setAddress(fullAddress);

        userMapper.insertUser(requestDto);
    }

    // USER_ID(사내 관리용 회원부여번호) 신규 생성
    public String generateNewUserId() {
        String maxId = userMapper.getMaxUserId();  // e.g. "U00127"
        int nextNum = 1;
        if (maxId != null && maxId.length() == 6) {
            nextNum = Integer.parseInt(maxId.substring(1)) + 1;
        }
        return String.format("U%05d", nextNum);
    }

    // 이메일 중복 확인을 위한 AJAX 호출작업
    public boolean isEmailDuplicated(String email) {
        return userMapper.isEmailDuplicated(email);
    }
}