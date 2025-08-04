package toyproject.controller.dto;

import lombok.Data;

@Data
public class FaqDto {
    private int faqId;
    private String faqCategory;
    private String faqTitle;
    private String faqContent;
}