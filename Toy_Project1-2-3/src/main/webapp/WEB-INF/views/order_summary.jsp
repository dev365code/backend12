<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions" %>

<link rel="stylesheet" href="<%= request.getContextPath() %>/publish/order_summary.css"/>

<%@ include file="header.jsp" %>

<div class="summary_body">
    <div class="order_title">주문완료</div>

    <div class="container">
        <div class="main_content">
            <div class="order_info_title">주문요약</div>
            <div class="order_info_content thick_border">
                <div class="order_summary_info">
                    <div class="summary_item">
                        <span class="summary_label">주문번호:</span>
                        <span class="summary_value" id="order_number">-</span>
                    </div>
                    <div class="summary_item">
                        <span class="summary_label">주문일시:</span>
                        <span class="summary_value" id="order_date">-</span>
                    </div>
                    <div class="summary_item">
                        <span class="summary_label">주문자:</span>
                        <span class="summary_value" id="summary_orderer_name">-</span>
                    </div>
                    <div class="summary_item">
                        <span class="summary_label">결제수단:</span>
                        <span class="summary_value" id="summary_payment_method">-</span>
                    </div>
                </div>
            </div>

            <div class="order_info_title">주문상품 정보</div>
            <%-- 2. [수정] 정적인 상품 정보 영역을 동적으로 채울 컨테이너로 변경 --%>
            <div class="order_info_content" id="summary_product_list_container">
            </div>

            <%-- 3. [추가] JS가 복제해서 사용할 상품 아이템 템플릿 (화면에 보이지 않음) --%>
            <template id="summary_product_item_template">
                <div class="product_item">
                    <div class="product_details">
                        <div class="product_name">상품명</div>
                        <div class="product_option">옵션</div>
                    </div>
                    <div class="product_quantity">수량</div>
                    <div class="product_price">가격</div>
                </div>
            </template>

            <div class="order_info_title">주문자 정보</div>
            <div class="order_info_content">
                <div class="content-form">
                    <label>주문하시는 분</label>
                    <div class="content-value" id="display_orderer_name">-</div>
                </div>
                <%-- ... (이하 나머지 HTML 구조는 기존과 동일) ... --%>
                <div class="content-form">
                    <label>주소</label>
                    <div class="content-value" id="display_orderer_address">-</div>
                </div>
                <div class="content-form">
                    <label>휴대폰 번호</label>
                    <div class="content-value" id="display_orderer_phone">-</div>
                </div>
                <div class="content-form">
                    <label>이메일</label>
                    <div class="content-value" id="display_orderer_email">-</div>
                </div>
            </div>

            <div class="order_info_title">배송 정보</div>
            <div class="order_info_content">
                <div class="content-form">
                    <label>받으실 분</label>
                    <div class="content-value" id="display_receiver_name">-</div>
                </div>
                <div class="content-form">
                    <label>받으실 곳</label>
                    <div class="content-value" id="display_receiver_address">-</div>
                </div>
                <div class="content-form">
                    <label>휴대폰 번호</label>
                    <div class="content-value" id="display_receiver_phone">-</div>
                </div>
                <div class="content-form">
                    <label>남기실 말씀</label>
                    <div class="content-value" id="display_delivery_message">-</div>
                </div>
            </div>

            <div class="order_info_title">결제 정보</div>
            <div class="order_info_content">
                <div class="content-form">
                    <label>결제수단</label>
                    <div class="content-value" id="display_payment_method">-</div>
                </div>
                <div class="content-form">
                    <label>적용 적립금</label>
                    <div class="content-value" id="display_bonus_point">-</div>
                </div>
            </div>

            <div class="order_info_title">최종 결제사항</div>
            <div class="order_info_content">
                <div class="summary_line">
                    <div>총 상품 금액</div>
                    <div id="display_total_product_amount">-</div>
                </div>
                <div class="summary_line">
                    <div>총 할인 금액</div>
                    <div id="display_total_discount_amount">-</div>
                </div>
                <div class="summary_line">
                    <div>총 배송비</div>
                    <div id="display_total_shipping_fee">-</div>
                </div>
                <div class="summary_total">
                    <div>최종 결제금액</div>
                    <div id="display_final_amount">-</div>
                </div>
            </div>
        </div>
    </div>
</div>

<%-- 1. [추가] Controller의 Model 데이터를 JavaScript 객체로 변환하는 스크립트 --%>
<script>
    // JSTL의 escapeXml 기능을 비활성화하여 JSON 문자열이 깨지지 않도록 합니다.
    const orderSummaryData = {
        // JSON.parse를 통해 문자열을 실제 JavaScript 객체 배열로 변환합니다.
        products: ${orderSummary.products},
        ordererName: '${orderSummary.ordererName}',
        ordererAddress: '${orderSummary.ordererAddress}',
        ordererDetailAddress: '${orderSummary.ordererDetailAddress}',
        ordererPhone: '${orderSummary.ordererPhone}',
        ordererEmail: '${orderSummary.ordererEmail}',
        receiverName: '${orderSummary.receiverName}',
        receiverAddress: '${orderSummary.receiverAddress}',
        receiverDetailAddress: '${orderSummary.receiverDetailAddress}',
        receiverPhone: '${orderSummary.receiverPhone}',
        deliveryMessage: '${orderSummary.deliveryMessage}',
        paymentMethod: '${orderSummary.paymentMethod}',
        useBonusPoint: '${orderSummary.useBonusPoint}',
        totalProductAmount: '${orderSummary.totalProductAmount}',
        totalDiscountAmount: '${orderSummary.totalDiscountAmount}',
        totalShippingFee: '${orderSummary.totalShippingFee}',
        finalAmount: '${orderSummary.finalAmount}'
    };
</script>
<script src="<%= request.getContextPath() %>/publish/order_summary.js"></script>

<%@ include file="footer.jsp" %>