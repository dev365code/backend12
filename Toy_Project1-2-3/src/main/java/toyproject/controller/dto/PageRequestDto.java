package toyproject.controller.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class PageRequestDto {

    private Integer page;
    private Integer size;

    public int getPageOrDefault() {
        return page != null ? page : 1;
    }

    public int getSizeOrDefault() {
        return size != null ? size : 10;
    }
}