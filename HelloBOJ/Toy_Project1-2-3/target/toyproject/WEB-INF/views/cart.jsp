<%--suppress ALL --%>
<%@ page contentType="text/html; charset=UTF-8" %>

<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<%@ include file="header.jsp" %>

<div class="page-wrapper">
    <div class="content-wrapper">

        <div class="container">
            <h1 class="title">장바구니 </h1>
            <div class="cart-wrapper">
                <!-- 상품 목록 -->
                <div class="cart-items">
                    <table class="cart-table">
                        <thead>
                        <tr>
                            <td><input type="checkbox" id="selectAllCheckbox"/></td>
                            <td>상품/옵션 정보</td>
                            <td>수량</td>
                            <td>상품금액</td>
                            <td>할인/적립</td>
                        </tr>
                        </thead>
                        <tbody>
                        <c:forEach var="cart" items="${cartListViewModel.cartList}">
                            <tr data-product-id="${cart.productId}" data-size="${cart.size}"
                                style="white-space: nowrap;">
                                <td><input type="checkbox" class="cart-item-checkbox"/></td>
                                <td>
                                    <div class="product-info">
                                        <img src="${cart.productImg}" alt="상품 이미지">
                                        <div>
                                            <strong><c:out value="${cart.productName}"/></strong><br/><br/>
                                            사이즈 :
                                            <c:choose>
                                                <c:when test="${cart.size == 0}">Free</c:when>
                                                <c:otherwise><c:out value="${cart.size}"/></c:otherwise>
                                            </c:choose>
                                            <div class="stock-warning-area"
                                                 style="color: red; font-weight: bold; margin-top: 5px;"></div>
                                        </div>
                                    </div>
                                </td>
                                <td class="${cart.stockQuantity == 0 ? 'sold-out' : ''}"
                                    style="align-content: center; text-align: center;">
                                    <c:out value="${cart.cartProductQuantity}"/>개<br/>

                                    <c:choose>
                                        <c:when test="${cart.stockQuantity == 0}">
                                            <span class="stock-warning">❌ 제품 품절</span>
                                        </c:when>
                                        <c:when test="${cart.cartProductQuantity > cart.stockQuantity}">
                                            <span class="stock-warning">⚠️ 현재 남은 재고수량: ${cart.stockQuantity}</span>
                                        </c:when>
                                        <c:when test="${cart.stockQuantity < 5}">
                                            <span class="stock-warning">🟡 남은 재고수량: ${cart.stockQuantity}</span>
                                        </c:when>
                                    </c:choose>

                                    <br/>
                                    <a href="#" onclick="openModal(event)"
                                       data-product-id="${cart.productId}"
                                       data-prev-size="${cart.size}"
                                       data-prev-quantity="${cart.cartProductQuantity}">
                                        옵션/수정변경
                                    </a></td>
                                <td style="align-content: center; text-align: center;">
                                    <strong>
                                        <fmt:formatNumber value="${cart.productPrice * cart.cartProductQuantity}"
                                                          type="number"
                                        />원
                                    </strong>
                                </td>
                                <td style="align-content: center; text-align: center;">
                                    <c:set var="discount"
                                           value="${(cart.productPrice * cart.cartProductQuantity * 0.01 + 9) - ((cart.productPrice * cart.cartProductQuantity * 0.01 + 9) % 10)}"/>
                                    할인 -<fmt:formatNumber value="${discount}" type="number" maxFractionDigits="0"/>원
                                    <br/><br/>
                                    적립 +<fmt:formatNumber value="${discount}" type="number" maxFractionDigits="0"/>원
                                </td>
                            </tr>
                        </c:forEach>
                        </tbody>
                    </table>

                    <div class="cart-actions">
                        <span id="deleteSelectedBtn" class="delete-text">선택삭제</span>
                    </div>
                </div>

                <!-- 결제 정보 -->
                <div class="summary-box">
                    <h3>
                        총 <strong id="summary-count">0</strong>개의 상품
                    </h3>

                    <div class="summary-row">
                        총 상품금액
                        <span><span id="summary-price">0</span>원</span>
                    </div>

                    <div class="summary-row">
                        총 할인금액
                        <span>-<span id="summary-discount">0</span>원</span>
                    </div>

                    <div class="summary-row">
                        총 배송비
                        <span id="summary-shipping">+0원</span>
                    </div>

                    <hr/>

                    <div class="total-price">
                        결제예상금액
                        <strong><span id="summary-total">0</span>원</strong>
                    </div>

                    <button class="btn black" id="purchaseAllBtn">전체상품 구매하기</button>
                    <button class="btn white" id="purchaseSelectedBtn">선택상품 구매하기</button>

                    <div id="stock-issues-summary" class="issue-summary-box" style="display:none;">
                        <h4>🧾 주문 불가 상품 요약</h4>
                        <ul id="stock-issues-list"></ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 옵션 모달 -->
    <div class="modal" id="optionModal">
        <div class="modal-content">
            <button class="close-btn" onclick="closeModal()">×</button>
            <h2 class="popup-title">옵션선택</h2>
            <strong></strong> <span class="code"></span><br/>

            <div class="product-info">
                <img src="https://capostoreimg.godohosting.com/store5/PMW/NPMW65592403.jpg" alt="상품 이미지">
                <div class="info-text"></div>
            </div>

            <hr/>

            <div class="option-select">
                <label>사이즈</label>
            </div>

            <div class="selected-option">
                <span>2XL</span>
                <div class="quantity">
                    <button class="qty-btn">-</button>
                    <input type="text" value="1"/>
                    <button class="qty-btn">+</button>
                </div>
                <span class="price">0원</span>
            </div>

            <div class="popup-footer">
                <button class="btn cancel">취소</button>
                <button class="btn confirm">확인</button>
            </div>
        </div>
    </div>
    <link rel="stylesheet" href="<%= request.getContextPath() %>/publish/cart.css"/>
    <script src="<%= request.getContextPath() %>/publish/cart.js" defer></script>
    <%@ include file="footer.jsp" %>
</div>