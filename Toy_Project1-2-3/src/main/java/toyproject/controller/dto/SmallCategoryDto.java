package toyproject.controller.dto;

public class SmallCategoryDto {
    private Integer subCategoryId;       // SMALL_CATEGORY.SUB_CATEGORY_ID
    private Integer midCategoryId;       // SMALL_CATEGORY.MID_CATEGORY_ID (FK)
    private String  subCategoryName;     // SMALL_CATEGORY.SUB_CATEGORY

    public SmallCategoryDto() {}
    public SmallCategoryDto(Integer subCategoryId, Integer midCategoryId, String subCategoryName) {
        this.subCategoryId = subCategoryId;
        this.midCategoryId = midCategoryId;
        this.subCategoryName = subCategoryName;
    }

    public Integer getSubCategoryId() {
        return subCategoryId;
    }
    public void setSubCategoryId(Integer subCategoryId) {
        this.subCategoryId = subCategoryId;
    }

    public Integer getMidCategoryId() {
        return midCategoryId;
    }
    public void setMidCategoryId(Integer midCategoryId) {
        this.midCategoryId = midCategoryId;
    }

    public String getSubCategoryName() {
        return subCategoryName;
    }
    public void setSubCategoryName(String subCategoryName) {
        this.subCategoryName = subCategoryName;
    }
}
