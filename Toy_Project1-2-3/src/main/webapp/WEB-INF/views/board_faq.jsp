<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>축구는 종교다</title>

    <link rel="stylesheet" href="${pageContext.request.contextPath}/publish/board_common.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
</head>

<%@ include file="header.jsp" %>

<body>
<div class="layout full-centered">
    <aside class="sidebar">
        <h2>고객센터</h2>
        <ul>
            <li><a href="${pageContext.request.contextPath}/board/notice">공지사항</a></li>
            <li><span class="active">FAQ</span></li>
            <li><a href="${pageContext.request.contextPath}/board/inquiry">1:1문의</a></li>
        </ul>
    </aside>

    <main class="content">
        <h1 class="page-title">자주 묻는 질문</h1>

        <div class="faq-icons">
            <div class="faq-icon" data-category="회원가입/정보">
                <i class="fa-solid fa-user fa-4x"></i>
                <span>회원가입/정보</span>
            </div>
            <div class="faq-icon" data-category="결제/배송">
                <i class="fa-solid fa-box fa-4x"></i>
                <span>결제/배송</span>
            </div>
            <div class="faq-icon" data-category="A/S 및 심의">
                <i class="fa-solid fa-wrench fa-4x"></i>
                <span>A/S 및 심의</span>
            </div>
            <div class="faq-icon" data-category="교환/반품/환불">
                <i class="fa-solid fa-rotate-left fa-4x"></i>
                <span>교환/반품/환불</span>
            </div>
            <div class="faq-icon" data-category="마일리지 적립">
                <i class="fa-solid fa-coins fa-4x"></i>
                <span>마일리지 적립</span>
            </div>
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="검색어를 입력하세요"/>
    <button id="searchBtn">🔍</button>
        </div>

        <div id="faqSection" class="faq-list">
            <c:forEach var="faq" items="${faqList}">
                <div class="faq-item" data-category="${faq.faqCategory}">
                    <div class="faq-question">
                        <span class="faq-label">Q</span>
                        <span class="faq-title">[${faq.faqCategory}] ${faq.faqTitle}</span>
                        <span class="faq-toggle-icon">▾</span>
                    </div>
                    <div class="faq-answer">
                        <span class="faq-label">A</span>
                        <div class="faq-content">${faq.faqContent}</div>
                    </div>
                </div>
            </c:forEach>
        </div>
    </main>
</div>
<script src="https://kit.fontawesome.com/f350009f47.js" crossorigin="anonymous"></script>
<script src="${pageContext.request.contextPath}/publish/board_common.js"></script>
</body>
<%@ include file="footer.jsp" %>
</html>