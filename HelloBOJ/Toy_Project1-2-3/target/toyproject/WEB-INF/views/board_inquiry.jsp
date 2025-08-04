<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>

<!-- ⭐ -->
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
            <li><strong><a href="${pageContext.request.contextPath}/board/notice">공지사항</a></strong></li>
            <li><a href="${pageContext.request.contextPath}/board/faq">FAQ</a></li>
            <li><span class="active">1:1문의</span></li>
        </ul>
    </aside>

    <main class="content">
        <div class="title-with-button">
            <h1 class="page-title">1:1 문의 내역</h1>
            <button id="openModalBtn" class="inquiry-btn">문의하기</button>
        </div>

        <div id="inquirySection" class="faq-list">
            <c:forEach var="q" items="${questions}">
                <div class="faq-item">
                    <!-- ✅ 헤더: 제목 행만 처음 표시 -->
                    <div class="faq-header"
                         style="display: flex; justify-content: space-between; align-items: center; cursor: pointer;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span class="faq-label" style="font-weight: bold;">Q</span>
                            <div class="faq-title" style="font-weight: 500;">${q.generalBoardTitle}</div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="faq-date" style="font-size: 13px; color: #666;">${q.createdAt}</span>
                            <span class="faq-toggle-icon">▾</span>
                        </div>
                    </div>

                    <!-- ✅ 디테일: 클릭 시 열릴 상세 질문/답변 영역 -->
                    <div class="faq-detail" style="display: none; margin-top: 10px;">
                        <!-- 질문 내용 -->
                        <div class="faq-content" style="font-size: 13px; color: #555; margin-left: 24px;">
                                ${q.generalBoardContent}
                            <c:if test="${not empty q.img}">
                                <div style="margin-top: 12px; text-align: center;">
                                    <img src="${q.img}" alt="문의 이미지"
                                         style="max-width: 60%; max-height: 150px; height: auto; border-radius: 6px; object-fit: contain;"/>
                                </div>
                            </c:if>
                        </div>

                        <!-- 답변 내용 -->
                        <div class="faq-answer" style="margin-top: 12px; display: flex;">
                            <span class="faq-label">A</span>
                            <div class="faq-content" style="margin-left: 8px;">
                                <c:choose>
                                    <c:when test="${q.replyContent == null || q.replyContent eq ''}">
                                        <span style="font-style: italic; font-weight: bold;">관리자의 답변을 기다리는 중입니다.</span>
                                    </c:when>
                                    <c:otherwise>
                                        ${q.replyContent}
                                    </c:otherwise>
                                </c:choose>
                            </div>
                        </div>
                    </div>
                </div>
            </c:forEach>
        </div>

        <div class="pagination">
            <c:if test="${page > 1}">
                <a class="page-btn prev" href="?page=${page - 1}">«</a>
            </c:if>
            <c:forEach begin="1" end="${totalPages}" var="i">
                <a class="page-btn ${i == page ? 'active' : ''}" href="?page=${i}">${i}</a>
            </c:forEach>
            <c:if test="${page < totalPages}">
                <a class="page-btn next" href="?page=${page + 1}">»</a>
            </c:if>
        </div>
    </main>
</div>

<!-- 문의 작성 모달 -->
<div id="inquiryModal" class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <h2>1:1 문의 작성</h2>
        <form class="inquiry-form" method="post" action="${pageContext.request.contextPath}/board/inquiry/write">
            <label>말머리</label>
            <select name="contentType" required>
                <option value="회원/정보관리">회원/정보관리</option>
                <option value="주문/결제">주문/결제</option>
                <option value="배송">배송</option>
                <option value="반품/환불/교환/AS">반품/환불/교환/AS</option>
                <option value="영수증/증빙서류">영수증/증빙서류</option>
                <option value="상품/이벤트">상품/이벤트</option>
                <option value="기타">기타</option>
            </select>


            <label>제목</label>
            <input type="text" name="generalBoardTitle" placeholder="제목을 입력하세요"/>

            <label>본문</label>
            <textarea name="generalBoardContent" placeholder="해당글은 비밀글로만 작성이 됩니다."></textarea>

            <div class="btn-wrap">
                <button type="button" class="close">이전</button>
                <button type="submit" class="primary">저장</button>
            </div>
        </form>
    </div>
</div>

<script src="https://kit.fontawesome.com/f350009f47.js" crossorigin="anonymous"></script>
<script src="${pageContext.request.contextPath}/publish/board_common.js"></script>
</body>
<%@ include file="footer.jsp" %>
</html>