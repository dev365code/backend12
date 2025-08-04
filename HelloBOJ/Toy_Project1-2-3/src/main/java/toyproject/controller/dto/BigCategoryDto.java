package toyproject.controller.dto;

import java.util.List;

public class BigCategoryDto {
    private Integer majorCategoryId;     // BIG_CATEGORY.MAJOR_CATEGORY_ID
    private String  majorCategoryName;   // BIG_CATEGORY.MAJOR_CATEGORY
    private List<MiddleCategoryDto> middles;

public BigCategoryDto() {}
    public BigCategoryDto(Integer majorCategoryId, String majorCategoryName, List<MiddleCategoryDto> middles) {
        this.majorCategoryId = majorCategoryId;
        this.majorCategoryName = majorCategoryName;
        this.middles = middles;
    }

    public Integer getMajorCategoryId() {
        return majorCategoryId;
    }

    public void setMajorCategoryId(Integer majorCategoryId) {
        this.majorCategoryId = majorCategoryId;
    }

    public String getMajorCategoryName() {
        return majorCategoryName;
    }

    public void setMajorCategoryName(String majorCategoryName) {
        this.majorCategoryName = majorCategoryName;
    }

    public List<MiddleCategoryDto> getMiddles() {
        return middles;
    }

    public void setMiddles(List<MiddleCategoryDto> middles) {
        this.middles = middles;
    }
    @Override
    public String toString() {
        return "BigCategoryDto{" +
                "majorCategoryId=" + majorCategoryId +
                ", majorCategoryName='" + majorCategoryName + '\'' +
                ", middles=" + middles +
                '}';
    }
}