<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<script src="publish/user_login.js"></script>
<script>
    <c:if test="${not empty error}">
    alert("${error}");
    </c:if>
</script>
<link rel="stylesheet" href="publish/user_login.css"/>

<%@ include file="header.jsp" %>

<%--참조 CSS --%>
<%--body 로 걸려있는 CSS 를 ex)login-wrapper / login-container 와 같이 감싸고, 재조정 필요--%>

<div class="login-wrapper">
    <div class="login-container">
    <h2>로그인</h2>
    <form action="/login" method="post" id="loginForm">
        <input type="email" name="email" id="email" placeholder="아이디">
        <input type="password" name="password" id="password" placeholder="비밀번호">
        <label for="email"><input type="checkbox" name="remember"> 아이디 저장</label>
        <button type="submit">로그인</button>
    </form>

    <button type="button" onclick="location.href='/register'">회원가입</button>

        <div class="sns">
            <p>SNS 로그인</p>
            <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/_dbook/img/sns_login_kakao.png" alt="kakao">
            <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/_dbook/img/sns_login_naver.png" alt="naver">
            <img src="https://caposttr4591.cdn-nhncommerce.com/data/skin/front/dbook_20220713/_dbook/img/sns_login_facebook.png" alt="facebook">
        </div>
</div>
</div>

<%@ include file="footer.jsp" %>