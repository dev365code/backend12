package toyproject.controller.dto;

import lombok.*;

@Getter
@Setter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class TestRequestDto {
    private String keyword;
    private String status;
}