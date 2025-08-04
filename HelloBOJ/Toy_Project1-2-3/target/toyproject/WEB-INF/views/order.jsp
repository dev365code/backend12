<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions" %>

<link rel="stylesheet" href="<%= request.getContextPath() %>/publish/reset.css"/>
<link rel="stylesheet" href="<%= request.getContextPath() %>/publish/order.css"/>

<%@ include file="header.jsp" %>

<div class="order_body">
    <div class="order_title">주문하기</div>

    <div class="container">
        <div class="main_content">
            <div class="order_info_title">
                주문상품 정보
            </div>
            <div class="order_info_content">
                <div class="order_items_form">
                    <div class="order_items">
                        <table class="order_items_table">
                            <thead>
                            <tr>
                                <th>상품/옵션 정보</th>
                                <th>수량</th>
                                <th>상품금액</th>
                                <th>할인/적립</th>
                                <th>배송비</th>
                            </tr>
                            </thead>
                            <tbody>
                            <c:forEach var="orderList" items="${orderListViewModel.orderList}" varStatus="status">
                                <tr>
                                    <td class="product-info">
                                        <img src="${orderList.productImg}" alt="상품이미지">
                                        <div class="info-text">
                                            <span class="name">${orderList.productName}</span>
                                            <span class="option">사이즈:
                                        <c:choose>
                                            <c:when test="${orderList.size == 0}">Free</c:when>
                                            <c:otherwise><c:out value="${orderList.size}"/></c:otherwise>
                                        </c:choose>
                                        </span>
                                        </div>
                                    </td>
                                    <td class="center">${orderList.quantity}개</td>
                                    <td class="center"><fmt:formatNumber value="${orderList.quantity * orderList.productPrice}" type="number"/>원</td>
                                    <td style="width: 110px">
                                        <div class="info-line">할인 <span class="val">-<fmt:formatNumber value="${((orderList.quantity * orderList.productPrice * 0.01 + 9) - ((orderList.quantity * orderList.productPrice * 0.01 + 9) % 10))}" type="number" maxFractionDigits="0"/>원</span></div>
                                        <div class="info-line">적립 <span class="val">+<fmt:formatNumber value="${((orderList.quantity * orderList.productPrice * 0.01 + 9) - ((orderList.quantity * orderList.productPrice * 0.01 + 9) % 10))}" type="number" maxFractionDigits="0"/>원</span></div>
                                    </td>

                                    <c:if test="${status.first}">
                                        <td class="center shipping-fee" rowspan="${fn:length(orderListViewModel.orderList)}">고정 배송비<br>3,000원</td>
                                    </c:if>
                                </tr>
                            </c:forEach>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="order_info_title">
                주문자 정보
            </div>
            <div class="order_info_content">
                <div class="content-form">
                    <label for="order_member" class="required-label">주문하시는 분</label>
                    <input type="text" id="order_member" name="order_member" class="input-field-flex" value="${loginUser.userName}" required>
                </div>
                <div class="content-form">
                    <label for="address" class="required-label">주소</label>
                    <input type="text" id="address" name="address" class="input-field-flex" value="${loginUser.userAddress}" required>
                </div>
                <div class="content-form">
                    <label for="detail_address">상세주소</label>
                    <input type="text" id="detail_address" name="detail_address" class="input-field-flex" value="${loginUser.userAddressDetail}" >
                </div>
                <div class="content-form">
                    <label for="phone_number" class="required-label">휴대폰 번호</label>
                    <input type="tel" id="phone_number" name="phone_number" class="input-field-flex"  value="${loginUser.userPhone}" required>
                </div>
                <div class="content-form">
                    <%
                        // 세션에서 로그인 사용자 정보 가져오기
                        toyproject.controller.dto.LoginUserDto user = (toyproject.controller.dto.LoginUserDto) session.getAttribute("loginUser");

                        String emailId = "";
                        String emailDomain = "";

                        if (user != null && user.getEmail() != null && user.getEmail().contains("@")) {
                            String[] parts = user.getEmail().split("@");
                            emailId = parts[0];
                            emailDomain = parts[1];
                        }
                    %>
                    <label for="email-id" class="required-label">이메일</label>
                    <input type="text" id="email-id" name="email-id" class="input-field-flex" value="<%= emailId %>" required />@
                    <%--suppress HtmlFormInputWithoutLabel --%>
                    <input list="email-domains" id="email-domain" name="email-domain" class="input-field-flex" value="<%= emailDomain %>" required />
                    <label for="email_type">
                        <select id="email_type" name="email_type" class="input-field-flex">
                            <option value="custom">직접 입력</option>
                            <option value="naver.com">naver.com</option>
                            <option value="hanmail.net">hanmail.net</option>
                            <option value="nate.com">nate.com</option>
                            <option value="gmail.com">gmail.com</option>
                            <option value="hotmail.com">hotmail.com</option>
                            <option value="yahoo.com">yahoo.com</option>
                        </select>
                    </label>
                </div>
            </div>

            <div class="order_info_title">
                배송 정보
            </div>
            <div class="order_info_content">
                <div class="content-form">
                    <label>배송지 확인</label>
                    <div class="radio-group">
                        <label for="default_address" class="choice_label">
                            <input type="radio" id="default_address" name="address_check" class="choices">기본 배송지
                        </label>
                        <label for="recent_address" class="choice_label">
                            <input type="radio" id="recent_address" name="address_check" class="choices">최근 배송지
                        </label>
                        <label for="custom_address" class="choice_label">
                            <input type="radio" id="custom_address" name="address_check" class="choices">직접 입력
                        </label>
                        <label for="same_as_member_info" class="choice_label">
                            <input type="radio" id="same_as_member_info" name="address_check" class="choices">주문자 정보와 동일
                        </label>
                    </div>
                </div>
                <div class="content-form">
                    <label for="receiver" class="required-label">받으실 분</label>
                    <input type="text" id="receiver" name="receiver" class="input-field-flex" required>
                </div>
                <div class="content-form">
                    <label for="receiver_address" class="required-label">받으실 곳</label>
                    <input type="text" id="receiver_address" name="receiver_address" class="input-field-flex" required readonly>
                    <button type="button" class="btn-gray">우편번호 검색</button>
                </div>
                <div class="content-form">
                    <label for="receiver_detail_address">상세주소</label>
                    <input type="text" id="receiver_detail_address" name="receiver_detail_address" class="input-field-flex" placeholder="상세주소를 입력하세요.">
                </div>
                <div class="content-form">
                    <label for="receiver_phone_number" class="required-label">휴대폰 번호</label>
                    <input type="tel" id="receiver_phone_number" name="receiver_phone_number" class="input-field-flex" required>
                </div>
                <div class="content-form">
                    <label for="delivery_message">남기실 말씀</label>
                    <input type="text" id="delivery_message" name="delivery_message" class="input-field-flex">
                </div>
            </div>

            <div class="order_info_title">
                결제 정보
            </div>
            <div class="order_info_content">
                <div class="content-form">
                    <label>할인 및 적립</label>
                    <div class="discount-info">
                        <div>
                            적용된 할인: 0원
                        </div>
                        <div>
                            발생 적립금: 0원
                        </div>
                    </div>
                </div>
                <div class="content-form">
                    <label for="coupon_check">쿠폰 사용</label>
                    <div class="input-wrapper">
                        <button type="button" id="coupon_check" name="coupon_check" class="btn-gray">쿠폰 조회 및 적용</button>
                    </div>
                </div>
                <div class="content-form">
                    <label for="use_bonuspoint">적립금 사용</label>
                    <c:set var="bonusPoint" value="${loginUser.bonusPoint}" />
                    <div class="point-info">
                        <div>
                            <input type="number" id="use_bonuspoint" name="use_bonuspoint" class="input-field-flex">
                            <div style="width: 45%">
                                <span>원</span>
                                <input type="checkbox" id="use_all_point" name="use_all_point" value="is_all">
                                <label for="use_all_point" class="bonuspoint-label">전액 사용하기 (보유 적립금: <fmt:formatNumber value="${bonusPoint}" type="number"/>원)</label>
                            </div>
                        </div>
                        <div>
                            <c:if test="${bonusPoint >= 1000}">
                                ※ 1,000원부터 <fmt:formatNumber value="${bonusPoint}" type="number"/>원까지 사용 가능합니다.
                            </c:if>
                            <c:if test="${bonusPoint < 1000}">
                                ※ 적립금은 1,000원 이상부터 사용 가능합니다.
                            </c:if>
                        </div>
                    </div>
                </div>
                <div class="content-form">
                    <label>총 결제 금액</label>
                    <div class="pre_total_price">
                        0원
                    </div>
                </div>
            </div>

            <div class="order_info_title">
                결제 수단 선택
            </div>
            <div class="order_info_content">
                <div class="content-form">
                    <label class="required-label">결제 수단</label>
                    <div class="radio-group">
                        <label for="payment_by_brief_payment" class="choice_label">
                            <input type="radio" id="payment_by_brief_payment" name="payment_method" class="choices">간편결제
                        </label>
                        <label for="payment_by_account" class="choice_label">
                            <input type="radio" id="payment_by_account" name="payment_method" class="choices">무통장 입금
                        </label>
                        <label for="payment_by_credit_card" class="choice_label">
                            <input type="radio" id="payment_by_credit_card" name="payment_method" class="choices">신용카드
                        </label>
                        <label for="payment_by_phone" class="choice_label">
                            <input type="radio" id="payment_by_phone" name="payment_method" class="choices">휴대폰 결제
                        </label>
                    </div>
                </div>
            </div>

            <div class="total_price">
                총 결제 금액(배송비 제외) 0원
            </div>
        </div>

        <div class="summary-box">
            <form>
                <div class="summary-line_item">
                    <div>총 개의 상품</div>
                </div>
                <div class="summary-line">
                    <div>총 상품 금액</div>
                    <div>0원</div>
                </div>
                <div class="summary-line">
                    <div>총 할인 금액</div>
                    <div>0원</div>
                </div>
                <div class="summary-line">
                    <div>총 배송비</div>
                    <div>0원</div>
                </div>
                <div class="summary-line_total">
                    <div>최종 결제 금액</div>
                    <div>0원</div>
                </div>
                <label for="order_agree">
                    <input type="checkbox" id="order_agree" name="order_agree" value="is_agree"/>
                    (필수) 구매하실 상품의 결제정보를 확인하였으며, 구매진행에 동의합니다.
                </label>
                <button type="submit" class="btn-order">결제하기</button>
            </form>
        </div>
    </div>
</div>
<script>
    window.addEventListener('DOMContentLoaded', function () {
        const domainInput = document.getElementById('email-domain');
        const domainSelect = document.getElementById('email_type');
        const currentDomain = domainInput.value;

        let matched = false;
        for (let i = 0; i < domainSelect.options.length; i++) {
            if (domainSelect.options[i].value === currentDomain) {
                domainSelect.selectedIndex = i;
                domainInput.disabled = true;
                matched = true;
                break;
            }
        }

        if (!matched) {
            domainSelect.value = 'custom';
            domainInput.disabled = false;
        }

        domainSelect.addEventListener('change', function () {
            if (this.value === 'custom') {
                domainInput.disabled = false;
                domainInput.value = '';
            } else {
                domainInput.disabled = true;
                domainInput.value = this.value;
            }
        });
    });
</script>
<script>
    const MAX_USABLE_POINT = ${loginUser.bonusPoint != null ? loginUser.bonusPoint : 0};
</script>
<script src="<%= request.getContextPath() %>/publish/order.js"></script>
<%--suppress JSUnresolvedLibraryURL --%>
<script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"></script>

<%@ include file="footer.jsp" %>