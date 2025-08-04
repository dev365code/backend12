package toyproject.controller.dto;

import lombok.Data;

@Data
public class NoticeDto {
    private Integer noticeId;
    private String noticeTitle;
    private String noticeContent;
    private String img;
    private String createdAt;
    private String adminId;
    private Boolean isTop;
}