// 기존 order_summary.js 파일의 내용을 아래 코드로 대체하거나 수정하세요.

document.addEventListener('DOMContentLoaded', function() {
    // URL 파라미터 대신 JSP에서 생성한 전역 변수 orderSummaryData를 사용합니다.
    if (typeof orderSummaryData !== 'undefined') {
        generateOrderInfo();
        displayProductInfo(orderSummaryData);
        displayOrdererInfo(orderSummaryData);
        displayShippingInfo(orderSummaryData);
        displayPaymentInfo(orderSummaryData);
        displayFinalPayment(orderSummaryData);
    } else {
        console.error('주문 데이터를 불러오지 못했습니다.');
    }
});

function generateOrderInfo() {
    const now = new Date();
    const orderNumber = now.getFullYear() +
        String(now.getMonth() + 1).padStart(2, '0') +
        String(now.getDate()).padStart(2, '0') +
        String(now.getHours()).padStart(2, '0') +
        String(now.getMinutes()).padStart(2, '0') +
        String(now.getSeconds()).padStart(2, '0');
    const orderDate = now.getFullYear() + '년 ' +
        (now.getMonth() + 1) + '월 ' +
        now.getDate() + '일 ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0');

    document.getElementById('order_number').textContent = orderNumber;
    document.getElementById('order_date').textContent = orderDate;
}

// [수정] 여러 상품을 동적으로 표시하는 함수
function displayProductInfo(data) {
    const container = document.getElementById('summary_product_list_container');
    const template = document.getElementById('summary_product_item_template');

    if (!container || !template) {
        console.error('상품 목록을 표시할 영역을 찾을 수 없습니다.');
        return;
    }

    // products 배열을 순회하며 템플릿을 복제하고 데이터를 채워넣습니다.
    data.products.forEach(product => {
        const productNode = template.content.cloneNode(true); // 템플릿 복제

        productNode.querySelector('.product_name').textContent = product.name || '상품 정보 없음';
        productNode.querySelector('.product_option').textContent = product.option || '-';
        productNode.querySelector('.product_quantity').textContent = product.quantity || '-';
        productNode.querySelector('.product_price').textContent = product.price || '0원';

        container.appendChild(productNode); // 컨테이너에 추가
    });
}

function displayOrdererInfo(data) {
    const ordererName = data.ordererName || '-';
    let fullAddress = data.ordererAddress || '';
    if (data.ordererDetailAddress) {
        fullAddress += (fullAddress ? ', ' : '') + data.ordererDetailAddress;
    }
    if (!fullAddress) fullAddress = '-';

    document.getElementById('display_orderer_name').textContent = ordererName;
    document.getElementById('summary_orderer_name').textContent = ordererName; // 주문요약 부분도 채워줌
    document.getElementById('display_orderer_address').textContent = fullAddress;
    document.getElementById('display_orderer_phone').textContent = data.ordererPhone || '-';
    document.getElementById('display_orderer_email').textContent = data.ordererEmail || '-';
}

function displayShippingInfo(data) {
    let fullAddress = data.receiverAddress || '';
    if (data.receiverDetailAddress) {
        fullAddress += (fullAddress ? ', ' : '') + data.receiverDetailAddress;
    }
    if (!fullAddress) fullAddress = '-';

    document.getElementById('display_receiver_name').textContent = data.receiverName || '-';
    document.getElementById('display_receiver_address').textContent = fullAddress;
    document.getElementById('display_receiver_phone').textContent = data.receiverPhone || '-';
    document.getElementById('display_delivery_message').textContent = data.deliveryMessage || '-';
}

function displayPaymentInfo(data) {
    const useBonusPoint = parseInt(data.useBonusPoint) || 0;
    const bonusPointDisplay = useBonusPoint > 0 ? formatPrice(useBonusPoint) + '원' : '0원';

    document.getElementById('display_payment_method').textContent = data.paymentMethod || '-';
    document.getElementById('summary_payment_method').textContent = data.paymentMethod || '-'; // 주문요약 부분도 채워줌
    document.getElementById('display_bonus_point').textContent = bonusPointDisplay;
}

function displayFinalPayment(data) {
    const totalProductAmount = parseInt(data.totalProductAmount) || 0;
    const totalDiscountAmount = parseInt(data.totalDiscountAmount) || 0;
    const totalShippingFee = parseInt(data.totalShippingFee) || 0;
    const finalAmount = parseInt(data.finalAmount) || 0;

    document.getElementById('display_total_product_amount').textContent = formatPrice(totalProductAmount) + '원';
    document.getElementById('display_total_discount_amount').textContent = '-' + formatPrice(totalDiscountAmount) + '원';
    document.getElementById('display_total_shipping_fee').textContent = '+' + formatPrice(totalShippingFee) + '원';
    document.getElementById('display_final_amount').textContent = formatPrice(finalAmount) + '원';
}

function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}