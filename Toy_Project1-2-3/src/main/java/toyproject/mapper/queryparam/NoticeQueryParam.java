package toyproject.mapper.queryparam;

import lombok.Data;

@Data
public class NoticeQueryParam {
    private int page = 1;
    private int size = 10;

    public int getOffset() {
        return (page - 1) * size;
    }
}