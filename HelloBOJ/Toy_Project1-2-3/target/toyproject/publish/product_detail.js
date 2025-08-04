document.addEventListener("DOMContentLoaded", function () {
    const sizeButtons = document.querySelectorAll('.size-btn');
    const selectedProductContainer = document.querySelector('.selected-product');
    const productPriceInput = document.getElementById('productPrice');
    const basePrice = parseInt(productPriceInput.value, 10);  // 원가격
    const cartBtn = document.querySelector('.btn.cart');
    const cartModal = document.getElementById('cartModal');
    const closeModalBtn = document.getElementById('closeModal');
    const goCartBtn = document.getElementById('goCart');
    const buyBtn = document.querySelector('.btn.buy');
    const totalPriceEl = document.querySelector('.total-price');

    // 사이즈 버튼 클릭 시 상품 추가
    sizeButtons.forEach(btn => {
        //재고가 0이면 size btn 클릭 X
        const stock = parseInt(btn.dataset.stock, 10);
        if (stock == 0) {
            btn.disabled = true;
            return;
        }
        //각 사이즈 버튼에 대해 반복문을 돌리면 이벤트 리스너 등록
        btn.addEventListener('click', function () {

            const selectedSize = this.innerText.trim();
            //버튼에서 선택된 사이즈 값을 가져옴(텍스트로 표시된 숫자, 250)
            const stock = parseInt(this.dataset.stock, 10);
            //버튼에 data-stock 속성으로 저장된 재고 수를 숫자로 변환하여 가져옴, 10진수

            if (selectedProductContainer.querySelector(`[data-size="${selectedSize}"]`)) return;
            //이미 해당 사이즈가 리스트에 추가되어 있으면 중복 추가 방지

            sizeButtons.forEach(b => b.classList.remove('active'));
            //모든 사이즈 버튼에서 active 클래스 제거(선택된 버튼만 표시하기 위해 초기화)
            this.classList.add('active');
            //현재 클릭한 버튼에만 active 클래스 추가(선택된 상태로 표시)

            const item = document.createElement('div');//새로운 div 요소를 생성, 선택된 상품 정보담음
            item.className = 'selected-info';
            item.setAttribute('data-size', selectedSize);
            item.setAttribute('data-stock', stock);
            //선택한 사이즈와 재고를 data 속성으로 div에 저장

            //리스트에 보여질 html내용
            //사이즈 텍스트, 수량 조절버튼, 초기 수량, 가격표시, 삭제버튼
            item.innerHTML = `
                <span>${selectedSize}</span>
                <div class="quantity">
                    <button class="minus">-</button>
                    <span class="count">1</span>
                    <button class="plus">+</button>
                </div>
                <span class="price">${basePrice.toLocaleString()}원</span>
                <button class="remove">×</button>
            `;
            selectedProductContainer.appendChild(item);
            //완성된 상품정보를 리스트 영역에 추가
            updateTotal();
        });
    });

    // 수량 변경 및 삭제 처리
    selectedProductContainer.addEventListener('click', function (e) {
        const parent = e.target.closest('.selected-info');
        //클릭된 요소에서 가장 가까운 selected-info 요소를 찾아서 저장
        //상품 하나가 parent임
        if (!parent) return;

        const countEl = parent.querySelector('.count');
        let count = parseInt(countEl.innerText, 10);
        const stock = parseInt(parent.dataset.stock, 10);
        const priceEl = parent.querySelector('.price');

        if (e.target.classList.contains('plus')) {
            if (count < stock) {
                //현재 수량이 재고보다 적을 때
                count++;
                countEl.innerText = count;
                //수량 1증가, 화면에도 반영
                priceEl.innerText = (basePrice * count).toLocaleString() + '원';
                //해당 수량에 따라 가격을 계산해서 표시
                updateTotal();
                //총 가격 업데이트 함수 ㅊ=호출
            } else {
                alert(`최대 수량은 ${stock}개입니다.`);
                //재고 초과시 경고창
            }

        }

        if (e.target.classList.contains('minus')) {
            if (count > 1) {//수량이 1개보다 클 경우만(0개 이하 방지)
                count--;
                countEl.innerText = count;
                priceEl.innerText = (basePrice * count).toLocaleString() + '원';
                updateTotal();
            }
        }

        if (e.target.classList.contains('remove')) {
            parent.remove();
            updateTotal();
        }
    });

    // 총 상품 금액 계산
    function updateTotal() {
        const items = document.querySelectorAll('.selected-info');
        //선택된 모든 상품 항목(selected-info 요소들)을 가져옴
        let total = 0;
        items.forEach(item => {
            //각 상품 항목에 대해 반복
            const count = parseInt(item.querySelector('.count').innerText, 10);
            //해당 상품 항목의 수량(count)를 가져와 숫자로 변환
            total += basePrice * count;
            //개별상품가격 X 수량 을 누적하여 총합 계산
        });
        totalPriceEl.innerText = total.toLocaleString() + '원';
        //계산된 총 상품 금액을 천 단위 콤마를 포함하여 화면에 표시
    }

    // 장바구니/구매 버튼 클릭 시 선택된 상품이 있는지 확인
    function hasSelectedItems() {
        return document.querySelectorAll('.selected-info').length > 0;
        //선택된 상품(selectec-info)이 1개 이상이면 true 반환
    }

    //장바구니
    cartBtn.addEventListener('click', () => {
        // 선택 안 했을 경우
        if (!hasSelectedItems()) {
            alert('상품이 선택되지 않았습니다.');
            return;
        }

        const userId = document.getElementById('userId').value;
        const productId = parseInt(document.getElementById('productId').value);
        const selectedItems = [];

        document.querySelectorAll('.selected-info').forEach(item => {
            const size = parseInt(item.getAttribute('data-size'));
            const quantity = parseInt(item.querySelector('.count').innerText);

            selectedItems.push({
                userId: userId || null,
                productId: productId,
                size: size,
                productQuantity: quantity
            });
        });

        if (userId) {
            // 로그인 상태 → 서버에 전송
            fetch('/cart/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(selectedItems)
            })
                .then(response => {
                    if (response.ok) {
                        cartModal.style.display = 'block';
                    } else {
                        alert('상품이 이미 장바구니에 담겨있습니다');
                    }
                })
                .catch(error => {
                    console.error('장바구니 요청 중 오류:', error);
                    alert('요청 중 오류 발생');
                });
        } else {
            const actionType = "ADD_TO_CART"; // 또는 "BUY_NOW"
            const requestData = selectedItems;

            fetch('/prelogin/store', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: actionType, payload: requestData})
            }).then(() => {
                window.location.href = "/login";
            });
        }

    });

    closeModalBtn.addEventListener('click', () => {
        cartModal.style.display = 'none';
    });

    goCartBtn.addEventListener('click', () => {
        // 장바구니 페이지로 이동
        window.location.href = '/cart';
    })

    //구매하기
    buyBtn.addEventListener('click', () => {
        const userIdInput = document.getElementById('email'); // 로그인 여부 판단용
        const productIdInput = document.getElementById('productId');

        if (!productIdInput) {
            alert('상품 ID를 찾을 수 없습니다.');
            return;
        }

        const productId = parseInt(productIdInput.value);
        const selectedItems = [];

        document.querySelectorAll('.selected-info').forEach(item => {
            const size = parseInt(item.getAttribute('data-size'));
            const quantity = parseInt(item.querySelector('.count').innerText);

            selectedItems.push({
                productId: productId,
                size: size,
                quantity: quantity
            });
        });

        if (selectedItems.length === 0) {
            alert('상품이 선택되지 않았습니다.');
            return;
        }

        // ✅ 로그인 상태인 경우: 바로 주문 진행
        if (userIdInput && userIdInput.value) {
            fetch('/order/prepare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({productId: selectedItems})
            })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                    } else {
                        window.location.href = '/order';
                    }
                })
                .catch(error => {
                    console.error('fetch 오류:', error);
                    alert('요청 중 오류가 발생했습니다.');
                });

        } else {
            // ✅ 비로그인 상태일 경우: 세션에 BUY_NOW 임시 저장 후 로그인 페이지로 이동
            fetch('/prelogin/store', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type: "BUY_NOW",
                    payload: {
                        productId: selectedItems
                    }
                })
            }).then(() => {
                window.location.href = '/login';
            });
        }
    });

    // 탭 이동 (상세정보/리뷰/문의)
    document.querySelectorAll(".scroll_move").forEach(function (el) {
        el.addEventListener("click", function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                const headerHeight = document.querySelector("header").offsetHeight;//헤더 높이
                const targetPosition = target.offsetTop - headerHeight;// 헤더 높이만큼 뺌
                window.scrollTo({top: targetPosition, behavior: "smooth"});
            }
        });
    });
});