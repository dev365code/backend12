<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>
<%@ include file="header.jsp" %>
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>축구는 종교다</title>
  <style>
    .filter-sort-section {
      display: flex;
      padding: 40px 60px;
      gap: 40px;
    }

    .filter-menu {
      width: 200px;
      flex-shrink: 0;
    }

    .filter-menu h4 {
      font-size: 16px;
      margin-bottom: 10px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 5px;
    }

    .filter-category {
      margin-bottom: 20px;
    }

    .filter-category summary {
      font-weight: bold;
      cursor: pointer;
    }

    .sort-bar {
      margin-left: auto;
    }

    .sort-bar select {
      padding: 6px 12px;
      font-size: 14px;
    }

    .filter-tags {
      display: flex;
      gap: 10px;
      margin: 20px 60px 10px;
      justify-content: center;
    }

    .filter-tag a {
      display: block;
      background-color: #f3f3f3;
      border: 1px solid #ccc;
      border-radius: 4px;
      padding: 6px 12px;
      font-size: 14px;
      text-decoration: none;
      color: black;
    }

    .product-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 40px;
      padding: 40px 60px;
    }

    .product-card {
      text-align: center;
    }

    .product-card img {
      width: 100%;
      max-width: 300px;
    }
  </style>
  <link rel="stylesheet" href="<c:url value='/publish/new.css'/>">
</head>
<body>
<main>
  <div class="banner">

    <img src="<c:url value='/image/clothesBanner.png'/>" style="width:100%; object-fit:cover;"alt="의류 배너">
  </div>
  <div class="filter-tags">
    <div class="filter-tag"><a href="#">상의</a></div>
    <div class="filter-tag"><a href="#">하의</a></div>
  </div>

  <section class="filter-sort-section">
    <aside class="filter-menu">
      <h4>필터</h4>
      <div class="filter-category">
        <details open><summary>브랜드</summary></details>
        <details><summary>가격</summary></details>
        <details><summary>연령</summary></details>
        <details><summary>색상</summary></details>
        <button style="margin-top:10px">필터 초기화</button>
        <button style="margin-top:10px">검색</button>
      </div>
    </aside>

    <div class="sort-bar">
      <label for="sort">정렬:</label>
      <form id="sortForm" method="get" action="/clothes" style="display:inline-block; margin:0;">
        <input type="hidden" name="page" value="${page}" />
        <input type="hidden" name="size" value="${size}" />
        <select id="sort" name="sort" onchange="document.getElementById('sortForm').submit()">
          <option value="recommend" ${param.sort=='recommend'?'selected':''}>추천순</option>
          <option value="priceDesc" ${param.sort=='priceDesc'?'selected':''}>가격 높은순</option>
          <option value="priceAsc"  ${param.sort=='priceAsc'?'selected':''}>가격 낮은순</option>
          <option value="newest"    ${param.sort=='newest'?'selected':''}>등록일순</option>
          <option value="review"    ${param.sort=='review'?'selected':''}>상품평순</option>
        </select>
      </form>
    </div>
  </section>

  <section class="product-grid">
    <c:forEach var="p" items="${productList}">
      <div class="product-card">
        <a href="${pageContext.request.contextPath}/product/detail?productID=${p.productId}"><img src="${p.img}" alt="${p.productName}"></a>
        <p><c:out value="${p.brandName}" /></p>
        <a href="${pageContext.request.contextPath}/product/detail?productID=${p.productId}"style="text-decoration: none; color: #888;"><p><c:out value="${p.productName}" /></p></a>
        <p class="price"><fmt:formatNumber value="${p.price}" type="number" groupingUsed="true"/>원</p>
        <c:if test="${not empty p.size}">
          <p class="sizes"style="font-size: 12px; color: #999;">${p.size}</p>
        </c:if>
      </div>
    </c:forEach>

    <c:if test="${empty productList}">
      <p style="grid-column:1/-1; text-align:center;">의류 상품이 없습니다.</p>
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
      <a href="?page=${page+1}&size=${size}&sort=${sort}">Next ›</a>
    </c:if>
  </nav>
</main>
</body>
</html>
<%@ include file="footer.jsp" %>