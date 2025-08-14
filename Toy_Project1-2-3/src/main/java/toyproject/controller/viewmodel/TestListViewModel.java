package toyproject.controller.viewmodel;

import lombok.*;
import toyproject.controller.dto.TestReponseDto;

import java.util.List;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class TestListViewModel {
        private List<TestReponseDto> tests;
}