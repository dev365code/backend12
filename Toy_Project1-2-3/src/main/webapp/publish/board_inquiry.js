import { toggleFaqItemsOnClick } from "./board_common.js";

document.addEventListener("DOMContentLoaded", () => {
    toggleFaqItemsOnClick();

    const modal = document.getElementById("inquiryModal");
    const btn = document.getElementById("openModalBtn");
    const span = modal?.querySelector(".close");

    if (btn && modal) {
        btn.onclick = () => modal.style.display = "block";
    }
    if (span) {
        span.onclick = () => modal.style.display = "none";
    }
    window.onclick = (e) => {
        if (e.target === modal) modal.style.display = "none";
    };

    document.querySelectorAll(".btn-wrap button").forEach(btn => {
        if (btn.textContent.includes("이전")) {
            btn.addEventListener("click", () => {
                modal.style.display = "none";
            });
        }
    });
});