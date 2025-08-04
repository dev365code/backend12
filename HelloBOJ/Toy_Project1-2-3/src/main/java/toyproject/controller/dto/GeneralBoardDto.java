package toyproject.controller.dto;

import lombok.Data;

@Data
public class GeneralBoardDto {
    private int generalBoardId;
    private String generalBoardTitle;
    private String generalBoardContent;
    private String contentType;
    private String userId;
    private String img;
    private boolean replied;
    private String replyContent;
    private String createdAt;
    private String repliedAt;
    private String adminId;
}