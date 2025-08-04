<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<%@ include file="/WEB-INF/views/header.jsp" %>
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>축구는 종교다</title>
  <link rel="stylesheet" href="<c:url value='/publish/new.css'/>">

</head>
<body>
<main>
  <!-- 제목과 정렬 컨트롤을 같은 라인에 배치 -->
  <div style="position: relative; margin: 20px 0; height: 2.5em;">
    <!-- 제목은 화면 중앙 -->
    <h2 class="section-title"
        style="position: absolute; left: 50%; top: 0;
               transform: translateX(-50%); margin: 0;">
      ${pageTitle}
    </h2>

    <!-- 정렬 폼은 오른쪽 상단 -->
    <!-- ▼ action="/new" 속성을 제거했습니다 -->
    <form id="sortForm" method="get"
          action="${pageTitle == 'Womens' ? '/womens' : '/youth'}"
          style="position: absolute; right: 0; top: 0;
                 display: flex; align-items: center; gap: 8px; margin: 0;">
      <label for="sort">정렬:</label>
      <select id="sort" name="sort"
              onchange="document.getElementById('sortForm').submit()">
        <option value="recommend"
        ${param.sort=='recommend'?'selected':''}>추천순</option>
        <option value="priceDesc"
        ${param.sort=='priceDesc'?'selected':''}>가격 높은순</option>
        <option value="priceAsc"
        ${param.sort=='priceAsc'?'selected':''}>가격 낮은순</option>
        <option value="newest"
        ${param.sort=='newest'?'selected':''}>등록일순</option>
        <option value="review"
        ${param.sort=='review'?'selected':''}>상품평순</option>
      </select>
      <!-- 페이징 파라미터 유지 -->
      <input type="hidden" name="page" value="${page}" />
      <input type="hidden" name="size" value="${size}" />
    </form>
  </div>

  <!-- 상품 그리드 -->
  <div class="product-grid">
    <c:forEach var="p" items="${productList}">
      <div class="product-card">
        <a href="${pageContext.request.contextPath}/product/detail?productID=${p.productId}"><img src="${p.img}" alt="${p.productName}" /></a>
        <div class="product-info">
          <h3 class="brand">${p.brandName}</h3>
          <a href="${pageContext.request.contextPath}/product/detail?productID=${p.productId}"style="text-decoration: none; color: inherit;"><p class="product-name">${p.productName}</p></a>
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
      </div>
    </c:forEach>

    <!-- 상품이 없을 때 -->
    <c:if test="${empty productList}">
      <p style="grid-column:1/-1; text-align:center;">
        상품이 없습니다.
      </p>
    </c:if>
  </div>

  <!-- 페이지네이션 -->
  <nav class="pagination" style="text-align:center; margin:20px 0;">
    <c:if test="${page > 1}">
      <a href="?page=${page-1}&size=${size}&sort=${sort}">‹ Prev</a>
    </c:if>

    <c:forEach var="i" begin="1" end="${totalPages}">
      <c:choose>
        <c:when test="${i == page}">
          <span style="font-weight:bold; margin:0 5px;">${i}</span>
        </c:when>
        <c:otherwise>
          <a href="?page=${i}&size=${size}&sort=${sort}"
             style="margin:0 5px;">${i}</a>
        </c:otherwise>
      </c:choose>
    </c:forEach>

    <c:if test="${page < totalPages}">
      <a href="?page=${page+1}&size=${size}&sort=${sort}">Next ›</a>
    </c:if>
  </nav>
</main>
</body>
</html>
<%@ include file="footer.jsp" %>