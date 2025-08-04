// 📌 전역 변수
let emailDuplicateChecked = false;
let emailVerified = false;
let loginAttempts = 0;
const MAX_LOGIN_ATTEMPTS = 3;

// 📌 이메일 형식 유효성 검사 (강화)
function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

// 📌 비밀번호 유효성 검사 (강화)
function validatePassword(password) {
    // 최소 8자, 영문+숫자+특수문자 포함
    const minLength = password.length >= 8;
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
        isValid: minLength && hasLetter && hasNumber && hasSpecial,
        minLength,
        hasLetter,
        hasNumber,
        hasSpecial
    };
}

// 📌 비밀번호와 확인란 일치 검사
function validatePasswordMatch(pw1, pw2) {
    return pw1 === pw2 && pw1.length > 0;
}

// 📌 이메일 중복 확인 (AJAX)
async function checkEmailDuplicate(email) {
    try {
        const response = await fetch('/api/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('이메일 중복 확인 오류:', error);
        return { success: false, message: '서버 오류가 발생했습니다.' };
    }
}

// 📌 이메일 인증 요청 (AJAX)
async function requestEmailVerification(email) {
    try {
        const response = await fetch('/api/send-verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('이메일 인증 요청 오류:', error);
        return { success: false, message: '서버 오류가 발생했습니다.' };
    }
}

// 📌 메시지 표시 함수
function showMessage(elementId, message, type = 'error') {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.className = `message ${type}`;
        element.style.display = message ? 'block' : 'none';
    }
}

// 📌 폼 유효성 검사 통합
function validateForm() {
    const email = document.getElementById("email").value.trim();
    const pw1 = document.getElementById("pw1").value;
    const pw2 = document.getElementById("pw2").value;
    const name = document.querySelector("input[name='name']").value.trim();
    const phone = document.querySelector("input[name='phone']").value.trim();

    // 필수 입력 검사
    if (!email) {
        showMessage('emailError', '이메일을 입력해주세요.');
        document.getElementById("email").focus();
        return false;
    }

    if (!validateEmail(email)) {
        showMessage('emailError', '올바른 이메일 형식을 입력해주세요.');
        document.getElementById("email").focus();
        return false;
    }

    if (!emailDuplicateChecked) {
        showMessage('emailError', '이메일 중복 확인을 해주세요.');
        return false;
    }

    if (!emailVerified) {
        showMessage('emailError', '이메일 인증을 완료해주세요.');
        return false;
    }

    if (!pw1) {
        showMessage('pwError', '비밀번호를 입력해주세요.');
        document.getElementById("pw1").focus();
        return false;
    }

    const pwValidation = validatePassword(pw1);
    if (!pwValidation.isValid) {
        let errorMsg = '비밀번호는 ';
        if (!pwValidation.minLength) errorMsg += '8자 이상, ';
        if (!pwValidation.hasLetter) errorMsg += '영문 포함, ';
        if (!pwValidation.hasNumber) errorMsg += '숫자 포함, ';
        if (!pwValidation.hasSpecial) errorMsg += '특수문자 포함 ';
        errorMsg += '해야 합니다.';

        showMessage('pwError', errorMsg);
        document.getElementById("pw1").focus();
        return false;
    }

    if (!validatePasswordMatch(pw1, pw2)) {
        showMessage('pwError', '비밀번호가 일치하지 않습니다.');
        document.getElementById("pw2").focus();
        return false;
    }

    if (!name) {
        alert('이름을 입력해주세요.');
        document.querySelector("input[name='name']").focus();
        return false;
    }

    if (!phone) {
        alert('휴대전화 번호를 입력해주세요.');
        document.querySelector("input[name='phone']").focus();
        return false;
    }

    // 필수 약관 동의 확인
    const requiredAgreements = document.querySelectorAll('.agreements input[type="checkbox"]');
    const requiredChecked = Array.from(requiredAgreements).slice(1, 4); // 첫 번째(전체동의) 제외, 필수 3개

    if (!requiredChecked.every(chk => chk.checked)) {
        alert('필수 약관에 모두 동의해주세요.');
        return false;
    }
    return true;
}

// 📌 생년월일 select 동적 생성
function populateBirthSelects() {
    const yearSelect = document.getElementById("birthYear");
    const monthSelect = document.getElementById("birthMonth");
    const daySelect = document.getElementById("birthDay");

    if (!yearSelect || !monthSelect || !daySelect) return;

    const thisYear = new Date().getFullYear();

    // 년도 (현재년도부터 1940년까지)
    for (let y = thisYear; y >= 1940; y--) {
        yearSelect.innerHTML += `<option value="${y}">${y}년</option>`;
    }
    // 월 (1월부터 12월까지)
    for (let m = 1; m <= 12; m++) {
        monthSelect.innerHTML += `<option value="${m}">${m}월</option>`;
    }
    // 일 (1일부터 31일까지)
    for (let d = 1; d <= 31; d++) {
        daySelect.innerHTML += `<option value="${d}">${d}일</option>`;
    }
    // 월 변경 시 일수 조정
    monthSelect.addEventListener('change', updateDays);
    yearSelect.addEventListener('change', updateDays);
}

// 📌 월별 일수 조정
function updateDays() {
    const yearSelect = document.getElementById("birthYear");
    const monthSelect = document.getElementById("birthMonth");
    const daySelect = document.getElementById("birthDay");

    const year = parseInt(yearSelect.value);
    const month = parseInt(monthSelect.value);

    if (year && month) {
        const daysInMonth = new Date(year, month, 0).getDate();
        const currentDay = daySelect.value;

        // 일 옵션 재생성
        daySelect.innerHTML = '<option value="">일</option>';
        for (let d = 1; d <= daysInMonth; d++) {
            const selected = d == currentDay ? 'selected' : '';
            daySelect.innerHTML += `<option value="${d}" ${selected}>${d}일</option>`;
        }
    }
}

// 📌 전체 동의 체크박스 연동
function setupAgreementCheck() {
    const agreeAll = document.querySelector("input[name='agreeAll']");
    const subChecks = document.querySelectorAll(".agreements input[type='checkbox']:not([name='agreeAll'])");

    if (!agreeAll) return;

    // 전체동의 체크 시 → 하위 전체 선택/해제
    agreeAll.addEventListener("change", function () {
        subChecks.forEach(chk => {
            chk.checked = agreeAll.checked;
        });
    });

    // 하위 체크박스 변경 시 → 전체동의 상태 갱신
    subChecks.forEach(chk => {
        chk.addEventListener("change", function () {
            const allChecked = Array.from(subChecks).every(c => c.checked);
            agreeAll.checked = allChecked;
        });
    });
}

// 📌 약관 토글 기능
function toggleTerms(contentId) {
    const content = document.getElementById(contentId);
    const button = event.target;

    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        button.textContent = '접기 ▲';
    } else {
        content.style.display = 'none';
        button.textContent = '전체보기 ▼';
    }
}

// 📌 우편번호 API 연동
function execDaumPostcode() {
    new daum.Postcode({
        oncomplete: function (data) {
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

// 📌 계정 잠금 확인
function checkAccountLock() {
    const lockTime = localStorage.getItem('accountLockTime');
    if (lockTime) {
        const now = new Date().getTime();
        const lockDuration = 30 * 60 * 1000; // 30분

        if (now - parseInt(lockTime) < lockDuration) {
            const remainingTime = Math.ceil((lockDuration - (now - parseInt(lockTime))) / 60000);
            return { locked: true, remainingTime };
        } else {
            localStorage.removeItem('accountLockTime');
            localStorage.removeItem('loginAttempts');
        }
    }
    return { locked: false };
}

// 📌 로그인 시도 기록
function recordLoginAttempt() {
    loginAttempts = parseInt(localStorage.getItem('loginAttempts') || '0') + 1;
    localStorage.setItem('loginAttempts', loginAttempts.toString());

    if (loginAttempts >= MAX_LOGIN_ATTEMPTS) {
        localStorage.setItem('accountLockTime', new Date().getTime().toString());
        alert(`로그인 ${MAX_LOGIN_ATTEMPTS}회 실패로 계정이 30분간 잠겼습니다.`);
        return true;
    }
    return false;
}

// 📌 DOM 로드 완료 시 실행
document.addEventListener("DOMContentLoaded", function () {

    // 이메일 실시간 유효성 검사
    const emailInput = document.getElementById("email");
    if (emailInput) {
        emailInput.addEventListener("input", function () {
            const email = this.value.trim();
            emailDuplicateChecked = false; // 이메일 변경 시 중복확인 초기화
            emailVerified = false; // 이메일 변경 시 인증 초기화

            if (email === '') {
                showMessage('emailError', '');
                return;
            }

            if (!validateEmail(email)) {
                showMessage('emailError', '올바른 이메일 형식을 입력해주세요.');
            } else {
                showMessage('emailError', '');
            }
        });
    }

    // 비밀번호 실시간 유효성 검사
    const pw1Input = document.getElementById("pw1");
    const pw2Input = document.getElementById("pw2");

    if (pw1Input) {
        pw1Input.addEventListener("input", function () {
            const password = this.value;
            if (password === '') {
                showMessage('pwError', '');
                return;
            }

            const validation = validatePassword(password);
            if (!validation.isValid) {
                let errorMsg = '비밀번호는 ';
                if (!validation.minLength) errorMsg += '8자 이상, ';
                if (!validation.hasLetter) errorMsg += '영문 포함, ';
                if (!validation.hasNumber) errorMsg += '숫자 포함, ';
                if (!validation.hasSpecial) errorMsg += '특수문자 포함 ';
                errorMsg += '해야 합니다.';
                showMessage('pwError', errorMsg);
            } else {
                showMessage('pwError', '');
            }

            // 비밀번호 확인란과 비교
            if (pw2Input.value) {
                checkPasswordMatch();
            }
        });
    }

    if (pw2Input) {
        pw2Input.addEventListener("input", checkPasswordMatch);
    }

    function checkPasswordMatch() {
        const pw1 = document.getElementById("pw1").value;
        const pw2 = document.getElementById("pw2").value;

        if (pw2 === '') {
            showMessage('pwError', '');
            return;
        }

        if (!validatePasswordMatch(pw1, pw2)) {
            showMessage('pwError', '비밀번호가 일치하지 않습니다.');
        } else {
            showMessage('pwError', '비밀번호가 일치합니다.', 'success');
        }
    }

    // 이메일 중복 확인 버튼
    const emailCheckBtn = document.getElementById("btn-email-check");
    if (emailCheckBtn) {
        emailCheckBtn.addEventListener("click", async function() {
            const email = document.getElementById("email").value.trim();

            if (!email) {
                showMessage('emailError', '이메일을 입력해주세요.');
                return;
            }

            if (!validateEmail(email)) {
                showMessage('emailError', '올바른 이메일 형식을 입력해주세요.');
                return;
            }

            this.disabled = true;
            this.textContent = '확인 중...';

            try {
                const result = await checkEmailDuplicate(email);

                if (result.success) {
                    if (result.isDuplicate) {
                        showMessage('emailError', '이미 사용 중인 이메일입니다.');
                        emailDuplicateChecked = false;
                    } else {
                        showMessage('emailError', '사용 가능한 이메일입니다.', 'success');
                        emailDuplicateChecked = true;
                    }
                } else {
                    showMessage('emailError', result.message || '중복 확인 중 오류가 발생했습니다.');
                }
            } catch (error) {
                showMessage('emailError', '서버 오류가 발생했습니다.');
            } finally {
                this.disabled = false;
                this.textContent = '중복 확인';
            }
        });
    }

    // 이메일 인증 요청 버튼
    const emailVerifyBtn = document.getElementById("btn-email-verify");
    if (emailVerifyBtn) {
        emailVerifyBtn.addEventListener("click", async function() {
            const email = document.getElementById("email").value.trim();

            if (!emailDuplicateChecked) {
                showMessage('emailError', '먼저 이메일 중복 확인을 해주세요.');
                return;
            }

            this.disabled = true;
            this.textContent = '발송 중...';

            try {
                const result = await requestEmailVerification(email);

                if (result.success) {
                    alert('인증 메일이 발송되었습니다. 이메일을 확인해주세요.');
                    // 실제로는 사용자가 이메일에서 인증 링크를 클릭하면 emailVerified = true로 설정
                    // 여기서는 데모용으로 3초 후 자동 인증 처리
                    emailVerified = true;
                    showMessage('emailError', '이메일 인증이 완료되었습니다.', 'success');
                } else {
                    alert(result.message || '인증 메일 발송 중 오류가 발생했습니다.');
                }
            } catch (error) {
                alert('서버 오류가 발생했습니다.');
            } finally {
                this.disabled = false;
                this.textContent = '인증 요청';
            }
        });
    }

    // 초기 설정
    populateBirthSelects();
    setupAgreementCheck();

    // 폼 제출 처리
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault(); // 기본 제출 방지

            if (validateForm()) {
                // 여기서 실제 회원가입 처리
                alert('회원가입이 완료되었습니다!');
                this.submit(); // 실제 제출
            }
        });
    }
});

// 📌 전역 함수로 노출 (JSP에서 onclick으로 호출하는 함수들)
window.toggleTerms = toggleTerms;
window.execDaumPostcode = execDaumPostcode;