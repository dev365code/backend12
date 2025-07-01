package toyproject.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import toyproject.controller.dto.FaqDto;
import toyproject.controller.dto.GeneralBoardDto;
import toyproject.controller.dto.NoticeDto;
import toyproject.mapper.BoardMapper;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class BoardService {

    private final BoardMapper boardMapper;

    public List<NoticeDto> getNotices(int page, int size) {
        int offset = (page - 1) * size;

        List<NoticeDto> result = new ArrayList<>();
        result.addAll(boardMapper.selectTopNotices()); // 고정 공지
        result.addAll(boardMapper.selectNormalNotices(size, offset)); // 일반 공지

        return result;
    }

    public List<FaqDto> getAllFaqs() {
        return boardMapper.selectAllFaqs();
    }

    public int getTotalPages(int size) {
        int count = boardMapper.countNormalNotices();
        return (int) Math.ceil((double) count / size);
    }

    public List<GeneralBoardDto> getUserInquiries(String userId, int page, int size) {
        int offset = (page - 1) * size;
        return boardMapper.selectUserInquiries(userId, size, offset);
    }

    public int countUserInquiries(String userId) {
        return boardMapper.countUserInquiries(userId);
    }

    public void saveInquiry(GeneralBoardDto dto) {
    boardMapper.insertInquiry(dto);
}
}