import { toggleFaqItemsOnClick } from "./board_common.js";

document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".tab");
    const icons = document.querySelectorAll(".faq-icon");
    const faqItems = document.querySelectorAll(".faq-item");
    const searchInput = document.getElementById("searchInput");

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

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            const keyword = searchInput.value.toLowerCase();
            faqItems.forEach(item => {
                const text = item.innerText.toLowerCase();
                item.style.display = text.includes(keyword) ? "" : "none";
            });
        });
    }

    icons.forEach(icon => {
        icon.addEventListener("click", () => {
            const category = icon.getAttribute("data-category");
            faqItems.forEach(item => {
                const matches = item.getAttribute("data-category") === category;
                item.style.display = matches ? "" : "none";
            });
        });
    });
    toggleFaqItemsOnClick();
});