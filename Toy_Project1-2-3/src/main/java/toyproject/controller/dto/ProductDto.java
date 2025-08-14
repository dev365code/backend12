package toyproject.controller.dto;

import java.math.BigDecimal;

public class ProductDto {
    private Integer productId;
    private Integer brandId;
    private Integer subCategoryId;
    private String  productName;
    private String  img;
    private String  sailo;
    private String  material;
    private String  color;
    private BigDecimal avgScore;
    private String  detailInfo;
    private Integer price;
    private String  basicInfo;
    private Boolean isNew;
    private Boolean isEvent;
    private String size;
    private String brandName;

    public ProductDto() {
    }

    public ProductDto(Integer productId, Integer brandId, Integer subCategoryId, String productName, String img, String sailo, String material, String color, BigDecimal avgScore, String detailInfo, Integer price, String basicInfo, Boolean isNew, Boolean isEvent, String size) {
        this.productId = productId;
        this.brandId = brandId;
        this.subCategoryId = subCategoryId;
        this.productName = productName;
        this.img = img;
        this.sailo = sailo;
        this.material = material;
        this.color = color;
        this.avgScore = avgScore;
        this.detailInfo = detailInfo;
        this.price = price;
        this.basicInfo = basicInfo;
        this.isNew = isNew;
        this.isEvent = isEvent;
        this.size = size;
    }

    @Override
    public String toString() {
        return "ProductDto{" +
                "productId=" + productId +
                ", brandId=" + brandId +
                ", subCategoryId=" + subCategoryId +
                ", productName='" + productName + '\'' +
                ", img='" + img + '\'' +
                ", sailo='" + sailo + '\'' +
                ", material='" + material + '\'' +
                ", color='" + color + '\'' +
                ", avgScore=" + avgScore +
                ", detailInfo='" + detailInfo + '\'' +
                ", price=" + price +
                ", basicInfo='" + basicInfo + '\'' +
                ", isNew=" + isNew +
                ", isEvent=" + isEvent +
                '}';
    }

    public String getBrandName() {
        return brandName;
    }

    public void setBrandName(String brandName) {
        this.brandName = brandName;
    }

    public String getSize() {
        return size;
    }

    public void setSize(String size) {
        this.size = size;
    }

    public Integer getProductId() {
        return productId;
    }

    public void setProductId(Integer productId) {
        this.productId = productId;
    }

    public Integer getBrandId() {
        return brandId;
    }

    public void setBrandId(Integer brandId) {
        this.brandId = brandId;
    }

    public Integer getSubCategoryId() {
        return subCategoryId;
    }

    public void setSubCategoryId(Integer subCategoryId) {
        this.subCategoryId = subCategoryId;
    }

    public String getProductName() {
        return productName;
    }

    public void setProductName(String productName) {
        this.productName = productName;
    }

    public String getImg() {
        return img;
    }

    public void setImg(String img) {
        this.img = img;
    }

    public String getSailo() {
        return sailo;
    }

    public void setSailo(String sailo) {
        this.sailo = sailo;
    }

    public String getMaterial() {
        return material;
    }

    public void setMaterial(String material) {
        this.material = material;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public BigDecimal getAvgScore() {
        return avgScore;
    }

    public void setAvgScore(BigDecimal avgScore) {
        this.avgScore = avgScore;
    }

    public String getDetailInfo() {
        return detailInfo;
    }

    public void setDetailInfo(String detailInfo) {
        this.detailInfo = detailInfo;
    }

    public Integer getPrice() {
        return price;
    }

    public void setPrice(Integer price) {
        this.price = price;
    }

    public String getBasicInfo() {
        return basicInfo;
    }

    public void setBasicInfo(String basicInfo) {
        this.basicInfo = basicInfo;
    }

    public Boolean getNew() {
        return isNew;
    }

    public void setNew(Boolean aNew) {
        isNew = aNew;
    }

    public Boolean getEvent() {
        return isEvent;
    }

    public void setEvent(Boolean event) {
        isEvent = event;
    }
}