package toyproject.mapper;

import org.apache.ibatis.annotations.Param;
import toyproject.controller.dto.FaqDto;
import toyproject.controller.dto.GeneralBoardDto;
import toyproject.controller.dto.NoticeDto;

import java.util.List;

public interface BoardMapper {
    List<NoticeDto> selectTopNotices();

    List<NoticeDto> selectNormalNotices(@Param("limit") int limit, @Param("offset") int offset);

    int countNormalNotices();

    List<FaqDto> selectAllFaqs();

    void insertInquiry(GeneralBoardDto dto);

    List<GeneralBoardDto> selectUserInquiries(@Param("userId") String userId,
                                              @Param("limit") int limit,
                                              @Param("offset") int offset);

    int countUserInquiries(@Param("userId") String userId);
}

