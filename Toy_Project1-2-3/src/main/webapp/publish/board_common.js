document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab");
    const icons = document.querySelectorAll(".faq-icon");
    const faqItems = document.querySelectorAll(".faq-item");
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");
    const openBtn = document.getElementById("openModalBtn");
    const modal = document.getElementById("inquiryModal");

    // 탭 필터링
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const category = tab.getAttribute("data-category");
            faqItems.forEach(item => {
                const matchesCategory = category === "전체" || item.getAttribute("data-category") === category;
                item.style.display = matchesCategory ? "" : "none";
            });
        });
    });

    // 검색 실행 함수
    function runSearch(keyword) {
        const lowerKeyword = keyword.trim().toLowerCase();
        faqItems.forEach(item => {
            const titleEl = item.querySelector(".faq-title");
            const titleText = titleEl ? titleEl.textContent.toLowerCase() : "";
            item.style.display = titleText.includes(lowerKeyword) ? "" : "none";
        });
    }

    // ① 검색창에 '엔터' 입력 시
    if (searchInput) {
        searchInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                runSearch(searchInput.value);
            }
        });
    }

    // ② 검색 버튼 클릭 시
    if (searchBtn) {
        searchBtn.addEventListener("click", () => {
            runSearch(searchInput.value);
        });
    }

    // 아이콘 클릭 필터링 (토글)
    let activeCategory = null;
    icons.forEach(icon => {
        icon.addEventListener("click", () => {
            const category = icon.getAttribute("data-category");

            if (activeCategory === category) {
                faqItems.forEach(item => item.style.display = "");
                activeCategory = null;
            } else {
                faqItems.forEach(item => {
                    const matches = item.getAttribute("data-category") === category;
                    item.style.display = matches ? "" : "none";
                });
                activeCategory = category;
            }
        });
    });

    // FAQ 질문 클릭 → 답변 토글
    document.querySelectorAll(".faq-question").forEach(q => {
        q.addEventListener("click", () => {
            const parent = q.closest(".faq-item");
            parent.classList.toggle("active");
        });
    });

    // 모달 열기
    if (openBtn && modal) {
        openBtn.addEventListener("click", () => {
            modal.style.display = "block";
        });
    }

    // 모달 닫기
    if (modal) {
        modal.querySelectorAll(".close").forEach(btn => {
            btn.addEventListener("click", () => {
                modal.style.display = "none";
            });
        });

        window.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.style.display = "none";
            }
        });
    }

    // 중복 전송 방지
    const form = document.querySelector(".inquiry-form");
    if (form) {
        const submitBtn = form.querySelector("button[type='submit']");
        form.addEventListener("submit", () => {
            if (submitBtn.disabled) return false;
            submitBtn.disabled = true;
            submitBtn.innerText = "전송 중...";
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerText = "저장";
            }, 10000);
        });
    }

  document.querySelectorAll(".faq-header").forEach(header => {
        header.addEventListener("click", () => {
            const detail = header.nextElementSibling;
            const icon = header.querySelector(".faq-toggle-icon");
            const isOpen = detail.style.display === "block";

            detail.style.display = isOpen ? "none" : "block";
            icon.textContent = isOpen ? "▾" : "▴";
        });
    });
});