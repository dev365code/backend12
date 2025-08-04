document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const emailInput = document.getElementById("email");
    const pwInput = document.getElementById("password");
    const rememberCheckbox = document.querySelector("input[name='remember']"); // 추가

    // 페이지 로드 시 저장된 아이디 불러오기 (추가)
    const savedEmail = getCookie("savedEmail");
    if (savedEmail) {
        emailInput.value = savedEmail;
        rememberCheckbox.checked = true;
    }

    loginForm.addEventListener("submit", function (e) {
        const email = emailInput.value.trim();
        const password = pwInput.value.trim();

        // 1. 이메일 입력 확인
        if (email === "") {
            alert("이메일을 입력하세요.");
            emailInput.focus();
            e.preventDefault();  // submit 중단
            return;
        }

        // 2. 이메일 형식 확인
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert("올바른 이메일 형식을 입력하세요.");
            emailInput.focus();
            e.preventDefault();
            return;
        }

        // 3. 비밀번호 입력 확인
        if (password === "") {
            alert("비밀번호를 입력하세요.");
            pwInput.focus();
            e.preventDefault();
            return;
        }

        // 4. 아이디 저장 처리 (추가)
        if (rememberCheckbox.checked) {
            setCookie("savedEmail", email, 30); // 30일간 저장
        } else {
            deleteCookie("savedEmail"); // 체크 해제시 삭제
        }
    });
});

// 쿠키 관련 함수들 (추가)
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + '=' + value + ';expires=' + expires.toUTCString() + ';path=/';
}

function getCookie(name) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}