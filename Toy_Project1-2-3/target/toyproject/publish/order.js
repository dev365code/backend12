// 유틸리티 함수: 숫자 추출
function extractNumber(text) {
    return parseInt(text.replace(/[^\d]/g, '')) || 0;
}

// 유틸리티 함수: DOM 요소 업데이트
function updateDOM(selector, text) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = text;
    } else {
        console.warn(`요소 ${selector}를 찾을 수 없음`);
    }
}

// 유틸리티 함수: 가격 포맷팅
function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 동적 rowspan 설정 함수
function setDynamicRowspan() {
    // 모든 rowspan이 비어있는 셀들 찾기
    const emptyRowspanCells = document.querySelectorAll('td[rowspan=""], th[rowspan=""]');

    emptyRowspanCells.forEach(cell => {
        const table = cell.closest('table');
        const tbody = cell.closest('tbody') || table;
        const allRows = tbody.querySelectorAll('tr');

        // 해당 셀이 있는 행의 인덱스 찾기
        let cellRowIndex = -1;
        allRows.forEach((row, index) => {
            if (row.contains(cell)) {
                cellRowIndex = index;
            }
        });

        // 해당 행부터 마지막까지의 행 개수 계산
        const rowspanValue = allRows.length - cellRowIndex;
        cell.setAttribute('rowspan', rowspanValue);
    });
}

// 주문 상품 정보 분석 (중복 제거된 핵심 함수)
function analyzeOrderItems() {
    const productRows = document.querySelectorAll('.order_items_table tbody tr');
    const totalItemCount = productRows.length;
    let totalProductAmount = 0;
    let totalDiscountAmount = 0;
    let totalEarnedPoints = 0;
    let totalShippingFee = 0;

    productRows.forEach((row, index) => {
        // 상품 금액
        const priceCell = row.querySelector('td:nth-child(3)');
        if (priceCell) {
            totalProductAmount += extractNumber(priceCell.textContent);
        }

        // 할인/적립 정보
        const discountCell = row.querySelector('td:nth-child(4)');
        if (discountCell) {
            const discountSpans = discountCell.querySelectorAll('.info-line .val');
            discountSpans.forEach(span => {
                const text = span.textContent;
                if (text.includes('-')) {
                    totalDiscountAmount += extractNumber(text);
                } else if (text.includes('+')) {
                    totalEarnedPoints += extractNumber(text);
                }
            });
        }

        // 배송비는 첫 번째 상품에서만 추출 (셀병합으로 인해)
        if (index === 0) {
            const shippingCell = row.querySelector('td:nth-child(5)');
            if (shippingCell) {
                totalShippingFee = extractNumber(shippingCell.textContent);
            }
        }
    });

    // 적립금 사용액 추가
    const useBonusPointInput = document.getElementById('use_bonuspoint');
    const bonusPointUsed = parseInt(useBonusPointInput?.value) || 0;
    totalDiscountAmount += bonusPointUsed;

    const finalAmount = totalProductAmount - totalDiscountAmount + totalShippingFee;

    return {
        totalItemCount,
        totalProductAmount,
        totalDiscountAmount,
        totalEarnedPoints,
        totalShippingFee,
        finalAmount,
        amountExcludingShipping: totalProductAmount - totalDiscountAmount
    };
}

// 이메일 도메인 선택 이벤트
document.getElementById('email_type').addEventListener('change', function () {
    const selected = this.value;
    const domainInput = document.getElementById('email-domain');
    if (selected === 'custom') {
        domainInput.value = '';
        domainInput.removeAttribute('readonly');
        domainInput.focus();
    } else {
        domainInput.value = selected;
        domainInput.setAttribute('readonly', true);
    }
});

// 주문 요약 계산 (리팩토링됨)
function calculateOrderSummary() {
    const orderInfo = analyzeOrderItems();

    updateSummaryBox(orderInfo);
    updateTotalPriceSection(orderInfo.amountExcludingShipping);
    updateDiscountAndPointsSection(orderInfo.totalDiscountAmount, orderInfo.totalEarnedPoints);
}

// 요약 박스 업데이트
function updateSummaryBox(orderInfo) {
    const { totalItemCount, totalProductAmount, totalDiscountAmount, totalShippingFee, finalAmount } = orderInfo;

    updateDOM('.summary-line_item div', `총 ${totalItemCount}개의 상품`);
    updateDOM('.summary-line:nth-child(2) div:last-child', `${formatPrice(totalProductAmount)}원`);
    updateDOM('.summary-line:nth-child(3) div:last-child', `-${formatPrice(totalDiscountAmount)}원`);
    updateDOM('.summary-line:nth-child(4) div:last-child', `+${formatPrice(totalShippingFee)}원`);
    updateDOM('.summary-line_total div:last-child', `${formatPrice(finalAmount)}원`);
}

// 총 결제 금액 섹션 업데이트
function updateTotalPriceSection(amountExcludingShipping) {
    updateDOM('.total_price', `총 결제 금액(배송비 제외) ${formatPrice(amountExcludingShipping)}원`);
    updateDOM('.pre_total_price', `${formatPrice(amountExcludingShipping)}원`);
}

// 할인 및 적립금 섹션 업데이트
function updateDiscountAndPointsSection(discountAmount, earnedPoints) {
    updateDOM('.discount-info div:nth-child(1)', `적용된 할인: (-) ${formatPrice(discountAmount)}원`);
    updateDOM('.discount-info div:nth-child(2)', `발생 적립금: (+) ${formatPrice(earnedPoints)}원`);
}

// 우편번호 검색 API
function openPostcodeSearch() {
    new daum.Postcode({
        oncomplete: function(data) {
            let addr = data.userSelectedType === 'R' ? data.roadAddress : data.jibunAddress;
            let extraAddr = '';
            if (data.userSelectedType === 'R') {
                if (data.bname !== '' && /[동|로|가]$/g.test(data.bname)) {
                    extraAddr += data.bname;
                }
                if (data.buildingName !== '' && data.apartment === 'Y') {
                    extraAddr += (extraAddr !== '' ? ', ' + data.buildingName : data.buildingName);
                }
                if (extraAddr !== '') {
                    extraAddr = ' (' + extraAddr + ')';
                }
            }
            const receiverAddressInput = document.getElementById('receiver_address');
            if (receiverAddressInput) {
                receiverAddressInput.value = `(${data.zonecode}) ${addr}${extraAddr}`;
            }
            const detailAddressInput = document.getElementById('receiver_detail_address');
            if (detailAddressInput) {
                detailAddressInput.focus();
            }
        },
        width: '100%',
        height: '100%'
    }).open();
}

// 주문자 및 배송 정보 매핑
const fieldMappings = [
    { orderer: 'order_member', receiver: 'receiver' },
    { orderer: 'address', receiver: 'receiver_address' },
    { orderer: 'detail_address', receiver: 'receiver_detail_address' },
    { orderer: 'phone_number', receiver: 'receiver_phone_number' }
];

function copyOrdererInfoToReceiver() {
    fieldMappings.forEach(({ orderer, receiver }) => {
        const ordererField = document.getElementById(orderer);
        const receiverField = document.getElementById(receiver);
        if (ordererField && receiverField) {
            receiverField.value = ordererField.value;
        }
    });
}

function clearReceiverInfo() {
    fieldMappings.forEach(({ receiver }) => {
        const receiverField = document.getElementById(receiver);
        if (receiverField) {
            receiverField.value = '';
        }
    });
}

// 주문 정보 수집 (리팩토링됨)
function collectOrderData() {
    // 상품 정보 (여러 개 수집)
    const productRows = document.querySelectorAll('.order_items_table tbody tr');
    const products = [];
    productRows.forEach(row => {
        const product = {
            name: row.querySelector('.product-info .name')?.textContent || '',
            option: row.querySelector('.product-info .option')?.textContent || '',
            quantity: row.querySelector('td:nth-child(2)')?.textContent || '',
            price: row.querySelector('td:nth-child(3)')?.textContent || ''
        };
        products.push(product);
    });

    // 주문자 정보
    const ordererName = document.getElementById('order_member')?.value || '';
    const ordererAddress = document.getElementById('address')?.value || '';
    const ordererDetailAddress = document.getElementById('detail_address')?.value || '';
    const ordererPhone = document.getElementById('phone_number')?.value || '';
    const emailId = document.getElementById('email-id')?.value || '';
    const emailDomain = document.getElementById('email-domain')?.value || '';
    const ordererEmail = emailId && emailDomain ? `${emailId}@${emailDomain}` : '';

    // 수령자 정보
    const receiverName = document.getElementById('receiver')?.value || '';
    const receiverAddress = document.getElementById('receiver_address')?.value || '';
    const receiverDetailAddress = document.getElementById('receiver_detail_address')?.value || '';
    const receiverPhone = document.getElementById('receiver_phone_number')?.value || '';
    const deliveryMessage = document.getElementById('delivery_message')?.value || '';

    // 결제 방법
    const selectedPaymentMethod = document.querySelector('input[name="payment_method"]:checked');
    let paymentMethod = '';
    if (selectedPaymentMethod) {
        const paymentMethods = {
            'payment_by_brief_payment': '간편결제',
            'payment_by_account': '무통장 입금',
            'payment_by_credit_card': '신용카드',
            'payment_by_phone': '휴대폰 결제'
        };
        paymentMethod = paymentMethods[selectedPaymentMethod.id] || '';
    }

    // 적립금 사용 정보
    const useBonusPoint = document.getElementById('use_bonuspoint')?.value || '';
    const useAllPoint = document.getElementById('use_all_point')?.checked || false;

    // 결제 금액 정보 (중복 제거 - analyzeOrderItems 사용)
    const orderInfo = analyzeOrderItems();

    return {
        products: JSON.stringify(products), // 배열을 JSON 문자열로 변환
        ordererName, ordererAddress, ordererDetailAddress, ordererPhone, ordererEmail,
        receiverName, receiverAddress, receiverDetailAddress, receiverPhone, deliveryMessage,
        paymentMethod, useBonusPoint, useAllPoint: useAllPoint ? 'true' : 'false',
        ...orderInfo
    };
}

// 폼 검증
function validateFormSequentially() {
    const requiredFields = [
        { id: 'order_member', name: '주문하시는 분', validator: () => document.getElementById('order_member').value.trim() },
        { id: 'address', name: '주문자 주소', validator: () => document.getElementById('address').value.trim() },
        { id: 'phone_number', name: '주문자 휴대폰 번호', validator: () => document.getElementById('phone_number').value.trim() },
        { id: 'email-id', name: '이메일', validator: () => {
                const emailId = document.getElementById('email-id').value.trim();
                const emailDomain = document.getElementById('email-domain').value.trim();
                return emailId && emailDomain;
            }},
        { id: 'receiver', name: '받으실 분', validator: () => document.getElementById('receiver').value.trim() },
        { id: 'receiver_address', name: '받으실 곳', validator: () => document.getElementById('receiver_address').value.trim() },
        { id: 'receiver_phone_number', name: '받는 분 휴대폰 번호', validator: () => document.getElementById('receiver_phone_number').value.trim() },
        { id: 'payment_by_brief_payment', name: '결제 수단 선택', validator: () => {
                const paymentMethodRadios = document.querySelectorAll('input[name="payment_method"]');
                return Array.from(paymentMethodRadios).some(radio => radio.checked);
            }},
        { id: 'order_agree', name: '구매 동의', validator: () => document.getElementById('order_agree').checked }
    ];

    for (const field of requiredFields) {
        if (!field.validator()) {
            return field;
        }
    }
    return null;
}

// 수정된: POST 방식으로 주문 요약 페이지로 데이터 전송
function redirectToOrderSummary() {
    const orderData = collectOrderData();

    // 동적으로 form 생성
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/order/summary';

    for (const [key, value] of Object.entries(orderData)) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = value;
        form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();
}

// 필드 포커스 이동
function focusField(fieldId) {
    const element = document.getElementById(fieldId);
    if (element) {
        element.focus();
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// 테이블이 동적으로 변경될 때 호출할 수 있는 함수
function updateAllRowspans() {
    setDynamicRowspan();
}

// DOM 로드 후 이벤트 설정
document.addEventListener('DOMContentLoaded', function() {
    // 동적 rowspan 설정
    setDynamicRowspan();

    calculateOrderSummary();

    const useBonusPointInput = document.getElementById('use_bonuspoint');
    const useAllPointCheckbox = document.getElementById('use_all_point');

    if (useBonusPointInput) {
        useBonusPointInput.addEventListener('input', calculateOrderSummary);
        useBonusPointInput.addEventListener('blur', function () {
            const rawValue = useBonusPointInput.value.trim();
            if (rawValue === '' || Number(rawValue) === 0) {
                return;
            }
            const parsedValue = Number(rawValue);
            if (isNaN(parsedValue)) {
                alert('숫자만 입력 가능합니다.');
                useBonusPointInput.value = '';
                useBonusPointInput.focus();
                return;
            }
            if (parsedValue < 1000) {
                alert('최소 사용 가능 적립금은 1000원입니다.');
                useBonusPointInput.value = '';
                useBonusPointInput.focus();
                return;
            }
            if (parsedValue > MAX_USABLE_POINT) {
                alert(`최대 사용 가능 적립금은 ${MAX_USABLE_POINT.toLocaleString()}원입니다.`);
                useBonusPointInput.value = '';
                useBonusPointInput.focus();
            }
        });
    }

    if (useAllPointCheckbox) {
        useAllPointCheckbox.addEventListener('change', function() {
            useBonusPointInput.value = this.checked ? MAX_USABLE_POINT : 0;
            calculateOrderSummary();
        });
    }

    const postcodeSearchBtn = document.querySelector('.btn-gray');
    if (postcodeSearchBtn && postcodeSearchBtn.textContent.includes('우편번호 검색')) {
        postcodeSearchBtn.addEventListener('click', openPostcodeSearch);
    }

    const addressCheckRadios = document.querySelectorAll('input[name="address_check"]');
    const sameAsOrdererRadio = document.getElementById('same_as_member_info');
    const ordererFields = fieldMappings.map(({ orderer }) => document.getElementById(orderer));

    addressCheckRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.id === 'same_as_member_info' && this.checked) {
                copyOrdererInfoToReceiver();
            } else {
                clearReceiverInfo();
            }
        });
    });

    ordererFields.forEach(field => {
        if (field) {
            field.addEventListener('input', function() {
                if (sameAsOrdererRadio.checked) {
                    copyOrdererInfoToReceiver();
                }
            });
        }
    });

    const paymentButton = document.querySelector('.btn-order');
    const form = document.querySelector('.summary-box form');

    if (form) {
        form.addEventListener('submit', e => e.preventDefault());
    }

    if (paymentButton) {
        paymentButton.addEventListener('click', function(e) {
            e.preventDefault();
            const firstMissingField = validateFormSequentially();
            if (firstMissingField) {
                alert(`'${firstMissingField.name}' 정보를 다시 확인해주세요.`);
                focusField(firstMissingField.id);
            } else {
                redirectToOrderSummary();
            }
        });
    }
});