<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>공지사항</title>
    <link rel="stylesheet" href="${pageContext.request.contextPath}/publish/board_common.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
</head>

<%@ include file="header.jsp" %>

<body>
<div class="layout full-centered">
    <aside class="sidebar">
        <h2>고객센터</h2>
        <ul>
            <li><span class="active">공지사항</span></li>
            <li><a href="${pageContext.request.contextPath}/board/faq">FAQ</a></li>
            <li><a href="${pageContext.request.contextPath}/board/inquiry">1:1문의</a></li>
        </ul>
    </aside>

    <main class="content">
        <h1 class="page-title">공지사항</h1>
        <table class="notice-table">
            <thead>
            <tr>
                <th>번호</th>
                <th>제목</th>
                <th>날짜</th>
                <th>작성자</th>
            </tr>
            </thead>
            <tbody>
            <c:forEach var="notice" items="${notices}">
                <tr>
                    <td>
                        <c:choose>
                            <c:when test="${notice.isTop}">
                                <span class="badge">공지</span>
                            </c:when>
                            <c:otherwise>
                                ${notice.noticeId}
                            </c:otherwise>
                        </c:choose>
                    </td>
                    <td>
                        <a href="#" class="notice-title"
                           data-title="${notice.noticeTitle}"
                           data-content="${notice.noticeContent}"
                           data-created="${notice.createdAt}"
                           data-admin="${notice.adminId}"
                           data-img="${notice.img}">
                                ${notice.noticeTitle}
                        </a>
                    </td>
                    <td>${notice.createdAt}</td>
                    <td>${notice.adminId}</td>
                </tr>
            </c:forEach>
            </tbody>
        </table>

        <div class="pagination">
            <c:if test="${currentPage > 1}">
                <a href="?page=${currentPage - 1}" class="page-btn prev">«</a>
            </c:if>

            <c:forEach begin="1" end="${totalPages}" var="i">
                <a href="?page=${i}" class="page-btn ${i == currentPage ? 'active' : ''}">${i}</a>
            </c:forEach>

            <c:if test="${currentPage < totalPages}">
                <a href="?page=${currentPage + 1}" class="page-btn next">»</a>
            </c:if>
        </div>
    </main>
</div>

<div id="noticeModal" class="modal">
    <div class="modal-content" style="
    width: 90%;
    max-width: 1000px;
    padding: 30px 60px 30px 160px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    position: relative;
">
        <span class="close" style="font-size: 28px; position: absolute; top: 20px; right: 30px; cursor: pointer;">&times;</span>

        <h2 id="modalTitle"
            style="margin-bottom: 20px; font-size: 24px; border-bottom: 2px solid #444; padding-bottom: 10px;"></h2>

        <div id="modalContent"
             style="white-space: pre-line; line-height: 1.7; font-size: 15px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 20px;">
        </div>

        <div id="modalImageContainer" style="margin-top: 30px; text-align: center;">
            <img id="modalImage" src="" alt="공지 이미지" style="max-width: 100%; height: auto; display: none;"/>
        </div>

        <div style="margin-top: 20px; font-size: 13px; color: #666; display: flex; justify-content: flex-end; gap: 16px;">
            <span id="modalCreated"></span>
            <span id="modalAdmin"></span>
        </div>
    </div>
</div>


<script src="https://kit.fontawesome.com/f350009f47.js" crossorigin="anonymous"></script>

</body>

<%@ include file="footer.jsp" %>
</html>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        const modal = document.getElementById("noticeModal");
        const modalTitle = document.getElementById("modalTitle");
        const modalContent = document.getElementById("modalContent");
        const modalImage = document.getElementById("modalImage");

        const modalCreated = document.getElementById("modalCreated");
        const modalAdmin = document.getElementById("modalAdmin");
        const closeBtn = modal.querySelector(".close");

        document.querySelectorAll(".notice-title").forEach(link => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                modalTitle.textContent = link.dataset.title;
                modalContent.textContent = link.dataset.content;
                modalCreated.textContent = link.dataset.created;
                modalAdmin.textContent = link.dataset.admin;
                const imageUrl = link.dataset.img;

                console.log(imageUrl);

                if (imageUrl) {
                    modalImage.src = imageUrl;
                    modalImage.style.display = "block";
                } else {
                    modalImage.style.display = "none";
                }
                modal.style.display = "block";
            });
        });

        closeBtn.addEventListener("click", () => modal.style.display = "none");
        window.addEventListener("click", (e) => {
            if (e.target === modal) modal.style.display = "none";
        });
    });
</script>