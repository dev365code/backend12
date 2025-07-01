<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<%@ include file="header.jsp" %>
<link rel="stylesheet" href="<c:url value='/publish/football_shoes.css'/>">
<link rel="stylesheet" href="<c:url value='/publish/new.css'/>">

<main>
    <div class="banner">
        <img src=https://caposttr4591.cdn-nhncommerce.com/data/editor/goods/250623/20250623_Fear-Nothing_132556.jpg style="width:100%; object-fit: cover;"alt="용품 배너">
    </div>
<div class="filter-tags">
        <div class="filter-tag"><a href="/brand.html">브랜드</a></div>
        <div class="filter-tag"><a href="/silo.html">사일로</a></div>
        <div class="filter-tag"><a href="/ground.html">그라운드</a></div>
    </div>

    <section class="filter-sort-section">
        <aside class="filter-menu">
            <h4>필터</h4>
            <div class="filter-category">
                <details open><summary>브랜드</summary></details>
                <details><summary>가격</summary></details>
                <details><summary>용도</summary></details>
                <details><summary>연령</summary></details>
                <details><summary>색상</summary></details>
                <details><summary>사일로</summary></details>
                <button style="margin-top:10px">필터 초기화</button>
                <button style="margin-top:10px">검색</button>
            </div>
        </aside>

        <div class="sort-bar">
            <label for="sort">정렬:</label>
            <form id="sortForm" method="get" action="/football_shoes" style="display:inline-block; margin:0;">
                <select id="sort" name="sort" onchange="document.getElementById('sortForm').submit()">
                    <option value="recommend" ${param.sort=='recommend'?'selected':''}>추천순</option>
                    <option value="priceDesc" ${param.sort=='priceDesc'?'selected':''}>가격 높은순</option>
                    <option value="priceAsc"  ${param.sort=='priceAsc'?'selected':''}>가격 낮은순</option>
                    <option value="newest"    ${param.sort=='newest'?'selected':''}>등록일순</option>
                    <option value="review"    ${param.sort=='review'?'selected':''}>상품평순</option>
                </select>
                <input type="hidden" name="page" value="${page}" />
                <input type="hidden" name="size" value="${size}" />
            </form>
        </div>
    </section>

    <section class="product-grid">
       <c:if test="${not empty productList}">
           <c:forEach var="p" items="${productList}">
               <div class="product-card">
                   <a href="${pageContext.request.contextPath}/product/detail?productID=${p.productId}"><img src="${p.img}" alt="${p.productName}"></a>
                   <p>${p.brandName}</p>
                   <a href="${pageContext.request.contextPath}/product/detail?productID=${p.productId}"style="text-decoration: none; color: #888;"><p>${p.productName}</p></a>
                   <p class="price"><fmt:formatNumber value="${p.price}" type="number" groupingUsed="true"/>원</p>
                   <c:if test="${not empty p.size}">
                       <p class="sizes"style="font-size: 12px; color: #999;">
                           <c:choose>
                               <c:when test="${p.size == '0'}">
                                   Free
                               </c:when>
                               <c:otherwise>
                                   ${p.size}
                               </c:otherwise>
                           </c:choose>
                       </p>
                   </c:if>
               </div>
           </c:forEach>
       </c:if>
        <c:if test="${empty productList}">
            <p>해당 카테고리의 상품이 없습니다.</p>
        </c:if>
    </section>

    <nav class="pagination" style="text-align:center; margin:20px 0;">
        <!-- 이전 페이지 링크 -->
        <c:if test="${page > 1}">
            <a href="?page=${page-1}&size=${size}&sort=${sort}">‹ Prev</a>
        </c:if>

        <!-- 페이지 번호 -->
        <c:forEach var="i" begin="1" end="${totalPages}">
            <c:choose>
                <c:when test="${i == page}">
                    <span style="font-weight:bold; margin:0 5px;">${i}</span>
                </c:when>
                <c:otherwise>
                    <a href="?page=${i}&size=${size}&sort=${sort}" style="margin:0 5px;">${i}</a>
                </c:otherwise>
            </c:choose>
        </c:forEach>
        <!-- 다음 페이지 링크 -->
        <c:if test="${page < totalPages}">
            <a href="?page=${page+1}&size=${size}">Next ›</a>
        </c:if>
    </nav>
</main>

<%@ include file="footer.jsp" %>