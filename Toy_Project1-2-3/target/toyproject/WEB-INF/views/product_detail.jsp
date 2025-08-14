<%--
  Created by IntelliJ IDEA.
  User: polyp
  Date: 06-19(목)
  Time: 오후 2:27
  To change this template use File | Settings | File Templates.
  <%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
--%>

<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<%@ include file="header.jsp" %>
    <link rel="stylesheet" href="<%= request.getContextPath() %>/publish/product_detail.css"/>

<div class="product">
    <div class="product-detail">
        <!-- 좌측: 이미지 -->
        <div class="image-box">
            <div class="product-image" ><img src="${productDto.productIMG}"  alt="상품 이미지"></div>
            <div class="rating"><h2>5.0/5.0</h2></div>
        </div>

        <!-- 우측: 상품 정보 -->
        <div class="info-box">
            <p>${productDto.brandName}</p>
            <h2 class="product-title">
                ${productDto.productName}</h2>
                  <h2 class="product-title">  <fmt:formatNumber value="${productDto.productPrice}" type="number" />원
                    <input type="hidden" id="productPrice" value="${productDto.productPrice}">
            </h2>

            <ul class="product-info">
                <li>사일로: ${productDto.sailo}</li>
                <li>성별: ${productDto.gender}</li>
                <li>소재: ${productDto.material}</li>
                <li>색상: ${productDto.color}</li>
            </ul>

            <div class="size-section">
                <div class="size-label">사이즈</div>

                <div class="size-options">
                    <c:forEach var="size" items="${sizeList}">
                        <c:choose>
                            <c:when test="${size.size==0}">
                                <button class="size-btn"  data-size="0" data-stock="${size.stock}">Free</button>
                            </c:when>
                            <c:otherwise>
                                <button class="size-btn" data-size="${size.size}" data-stock="${size.stock}">${size.size}</button>
                            </c:otherwise>
                        </c:choose>
                    </c:forEach>
                </div>
            </div>

            <input type="hidden" id="email" value="${sessionScope.loginUser.email}" />
            <input type="hidden" id="userId" value="${sessionScope.loginUser.userId}" />
            <!-- 기본 상품 정보 -->
            <input type="hidden" name="productId" id="productId" value="${productDto.productID}" />

            <!-- 사이즈 선택 후 노출되는 상품 요약 영역 -->
            <div class="selected-product"></div>

            <div class="total">
                총 상품금액 <span class="total-price">0원</span>
            </div>

            <div class="buttons">
                <button type="submit" class="btn cart">장바구니</button> <!-- 장바구니 버튼 클릭시 화면 이동위해 type="submit" 추가 by 홍성훈 -->
                <button type="submit" class="btn buy">구매하기</button> <!-- 구매하기 버튼 클릭시 화면 이동위해 type="submit" 추가 by 홍성훈 -->
            </div>

        </div>
    </div>
    <div id="detail">
        <ul class="tab-menu">
            <li class="tab active"><a href="#detail" class="scroll_move">상세정보</a></li>
            <li class="tab"><a href="#review" class="scroll_move">상품후기</a> <span class="count">0</span></li>

            <li class="tab"><a href="#inquiry" class="scroll_move">상품문의</a> <span class="count">0</span></li>
        </ul>

        <div class="tab-content" >
            <p>- 색상 : ${productDto.color}</p>
            <p>- 소재 : ${productDto.material}</p>
            <p>- 상품 설명 : ${productDto.productInfo}</p>
        </div>
    </div>

    <div class="product-tabs" id="review">
        <ul class="tab-menu">
            <li class="tab"><a href="#detail" class="scroll_move">상세정보</a></li>
            <li class="tab active"><a href="#review" class="scroll_move">상품후기</a>  <span class="count">1</span></li>
            <li class="tab"><a href="#inquiry" class="scroll_move">상품문의</a> <span class="count">4</span></li>
        </ul>

        <div class="review-summary">
            <p>상품 총 별점</p>
            <p class="rating">5.0/5.0</p>
        </div>

        <div class="review-list" >
            <h3>상품 후기</h3>
            <div class="review-item">
                <div class="stars">★★★★★</div>
                <div class="review-content">
                    <p><strong>색감 좋고 축구할 때 입기 편해요</strong> <span class="count">(1)</span></p>
                    <div class="review-meta">
                        <span>네이버페이 구매자</span>
                        <span>2022.04.22</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="review-buttons">
            <button class="btn write-review">리뷰등록</button>
        </div>
    </div>
    <!-- 탭 메뉴 -->
    <div id="inquiry">
        <ul class="tab-menu">
            <li class="tab"><a href="#detail" class="scroll_move">상세정보</a></li>
            <li class="tab"><a href="#review" class="scroll_move">상품후기</a> <span class="count">1</span></li>
            <li class="tab active"><a href="#inquiry" class="scroll_move">상품문의</a> <span class="count">2</span></li>
        </ul>

        <!-- 상품문의 테이블 -->
        <div class="inquiry-section" >
            <h3>상품문의</h3>
            <div class="inquiry-table">
                <div class="inquiry-row">
                    <div class="no">2</div>
                    <div class="title">사이즈문의</div>
                    <div class="writer">고은*</div>
                    <div class="date">2025.06.16</div>
                    <div class="status">답변완료</div>
                </div>
                <div class="inquiry-row">
                    <div class="no">1</div>
                    <div class="title">사이즈 구분</div>
                    <div class="writer">임채*</div>
                    <div class="date">2025.05.23</div>
                    <div class="status">답변완료</div>
                </div>
                <!-- ... 나머지 항목도 동일하게 반복 -->
            </div>

            <!-- 문의하기 버튼 -->
            <div class="inquiry-footer">
                <button class="btn inquiry-btn">문의하기</button>
            </div>
        </div>
    </div>
</div>

<div id="cartModal" class="modal" style="display: none;">
    <div class="modal-content">
        <p>상품이 장바구니에 담겼습니다.<br>바로 확인하시겠습니까?</p>
        <button id="goCart">확인</button>
        <button id="closeModal">취소</button>
    </div>
</div>

<script src="<%= request.getContextPath() %>/publish/product_detail.js" defer></script>

<%@ include file="footer.jsp" %>