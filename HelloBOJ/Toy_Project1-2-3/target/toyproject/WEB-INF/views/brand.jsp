<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ include file="header.jsp" %>
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>축구는 종교다</title>
<%--  <link rel="stylesheet" href="/publish/new.css">--%>
  <style>
    .brand-landing-wrap {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      /*min-height: 420px;*/
      padding: 60px 0 20px;
      background: url('https://via.placeholder.com/1600x500?text=Background+Pattern') center/cover no-repeat;
      margin-bottom: 1px;
      width: 100%;
    }
    .brand-landing-title {
      font-size: 48px;
      font-weight: 400;
      letter-spacing: 2px;
      margin-bottom: 1px;
      text-align: center;
      margin-top: 60px;

    }
    .brand-landing-title strong {
      font-weight: 900;
      letter-spacing: 1px;
    }
    .brand-landing-desc {
      font-size: 22px;
      color: #222;
      text-align: center;
      margin-bottom: 30px;
      line-height: 1.6;
      max-width: 900px;
      word-break: keep-all;
    }
    .brand-logos {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 0;
      /*margin: 0 auto;*/
      padding: 0;
      width: 90vw;
      max-width: 1400px;
      background: #fff;
      margin-top: 1px;
      margin-bottom: 20px;
      margin-left: auto;
      margin-right: auto;
    }
    .brand-logo-item {
      flex: 1 1 0px;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 60px 0;
      border-right: 1px solid #eee;
      background: #fff;
    }
    .brand-logo-item:last-child {
      border-right: none;
    }
    .brand-logo-item img {
      width: 180px;
      height: auto;
      max-height: 60px;
      object-fit: contain;
      filter: grayscale(100%);
    }
    @media (max-width: 900px) {
      .brand-landing-title { font-size: 28px; }
      .brand-landing-desc { font-size: 15px; }
      .brand-logo-item img { width: 100px; }
      .brand-logos { flex-wrap: wrap; }
      .brand-logo-item { padding: 28px 0; }
    }
  </style>
</head>
<body>
<main>
  <section class="brand-landing-wrap">
    <div class="brand-landing-title">Soccer is <strong>RELIGION</strong></div>
    <div class="brand-landing-desc">
      축구는 종교다. 축구는 삶의 일부이다.<br>
      식사를 하며 축구를 보고, 주말에는 직접 축구를 하고, 경기 날엔 스타디움에 가서 축구를 관람한다.
    </div>

  </section>
  <section class="brand-logos">
    <div class="brand-logo-item">
      <button type="button" onclick="location.href='<c:url value='/brand/101' />'">
        <img src="<c:url value='/image/nikelogo.png'/>" alt="Nike">
      </button>
    </div>
      <div class="brand-logo-item">
        <button type="button" onclick="location.href='<c:url value='/brand/102' />'">
          <img src="<c:url value='/image/adidaslogo.png'/>" alt="Adidas">
        </button>
      </div>
        <div class="brand-logo-item">
          <button type="button" onclick="location.href='<c:url value='/brand/103' />'">
            <img src="<c:url value='/image/pumalogo.png'/>" alt="Puma">
          </button>
        </div>
          <div class="brand-logo-item">
            <button type="button" onclick="location.href='<c:url value='/brand/104' />'">
              <img src="<c:url value='/image/mizunologo.png'/>" alt="Mizuno">
            </button>
          </div>
            <div class="brand-logo-item">
              <button type="button" onclick="location.href='<c:url value='/brand/105' />'">
                <img src="<c:url value='/image/asicslogo.png'/>" alt="Asics">
              </button>
            </div>
              <div class="brand-logo-item">
                <button type="button" onclick="location.href='<c:url value='/brand/108' />'">
                  <img src="<c:url value='/image/underarmorlogo.png'/>" alt="Under Armor">
                </button>
                </div>
  </section>
</main>
</body>
</html>
<%@ include file="footer.jsp" %>