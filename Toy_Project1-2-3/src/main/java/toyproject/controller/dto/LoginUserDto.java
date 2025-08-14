package toyproject.controller.dto;

import lombok.Data;

@Data
public class LoginUserDto {
    //DB에서 조회한 결과를 담는 역할
    private String email;
    private String password;
    private String userId;
    private int bonusPoint;
    private String userName;
    private String userAddress;
    private String userAddressDetail;
    private String userPhone;

    //생성자
    public LoginUserDto(String email, String password, String userId, int bonusPoint,  String userName, String userAddress, String userAddressDetail, String userPhone) {
        this.email = email;
        this.password = password;
        this.userId = userId;
        this.bonusPoint = bonusPoint;
        this.userName = userName;
        this.userAddress = userAddress;
        this.userAddressDetail = userAddressDetail;
        this.userPhone = userPhone;
    }

    //Getter
    public String getEmail() {
        return email;
    }
    public String getPassword() {
        return password;
    }
    public String getUserId() {
        return userId;
    }
    public int getBonusPoint() {
        return bonusPoint;
    }
    public String getUserName() { return userName; }
    public String getUserAddress() { return userAddress; }
    public String getUserAddressDetail() { return userAddressDetail; }
    public String getUserPhone() { return userPhone; }
}