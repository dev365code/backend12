<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<link rel="stylesheet" href="<c:url value='/publish/reset.css'/>">
<link rel="stylesheet" href="<c:url value='/publish/header.css'/>">
<link rel="icon" href="<c:url value='/image/football_favicon.png'/>" type="image/png">

<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>축구는 종교다</title>
  <link rel="stylesheet" href="<c:url value='/publish/header.css'/>">
  <link href="https://fonts.googleapis.com/css2?family=Bungee+Spice&display=swap" rel="stylesheet">
</head>
<body>
<%--용 추가--%>
  <div class="final_wrap">
    <header>
      <div class="top-banner">**회원가입시 10,000P 즉시할인쿠폰 지급**</div>
      <div class="header">
        <div class="logo">
          <a href="http://localhost:8080/main" style="text-decoration: none; color: inherit;">
            Soccer is religion
          </a>
        </div>
        <div class="right-menu">

          <c:choose>
            <c:when test="${not empty sessionScope.loginUser}">
              <a href="/logout" style="text-decoration: none; color: inherit;">로그아웃</a>
            </c:when>
            <c:otherwise>
              <a href="/login" style="text-decoration: none; color: inherit;">로그인</a>
              <a href="/register" style="text-decoration: none; color: inherit;">회원가입</a>
            </c:otherwise>
          </c:choose>

          <div class="search-box"><input type="text" placeholder="검색어를 입력하세요."></div>
          <div><a href="/cart" style="text-decoration: none; color: inherit;">장바구니</a></div>
        </div>
      </div>

      <%--용 추가--%>
      <nav class="main-nav">
        <ul class="nav-list">
          <!-- NEW -->
          <li><a href="<c:url value='/new'/>">NEW</a></li>

          <!-- BRAND -->
          <li class="brand-menu">
            <a href="<c:url value='/brand'/>">BRAND</a>
            <div class="brand-dropdown">
              <div class="brand-grid">
                <a href="<c:url value='/brand/101/'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/a3fbe657938f5f62c88cd06c61ddff05_86358.jpg"
                       alt="Nike">
                </a>
                <a href="<c:url value='/brand/102'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/47fc663e8b9994bcbc61fe057cf640ee_33799.jpg"
                       alt="Adidas">
                </a>
                <a href="<c:url value='/brand/103'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/ddf7651fd4a86018e05acf0ca7a889ee_15239.jpg"
                       alt="Puma">
                </a>
                <a href="<c:url value='/brand/104'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/0d62c6ba8861dc8d90621ebf10f4baea_53095.jpg"
                       alt="Mizuno">
                </a>
                <a href="<c:url value='/brand/105'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/1335036f432951aae5f2e563378e492f_81352.jpg"
                       alt="Asics">
                </a>
                <a href="<c:url value='/brand/106'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/0589c8adcd6606670162e3b3ce2e025d_54932.jpg"
                       alt="Under Armour">
                </a>
                <a href="<c:url value='/brand?name=Skechers'/>">
                  <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/img/banner/6e36caa9e3aa282fcc97d1560c18b614_46833.jpg"
                       alt="Skechers">
                </a>
              </div>
            </div>
          </li>

          <!-- 축구화 -->
          <li class="football-menu">
            <a href="<c:url value='/football_shoes'/>">축구화</a>
            <div class="dropdown football-dropdown">
              <%--          <div class="dropdown-group">--%>
              <%--            <h4>런칭캘린더</h4>--%>
              <%--            <ul>--%>
              <%--              <li><a href="<c:url value='/football_shoes?tab=launch_calendar'/>">런칭캘린더</a></li>--%>
              <%--              <li><a href="<c:url value='/football_shoes?tab=new_arrivals'/>">신상품</a></li>--%>
              <%--              <li><a href="<c:url value='/football_shoes?tab=special_edition'/>">스페셜에디션</a></li>--%>
              <%--              <li><a href="<c:url value='/football_shoes?tab=youth'/>">유소년축구화</a></li>--%>
              <%--              <li><a href="<c:url value='/football_shoes?tab=sneakers'/>">운동화</a></li>--%>
              <%--              <li><a href="<c:url value='/football_shoes?tab=slippers'/>">슬리퍼</a></li>--%>
              <%--            </ul>--%>
              <%--          </div>--%>
              <div class="dropdown-group">
                <h4>브랜드</h4>
                <ul>
                  <li><a href="<c:url value='/football_shoes?brand=Nike'/>">나이키</a></li>
                  <li><a href="<c:url value='/football_shoes?brand=Adidas'/>">아디다스</a></li>
                  <li><a href="<c:url value='/football_shoes?brand=Puma'/>">푸마</a></li>
                  <li><a href="<c:url value='/football_shoes?brand=Mizuno'/>">미즈노</a></li>
                  <li><a href="<c:url value='/football_shoes?brand=Asics'/>">아식스</a></li>
                  <li><a href="<c:url value='/football_shoes?brand=UnderArmour'/>">언더아머</a></li>
                  <li><a href="<c:url value='/football_shoes?brand=Skechers'/>">스케쳐스</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>사일로</h4>
                <ul>
                  <li><a href="<c:url value='/football_shoes?collection=Mercurial'/>">머큐리얼</a></li>
                  <li><a href="<c:url value='/football_shoes?collection=Phantom'/>">팬텀</a></li>
                  <li><a href="<c:url value='/football_shoes?collection=Tiempo'/>">티엠포</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>그라운드</h4>
                <ul>
                  <li><a href="<c:url value='/football_shoes?ground=natural'/>">천연잔디</a></li>
                  <li><a href="<c:url value='/football_shoes?ground=artificial'/>">인조잔디</a></li>
                  <li><a href="<c:url value='/football_shoes?ground=hard'/>">하드그라운드</a></li>
                  <li><a href="<c:url value='/football_shoes?ground=futsal'/>">풋살화</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>컬렉션</h4>
                <ul>
                  <li><a href="<c:url value='/football_shoes?series=KM'/>">KM</a></li>
                  <li><a href="<c:url value='/football_shoes?series=MESSI'/>">MESSI</a></li>
                  <li><a href="<c:url value='/football_shoes?series=LIGHTS_OUT'/>">LIGHTS OUT</a></li>
                  <li><a href="<c:url value='/football_shoes?series=CHROMATIC'/>">CHROMATIC</a></li>
                  <li><a href="<c:url value='/football_shoes?series=UNITED'/>">UNITED</a></li>
                  <li><a href="<c:url value='/football_shoes?series=MAD_ENERGY'/>">MAD ENERGY</a></li>
                  <li><a href="<c:url value='/football_shoes?series=MAD_VOLTAGE'/>">MAD VOLTAGE</a></li>
                </ul>
              </div>
            </div>
          </li>

          <!-- 팀 컬렉션 / 팀 유니폼 -->
          <%--            <li><a href="<c:url value='/team-collection'/>">팀 컬렉션</a></li>--%>
          <%--            <li><a href="<c:url value='/team-uniform'/>">팀 유니폼</a></li>--%>

          <!-- 의류 -->
          <li class="apparel-menu">
            <a href="<c:url value='/clothes'/>">의류</a>
            <div class="dropdown apparel-dropdown">
              <div class="dropdown-group">
                <h4>브랜드</h4>
                <ul>
                  <li><a href="<c:url value='/clothes?brand=Nike'/>">나이키</a></li>
                  <li><a href="<c:url value='/clothes?brand=Adidas'/>">아디다스</a></li>
                  <li><a href="<c:url value='/clothes?brand=Puma'/>">푸마</a></li>
                  <li><a href="<c:url value='/clothes?brand=Mizuno'/>">미즈노</a></li>
                  <li><a href="<c:url value='/clothes?brand=Asics'/>">아식스</a></li>
                  <li><a href="<c:url value='/clothes?brand=UnderArmour'/>">언더아머</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>상의</h4>
                <ul>
                  <li><a href="<c:url value='/clothes?category=short_sleeve'/>">반팔티/폴로</a></li>
                  <li><a href="<c:url value='/clothes?category=long_sleeve'/>">긴팔티/폴로</a></li>
                  <li><a href="<c:url value='/clothes?category=hoodie'/>">후드/후드자켓</a></li>
                  <li><a href="<c:url value='/clothes?category=training_top'/>">트레이닝 탑/자켓</a></li>
                  <li><a href="<c:url value='/clothes?category=padding'/>">다운&amp;패딩 조끼/자켓</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>하의</h4>
                <ul>
                  <li><a href="<c:url value='/clothes?category=training_pants'/>">트레이닝 팬츠</a></li>
                  <li><a href="<c:url value='/clothes?category=training_shorts'/>">트레이닝 쇼트</a></li>
                  <li><a href="<c:url value='/clothes?category=3_4pants'/>">트레이닝 3/4팬츠</a></li>
                  <li><a href="<c:url value='/clothes?category=inner_wear'/>">기능성 이너웨어</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>세트</h4>
                <ul>
                  <li><a href="<c:url value='/clothes?category=knit_suit'/>">니트 트레이닝 수트</a></li>
                  <li><a href="<c:url value='/clothes?category=woven_suit'/>">우븐 트레이닝 수트</a></li>
                </ul>
              </div>
            </div>
          </li>

          <!-- 용품 -->
          <li class="goods-menu">
            <a href="<c:url value='/goods'/>">용품</a>
            <div class="dropdown goods-dropdown" style="overflow-x: hidden">
              <div class="dropdown-group">
                <h4>신상품</h4>
                <ul>
                  <li><a href="<c:url value='/goods?tab=new_arrivals'/>">신상품</a></li>
                  <li><a href="<c:url value='/goods?tab=referee'/>">심판용품</a></li>
                  <li><a href="<c:url value='/goods?tab=1plus1'/>">1+1</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>축구공</h4>
                <ul>
                  <li><a href="<c:url value='/goods?category=match_ball'/>">매치볼</a></li>
                  <li><a href="<c:url value='/goods?category=futsal_ball'/>">풋살볼</a></li>
                  <li><a href="<c:url value='/goods?category=mini_ball'/>">미니볼/스킬볼</a></li>
                  <li><a href="<c:url value='/goods?category=gear_bag'/>">볼펌프/볼백</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>축구스타킹</h4>
                <ul>
                  <li><a href="<c:url value='/goods?category=stockings'/>">축구스타킹</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>신가드</h4>
                <ul>
                  <li><a href="<c:url value='/goods?category=shin_guard'/>">신가드</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>글러브</h4>
                <ul>
                  <li><a href="<c:url value='/goods?category=gk_gloves'/>">GK글러브</a></li>
                  <li><a href="<c:url value='/goods?category=field_gloves'/>">필드글러브</a></li>
                  <li><a href="<c:url value='/goods?category=fitness_gloves'/>">피트니스글러브</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>가방</h4>
                <ul>
                  <li><a href="<c:url value='/goods?category=team_bag'/>">팀백</a></li>
                  <li><a href="<c:url value='/goods?category=backpack'/>">백팩</a></li>
                  <li><a href="<c-url value='/goods?category=shoe_bag'/>">슈즈백/짐색/볼백</a></li>
                  <li><a href="<c-url value='/goods?category=waist_bag'/>">웨이스트백/기타가방</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>보호대/밴드</h4>
                <ul>
                  <li><a href="<c-url value='/goods?category=guard_band'/>">보호대/밴드</a></li>
                </ul>
              </div>
              <div class="dropdown-group">
                <h4>기타용품</h4>
                <ul>
                  <li><a href="<c-url value='/goods?category=winter_gear'/>">동계용품</a></li>
                  <li><a href="<c-url value='/goods?category=smellwell'/>">스멜웰</a></li>
                  <li><a href="<c-url value='/goods?category=soccerbee'/>">사커비</a></li>
                  <li><a href="<c-url value='/goods?category=game_equipment'/>">경기용품</a></li>
                  <li><a href="<c-url value='/goods?category=training_equipment'/>">훈련용품</a></li>
                  <li><a href="<c-url value='/goods?category=socks'/>">양말</a></li>
                  <li><a href="<c-url value='/goods?category=hat'/>">모자</a></li>
                  <li><a href="<c-url value='/goods?category=first_aid'/>">구급용품</a></li>
                </ul>
              </div>
            </div>
          </li>

          <!-- referee-kit / womens / youth -->
          <%--            <li><a href="<c:url value='/referee-kit'/>">레프리킷</a></li>--%>
          <li><a href="<c:url value='/womens'/>">우먼스</a></li>
          <li><a href="<c:url value='/youth'/>">유소년</a></li>

        </ul>
      </nav>
    </header>