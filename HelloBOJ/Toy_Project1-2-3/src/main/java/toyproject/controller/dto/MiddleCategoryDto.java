package toyproject.controller.dto;

import java.util.List;

public class MiddleCategoryDto {
    private Integer midCategoryId;       // MIDDLE_CATEGORY.MID_CATEGORY_ID
    private Integer majorCategoryId;     // MIDDLE_CATEGORY.MAJOR_CATEGORY_ID (FK)
    private String  midCategoryName;     // MIDDLE_CATEGORY.MID_CATEGORY
    private List<SmallCategoryDto> smalls;

    public MiddleCategoryDto() {
    }

    public MiddleCategoryDto(Integer midCategoryId, Integer majorCategoryId, String midCategoryName, List<SmallCategoryDto> smalls) {
        this.midCategoryId = midCategoryId;
        this.majorCategoryId = majorCategoryId;
        this.midCategoryName = midCategoryName;
        this.smalls = smalls;
    }

    public Integer getMidCategoryId() {
        return midCategoryId;
    }

    public void setMidCategoryId(Integer midCategoryId) {
        this.midCategoryId = midCategoryId;
    }

    public Integer getMajorCategoryId() {
        return majorCategoryId;
    }

    public void setMajorCategoryId(Integer majorCategoryId) {
        this.majorCategoryId = majorCategoryId;
    }

    public String getMidCategoryName() {
        return midCategoryName;
    }

    public void setMidCategoryName(String midCategoryName) {
        this.midCategoryName = midCategoryName;
    }

    public List<SmallCategoryDto> getSmalls() {
        return smalls;
    }

    public void setSmalls(List<SmallCategoryDto> smalls) {
        this.smalls = smalls;
    }
}
