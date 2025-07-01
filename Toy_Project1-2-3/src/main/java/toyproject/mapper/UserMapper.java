package toyproject.mapper;

import org.apache.ibatis.annotations.Mapper;
import toyproject.controller.dto.LoginUserDto;
import toyproject.controller.dto.RegisterRequestDto;

@Mapper
public interface UserMapper {
    void insertUser(RegisterRequestDto dto);

    //  로그인 시 이메일로 사용자 조회
    LoginUserDto findByEmail(String email);

    String getMaxUserId();

    // 필요하면 이후에 이메일 중복 체크 등 추가
    boolean isEmailDuplicated(String email);

    // 로그인 실패 횟수 증가
    void incrementFailCount(String email);

    // 로그인 실패 횟수 초기화 (로그인 성공 시)
    void resetFailCount(String email);

    // 실패 횟수 조회
    int getFailCount(String email);
}