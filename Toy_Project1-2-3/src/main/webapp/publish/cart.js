let sizeStockMap = new Map();

let currentProductPrice = 0; // 전역 변수 추가

function openModal(e) {
    e.preventDefault();
    const modal = document.getElementById("optionModal");
    currentRow = e.target.closest('tr');

    const productId = e.target.getAttribute("data-product-id");

    const prevSize = e.target.getAttribute("data-prev-size");
    const prevQuantity = e.target.getAttribute("data-prev-quantity");

    currentProductPrice = parseInt(
        currentRow.querySelector("td:nth-child(4) strong").innerText.replace(/[^0-9]/g, "")
    ) / parseInt(prevQuantity || 1);

    // 👉 모달 내부 hidden input 또는 JS 전역 변수로 저장 (예시)
    modal.setAttribute("data-product-id", productId);
    modal.setAttribute("data-prev-size", prevSize);
    modal.setAttribute("data-prev-quantity", prevQuantity);

    // ✅ 상품명 직접 설정
    const productNameText = currentRow.querySelector('.product-info strong')?.textContent || "상품명 없음";
    const productNameStrong = modal.querySelector(".popup-title + strong");
    if (productNameStrong) {
        productNameStrong.textContent = productNameText;
    }

    // 기존 이미지 동기화 (생략 가능)
    const productImg = currentRow.querySelector('.product-info img');
    const modalImg = modal.querySelector('.product-info img');
    if (productImg && modalImg) {
        modalImg.src = productImg.src;
        modalImg.alt = productImg.alt;
    }

    // 사이즈 버튼 새로 그리기 (생략: 이미 작성된 경우)
    fetch(`/cart/option/size?productId=${productId}`)
        .then(res => res.json())
        .then(data => {
            renderSizeButtons(data, prevSize, prevQuantity);
            modal.classList.add("show");
        })
        .catch(err => {
            console.error("사이즈 요청 실패", err);
            alert("옵션 정보를 불러오는 데 실패했습니다.");
        });
}

function closeModal() {
    const modal = document.getElementById("optionModal");
    modal.classList.remove("show");
}

// 모든 사이즈 버튼에 클릭 이벤트 추가
document.querySelectorAll('.size-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        // 모든 버튼에서 selected 클래스 제거
        document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));

        // 클릭된 버튼에만 selected 클래스 추가
        this.classList.add('selected');

        const selectedSize = this.textContent.trim();

        const displaySpan = document.querySelector('.selected-option span');
        if (displaySpan) {
            displaySpan.textContent = selectedSize;
        }

        const qtyInput = document.querySelector('.selected-option .quantity input');
        if (qtyInput) {
            qtyInput.value = 1;
        }
    });
});

document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const input = this.parentElement.querySelector('input');
        let value = parseInt(input.value, 10);

        let selectedSizeText = document.querySelector(".size-btn.selected")?.innerText?.trim();
        let selectedSize = selectedSizeText === "Free" ? 0 : parseInt(selectedSizeText);
        const maxStock = sizeStockMap.get(selectedSize) || 0;


        if (this.textContent === '+')
        {
            if (value < maxStock) {
                value++;
            } else {
                console.log("재고 수량을 초과할 수 없습니다.");
            }
        }
    else
        if (this.textContent === '-') {
            value = Math.max(1, value - 1);
        }
        input.value = value;

// ✅ 가격 업데이트
        const priceSpan = document.querySelector(".selected-option .price");
        if (priceSpan) {
            const total = currentProductPrice * value;
            priceSpan.textContent = `${total.toLocaleString()}원`;
        }
    });
});

// 취소 버튼
document.querySelector('.btn.cancel').addEventListener('click', () => {
    closeModal();
});

document.querySelector(".btn.confirm").addEventListener("click", function () {
    const modal = document.getElementById("optionModal");

    const productId = modal.getAttribute("data-product-id");
    const prevSize = modal.getAttribute("data-prev-size");
    const prevQuantity = modal.getAttribute("data-prev-quantity");

    const newSize = document.querySelector(".size-btn.selected").innerText;
    const newQuantity = document.querySelector(".quantity input").value;

    const payload = {
        productId: parseInt(productId),
        prevSize: parseInt(prevSize),
        prevQuantity: parseInt(prevQuantity),
        newSize: parseInt(newSize),
        newQuantity: parseInt(newQuantity)
    };

    fetch("/cart/update", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
        .then(res => {
            if (res.ok) {
                window.location.reload(); // 또는 성공 메시지
            } else {
                alert("장바구니 수정 실패");
            }
        })
        .catch(err => {
            console.error(err);
            alert("요청 실패");
        });
});

document.getElementById("purchaseSelectedBtn").addEventListener("click", () => {
    const selectedItems = [];

    document.getElementById("stock-issues-list").innerHTML = "";
    document.getElementById("stock-issues-summary").style.display = "none";

    document.querySelectorAll(".cart-item-checkbox:checked").forEach(cb => {
        const row = cb.closest("tr");

        const productId = parseInt(row.dataset.productId);

        // ✅ 사이즈는 .product-info div 내부 텍스트에서 추출
        const sizeTextMatch = row.querySelector(".product-info").innerText.match(/사이즈\s*:\s*(\d+|Free)/i);
        const size = sizeTextMatch && sizeTextMatch[1] === "Free" ? 0 : parseInt(sizeTextMatch[1]);

        // ✅ 수량은 td:nth-child(3) 텍스트에서 첫 번째 숫자만 추출 (예: "3개")
        const quantityTd = row.querySelector("td:nth-child(3)");
        const quantityMatch = quantityTd?.innerText.trim().match(/^(\d+)/);
        const quantity = quantityMatch ? parseInt(quantityMatch[1]) : 0;

        if (!isNaN(productId) && !isNaN(size) && !isNaN(quantity)) {
            selectedItems.push({productId, size, quantity});
        } else {
            console.warn("파싱 실패 - 무시됨", {productId, size, quantity});
        }
    });

    if (selectedItems.length === 0) {
        alert("상품을 선택해주세요.");
        return;
    }

    fetch("/cart/stock", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(selectedItems)
    })
        .then(async res => {
            if (res.ok) {
                // 정상: 문제 없음 → 주문 페이지 이동
                const orderRes = await fetch("/order/prepare", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({productId: selectedItems})
                });

                if (orderRes.redirected) {
                    window.location.href = orderRes.url;
                } else {
                    alert("주문 페이지 이동 실패");
                }
            } else {
                // 에러 응답 (예: 400): 문제 항목 리스트 처리
                const data = await res.json(); // 이건 서버에서 반드시 JSON으로 반환해야 함
                const issues = data.items || [];

                if (issues.length > 0) {
                    const summaryBox = document.getElementById("stock-issues-summary");
                    const summaryList = document.getElementById("stock-issues-list");
                    summaryBox.style.display = "block";
                    summaryList.innerHTML = "";

                    issues.forEach(issue => {

                        const row = document.querySelector(
                            `tr[data-product-id='${issue.productId}'][data-size='${issue.size}']`
                        );

                        if (!row) {
                            console.warn("해당 상품 행(tr)을 찾을 수 없음:", issue);
                            return;
                        }

                        const warningArea = row.querySelector(".stock-warning-area");

                        let message = "";

                        switch (issue.issueType) {
                            case "OUT_OF_STOCK":
                                message = "❌ 품절된 상품입니다.";
                                break;
                            case "NOT_ENOUGH_STOCK":
                                message = `⚠️ 재고 부족 (현재 ${issue.stock}개)`;
                                break;
                            case "UNKNOWN_PRODUCT":
                                message = "❓ 상품 정보를 찾을 수 없습니다.";
                                break;
                            default:
                                message = "⚠️ 알 수 없는 문제";
                        }

                        if (warningArea) {
                            warningArea.textContent = message;
                        } else {
                            console.warn("stock-warning-area가 없음", row);
                        }
                        const itemText = `${issue.productName} [사이즈 ${issue.size}] - ${message}`;
                        const li = document.createElement("li");
                        li.innerText = itemText;
                        summaryList.appendChild(li);
                    });
                } else {
                    alert("알 수 없는 오류 발생 (응답엔 문제가 있으나 항목이 없음)");
                }
            }
        })
        .catch(err => {
            console.error("주문 요청 실패", err);
            alert("요청 중 문제가 발생했습니다.");
        });
});

function renderSizeButtons(dataList, prevSize, prevQuantity) {
    sizeStockMap.clear(); // 기존 데이터 초기화

    const optionModal = document.getElementById("optionModal");

    // 1. productName 설정

    // 2. productId 저장용 hidden input 추가 (없으면 생성)
    let hiddenInput = document.getElementById("modalProductId");
    if (!hiddenInput) {
        hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.id = "modalProductId";
        optionModal.appendChild(hiddenInput);
    }
    hiddenInput.value = dataList[0]?.productId || "";

    // 3. 사이즈 버튼 초기화
    const container = optionModal.querySelector(".option-select");
    container.innerHTML = "<label>사이즈</label>";

    dataList.forEach(item => {
        const size = parseInt(item.size);
        const stockQty = parseInt(item.stockQuantity);

        sizeStockMap.set(size, stockQty);

        const btn = document.createElement("button");
        btn.classList.add("size-btn");
        btn.textContent = item.size == 0 ? "Free" : item.size;

        if (item.stockQuantity === 0) {
            btn.disabled = true;
            btn.style.backgroundColor = "#ccc";
            btn.title = "품절";
        } else {
            // 정상 버튼일 때만 클릭 이벤트 부여
            btn.addEventListener('click', function () {
                document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('selected'));
                this.classList.add('selected');

                currentStock = item.stockQuantity;
                document.querySelector('.selected-option span').textContent =
                    item.size == 0 ? "Free" : item.size;
                document.querySelector('.selected-option .quantity input').value = 1;

                const qty = 1;
                document.querySelector('.selected-option .quantity input').value = qty;

// ✅ 가격 초기화
                const priceSpan = document.querySelector(".selected-option .price");
                if (priceSpan) {
                    const total = currentProductPrice * qty;
                    priceSpan.textContent = `${total.toLocaleString()}원`;
                }

            });

            if (size === parseInt(prevSize)) {
                btn.classList.add('selected');

                const selectedSpan = document.querySelector('.selected-option span');
                const qtyInput = document.querySelector('.selected-option .quantity input');

                document.querySelector('.selected-option span').textContent =
                    parseInt(prevSize) === 0 ? "Free" : prevSize;
                document.querySelector('.selected-option .quantity input').value = prevQuantity;
            }
        }
        container.appendChild(btn);
    });

    const selectedSpan = document.querySelector('.selected-option span');
    const qtyInput = document.querySelector('.selected-option .quantity input');

    if (selectedSpan) selectedSpan.textContent =
        parseInt(prevSize) === 0 ? "Free" : prevSize;
    if (qtyInput) qtyInput.value = prevQuantity;
}

function renderStockStatus(cart) {
    if (cart.stockQuantity === 0) {
        return `<span class="stock-warning">❌ 제품 품절</span>`;
    } else if (cart.cartProductQuantity > cart.stockQuantity) {
        return `<span class="stock-warning">⚠️ 현재 남은 재고수량: ${cart.stockQuantity}</span>`;
    } else if (cart.stockQuantity < 5) {
        return `<span class="stock-warning">🟡 남은 재고수량: ${cart.stockQuantity}</span>`;
    } else {
        return '';
    }
}

function updateSummaryInfo() {
    const checkboxes = document.querySelectorAll(".cart-item-checkbox:checked");

    let productCount = 0;
    let totalPrice = 0;
    let totalDiscount = 0;

    checkboxes.forEach(cb => {
        const row = cb.closest("tr");
        const quantity = parseInt(row.querySelector("td:nth-child(3)").innerText);

        // 단가 계산
        const unitPrice = parseInt(
            row.querySelector("td:nth-child(4) strong").innerText.replace(/[^0-9]/g, "")
        ) / quantity;

        // 할인금액 가져오기
        const discountText = row.querySelector("td:nth-child(5)").innerText;
        const matched = discountText.match(/할인\s*-\s*([\d,]+)원/);
        const discount = matched ? parseInt(matched[1].replace(/,/g, '')) : 0;

        productCount++;
        totalPrice += unitPrice * quantity;
        totalDiscount += discount;
    });

    const shipping = productCount > 0 ? 3000 : 0;

    document.getElementById("summary-count").textContent = productCount;
    document.getElementById("summary-price").textContent = totalPrice.toLocaleString();
    document.getElementById("summary-discount").textContent = totalDiscount.toLocaleString();
    document.getElementById("summary-shipping").textContent = `+${shipping.toLocaleString()}원`;
    document.getElementById("summary-total").textContent = (totalPrice - totalDiscount + shipping).toLocaleString();
}

// ✅ 체크박스 변경 시 반영
document.addEventListener("change", function (e) {
    if (e.target.classList.contains("cart-item-checkbox")) {
        updateSummaryInfo();
    }
});

// ✅ 초기 진입 시에도 반영
document.addEventListener("DOMContentLoaded", updateSummaryInfo);

// 전체 선택 체크박스 처리
const selectAll = document.getElementById("selectAllCheckbox");
selectAll.addEventListener("change", () => {
    document.querySelectorAll(".cart-item-checkbox").forEach(cb => cb.checked = selectAll.checked);
    updateSummaryInfo();
});

// 개별 체크박스 변경 시 전체 체크 상태 동기화
document.addEventListener("change", e => {
    if (e.target.classList.contains("cart-item-checkbox")) {
        const all = document.querySelectorAll(".cart-item-checkbox");
        const checked = document.querySelectorAll(".cart-item-checkbox:checked");
        selectAll.checked = all.length === checked.length;
        updateSummary();
    }
});

document.getElementById("deleteSelectedBtn").addEventListener("click", () => {
    const selectedItems = [];

    document.querySelectorAll(".cart-item-checkbox:checked").forEach(cb => {
        const row = cb.closest("tr");
        const productId = parseInt(row.dataset.productId);
        const sizeText = row.querySelector(".product-info").innerText.match(/사이즈\s*:\s*(\d+|Free)/i);
        const size = sizeText && sizeText[1] === "Free" ? 0 : parseInt(sizeText[1]);

        selectedItems.push({productId, size});
    });

    if (selectedItems.length === 0) {
        alert("삭제할 상품을 선택해주세요.");
        return;
    }

    if (!confirm("정말 선택한 상품들을 삭제하시겠습니까?")) return;

    fetch("/cart/delete", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({items: selectedItems})
    })
        .then(res => {
            if (res.ok) {
                alert("선택된 상품이 삭제되었습니다.");
                window.location.reload();
            } else {
                alert("삭제 실패!");
            }
        })
        .catch(err => {
            console.error("삭제 요청 실패", err);
            alert("삭제 중 오류가 발생했습니다.");
        });
});

document.getElementById("purchaseAllBtn").addEventListener("click", () => {
    const allItems = [];

    document.getElementById("stock-issues-list").innerHTML = "";
    document.getElementById("stock-issues-summary").style.display = "none";

    document.querySelectorAll(".cart-table tbody tr").forEach(row => {
        const productId = parseInt(row.dataset.productId);

        const sizeTextMatch = row.querySelector(".product-info").innerText.match(/사이즈\s*:\s*(\d+|Free)/i);
        const size = sizeTextMatch && sizeTextMatch[1] === "Free" ? 0 : parseInt(sizeTextMatch[1]);

        const quantityTd = row.querySelector("td:nth-child(3)");
        const quantityMatch = quantityTd?.innerText.trim().match(/^(\d+)/);
        const quantity = quantityMatch ? parseInt(quantityMatch[1]) : 0;

        if (!isNaN(productId) && !isNaN(size) && !isNaN(quantity)) {
            allItems.push({productId, size, quantity});
        } else {
            console.warn("전체상품 파싱 실패 - 무시됨", {productId, size, quantity});
        }
    });

    if (allItems.length === 0) {
        alert("주문할 상품이 없습니다.");
        return;
    }

    fetch("/cart/stock", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(allItems)
    })
        .then(async res => {
            if (res.ok) {
                const orderRes = await fetch("/order/prepare", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({productId: allItems})
                });

                if (orderRes.redirected) {
                    window.location.href = orderRes.url;
                } else {
                    alert("주문 페이지 이동 실패");
                }
            } else {
                const data = await res.json();
                const issues = data.items || [];

                if (issues.length > 0) {
                    const summaryBox = document.getElementById("stock-issues-summary");
                    const summaryList = document.getElementById("stock-issues-list");
                    summaryBox.style.display = "block";
                    summaryList.innerHTML = "";

                    issues.forEach(issue => {
                        const row = document.querySelector(
                            `tr[data-product-id='${issue.productId}'][data-size='${issue.size}']`
                        );
                        const warningArea = row?.querySelector(".stock-warning-area");

                        let message = "";
                        switch (issue.issueType) {
                            case "OUT_OF_STOCK":
                                message = "❌ 품절된 상품입니다.";
                                break;
                            case "NOT_ENOUGH_STOCK":
                                message = `⚠️ 재고 부족 (현재 ${issue.stock}개)`;
                                break;
                            case "UNKNOWN_PRODUCT":
                                message = "❓ 상품 정보를 찾을 수 없습니다.";
                                break;
                            default:
                                message = "⚠️ 알 수 없는 문제";
                        }

                        if (warningArea) {
                            warningArea.textContent = message;
                        }

                        const itemText = `${issue.productName} [사이즈 ${issue.size}] - ${message}`;
                        const li = document.createElement("li");
                        li.innerText = itemText;
                        summaryList.appendChild(li);
                    });
                } else {
                    alert("알 수 없는 오류 발생");
                }
            }
        })
        .catch(err => {
            console.error("전체상품 주문 실패", err);
            alert("요청 중 문제가 발생했습니다.");
        });
});

// 배송비 적용: 선택된 항목 1개 이상일 경우 3000원
function updateSummary() {
    const checkboxes = document.querySelectorAll(".cart-item-checkbox:checked");
    const isSelected = checkboxes.length > 0;
    const shipping = isSelected ? 3000 : 0;
    document.getElementById("summary-shipping").textContent = `+${shipping.toLocaleString()}원`;
    // 여기에 total 계산 등 추가 처리 가능
}