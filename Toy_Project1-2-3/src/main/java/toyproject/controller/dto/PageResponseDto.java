package toyproject.controller.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class PageResponseDto {
    private int     page;
    private int     size;
    private int     totalElements;
    private int     totalPage;
    private boolean first;
    private boolean last;
}