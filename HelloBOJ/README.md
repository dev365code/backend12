# backend12 (AI 백엔드 부트캠프 12기)

**남궁성(자바의 정석 저자) 강의 기반 실습 중심의 커리큘럼을 수강하며 학습한 내용들을 정리한 레포지토리입니다.**

GitHub에는 주제별 학습 내용, 예제, 문제 풀이 등을 체계적으로 정리하고 있습니다.

---

## 📘 Java 학습

### ▸ 자바의 정석 예제 실습
* **3판(Java 8 기준)**: 기본 문법, 객체지향, 컬렉션, 제네릭, 예외 등
  ⤷ `java-basic-3rd/` 디렉토리에 정리
* **4판(Java 21 기준)**: 람다식, 스트림, record, switch 확장 등 최신 기능 포함  
  ⤷ `java-basic-4th/` 디렉토리에 정리

📌 **실습 중심으로 출제 예제 + 자체 변형 문제 풀이 포함**

---

## ☕ Spring & Spring Boot

* **`spring-basic/`** → IoC, DI, Bean 등록, AOP 등 핵심 개념 정리
* **`spring-boot/`** → REST API 설계, Validation, 예외처리, JPA 연동 등 실습 진행 중

---

## 📂 데이터베이스 관련 학습

* **`db-sql/`** → Oracle SQL 기본 문법, 조인, 서브쿼리, 인덱스 실습
* **`jdbc/`** → 자바와 DB 연동 (JDBC 기반 미니 프로젝트 포함 예정)

---

## 🔢 백준 BOJ 문제 풀이

### 📊 현재 진행 상황
* **디렉토리**: `HelloBOJ/`
* **총 풀이 문제 수**: **36문제** (2025.05.18 기준)
* **진행 단계**: **브론즈 → 실버** 단계별 진행 중
* **목적**: 자바 문법 복습 + 알고리즘 기초 훈련 겸용

---

## 🛠 토이 프로젝트

### 프로젝트 2&3: 쇼핑몰 만들기
**프로젝트명**: "축구는 종교다" - 축구용품 쇼핑몰 구현

#### 🎯 프로젝트 개요
- **기간**: 2025.06.09 ~ 2025.06.27
- **팀 구성**: 6명 (10조)
- **목적**: Spring을 활용한 쇼핑몰 기본 & 심화 기능 구현

#### 🔧 주요 기능
1. **회원가입 & 로그인** 기능
2. **상품 목록 & 상세** 내용 기능  
3. **주문 & 장바구니** 기능
4. **게시판** 기능

#### 💻 기술 스택
**Frontend**
- HTML, CSS, JavaScript(ES6+)
- JSP (Java Server Pages)
- JSTL (Java Standard Tag Library)

**Backend**
- Java 17
- Spring Framework 5, Spring MVC
- MyBatis, MySQL 8

**개발환경**
- IntelliJ IDEA Ultimate (JDK 17)
- Visual Studio Code
- Apache Tomcat 9
- Git & GitHub

#### 👥 팀원
- 홍성훈, 김지승, 이우용, 손장호, 이지현, 이은영

---

## 🗂 전체 폴더 구조

```
📁 backend12/
├── 📁 HelloBOJ/                    # 백준 문제 풀이
│
├── 📁 java-basic-3rd/              # 자바의 정석 3판 예제
│   └── 📁 Chapter05_ObjectOriented/
│       └── ClassExample.java
│
├── 📁 java-basic-4th/              # 자바의 정석 4판 예제  
│
├── 📁 spring-basic/                # Spring 핵심 개념
│
├── 📁 spring-boot/                 # Spring Boot 실습
│   └── 📁 user-api/
│       ├── 📁 controller/
│       └── 📁 service/
│
├── 📁 db-sql/                      # SQL 학습
│
├── 📁 jdbc/                       # JDBC 연동
│
└── 📁 Toy_Project1-2-3/           # 쇼핑몰 프로젝트
    ├── 📁 src/main/java/toyproject/
    │   ├── 📁 config/
    │   ├── 📁 controller/  
    │   ├── 📁 service/
    │   └── 📁 mapper/
    └── 📁 src/main/webapp/WEB-INF/views/
```

---

## 📝 개발 원칙

### 코딩 스타일
- **가독성**: 명확한 변수명과 메서드명 사용
- **유지보수성**: 적절한 주석과 문서화
- **일관성**: 팀 내 코딩 컨벤션 준수

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정  
refactor: 코드 리팩토링
docs: 문서 수정
style: 코드 스타일 변경
test: 테스트 코드
```

### 학습 방법
- **실습 중심**: 이론보다는 직접 코딩하며 학습
- **단계별 진행**: 기초부터 심화까지 체계적 접근
- **문제 해결**: 에러와 버그를 통한 실력 향상

---

## 🔗 참고 링크

- **스터디 블로그**: [arex.tistory.com](https://arex.tistory.com)
- **프로젝트 노션**: [팀페이지](https://www.notion.so/No-10-2099047c353d80afa5e2cac96ee5b2ab)
- **백준 온라인 저지**: [BOJ](https://www.acmicpc.net)

---
