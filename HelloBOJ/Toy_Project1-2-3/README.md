# 토이 프로젝트 2&3 : 쇼핑몰 만들기 프로젝트 2&3단계
### [프로젝트 개요] 
- **프로젝트 명** : 스프링을 통한 쇼핑몰 기본&심화 기능 구현
- **주제** : 축구 용품 쇼핑몰 "축구는 종교다 (Soccer Is Religion)"
- **상세 내용 :** [프로젝트 RFP 노션 링크](https://www.notion.so/Toy-Project-2-3-1b69047c353d8136b5b3f9614a04bb65?source=copy_link)
- **팀페이지 :** [노션 링크](https://www.notion.so/No-10-2099047c353d80afa5e2cac96ee5b2ab?source=copy_link)
- **수행 및 결과물 제출 기한** : 6/9 (월) ~ 6/27 (금) 14:00
- **멘토진 코드리뷰 기한** : 6/30 (월) ~ 7/13 (일), 2주 간 진행

## 프로젝트 소개 (Introduction)
스프링 프레임워크를 활용한 축구 용품 쇼핑몰 프로젝트입니다. 회원가입부터 상품 주문까지 전체적인 이커머스 플로우를 구현하며, 실무에 가까운 기능들을 개발했습니다.

### 주요 기능 (Key Features)

#### 회원 관리
- **회원가입 & 로그인** : 이메일 중복 확인, 이메일 인증, 패스워드 암호화
- **보안 기능** : 비밀번호 3회 실패 시 계정 잠금, 세션 관리
- **유효성 검증** : 프론트엔드 및 백엔드 이중 검증

####  상품 관리
- **상품 목록** : 카테고리별 상품 분류 (축구화, 유니폼, 용품 등)
- **상품 상세** : 상세 정보, 이미지, 평점, 리뷰 시스템
- **검색 & 필터링** : 브랜드, 가격, 평점별 필터링

#### 주문 & 장바구니
- **장바구니** : 상품 추가/삭제, 수량 변경
- **주문 처리** : 주문서 작성, 결제 프로세스
- **주문 관리** : 주문 내역 조회, 배송 상태 확인

#### 게시판
- **공지사항** : 상단 고정 공지, 일반 공지 페이징 처리
- **FAQ** : 자주 묻는 질문 카테고리별 관리
- **문의 게시판** : 사용자 문의 및 답변 관리

### 데이터베이스 설계 (ERD)
![축구는 종교다_통합 ERD](https://github.com/user-attachments/assets/ab39a3c5-8ee4-4a52-8c43-c84c009c1a7c)

## 기술 스택 (Technology Stack)

### Frontend
- **HTML5, CSS3** : 시맨틱 마크업, 반응형 디자인
- **JavaScript (ES6+)** : 동적 UI, 폼 검증, AJAX 통신
- **JSP (Java Server Pages)** : 서버사이드 렌더링
- **JSTL (Java Standard Tag Library)** : 템플릿 로직 처리

### Backend
- **Java 17** : 최신 자바 기능 활용
- **Spring Framework 5** : DI, AOP, MVC 패턴
- **Spring MVC** : 웹 계층 아키텍처
- **MyBatis** : SQL 매퍼 프레임워크
- **MySQL 8** : 관계형 데이터베이스

### 개발환경 (Development Environment)
- **IDE** : IntelliJ IDEA Ultimate (JDK 17)
- **Editor** : Visual Studio Code
- **WAS** : Apache Tomcat 9
- **Version Control** : Git & GitHub
- **Build Tool** : Maven

## 프로젝트 구조 (Project Structure)

```
Toy_Project1-2-3/
├── src/main/
│   ├── java/toyproject/
│   │   ├── controller/     # MVC 컨트롤러
│   │   ├── service/        # 비즈니스 로직
│   │   ├── mapper/         # MyBatis 매퍼
│   │   ├── dto/           # 데이터 전송 객체
│   │   └── config/        # 설정 클래스
│   ├── resources/
│   │   ├── mapper/        # MyBatis XML 매퍼
│   │   └── config/        # 설정 파일
│   └── webapp/
│       ├── WEB-INF/       # 웹 설정
│       ├── css/           # 스타일시트
│       ├── js/            # JavaScript 파일
│       └── jsp/           # JSP 페이지
└── README.md
```

## 시작하기 (Getting Started)

### 사전 요구사항
- Java 17 이상
- Apache Tomcat 9
- MySQL 8
- IntelliJ IDEA 또는 Eclipse

## 주요 화면 (Screenshots)

### 메인 페이지
- 브랜드별 상품 진열
- 최신 상품, 이벤트 상품 노출
- 반응형 네비게이션

### 회원가입/로그인
- 실시간 유효성 검증
- 이메일 인증 시스템
- 보안 강화 기능

### 상품 목록/상세
- 카테고리별 필터링
- 상품 이미지 갤러리
- 리뷰 및 평점 시스템

## 개선 요구사항
- [ ] **결제 시스템** : PG사 연동 (토스페이, 카카오페이)
- [ ] **알림 시스템** : 실시간 알림, 이메일 발송
- [ ] **관리자 페이지** : 상품/주문/회원 관리 기능
- [ ] **API 서버** : RESTful API 구현
- [ ] **모바일 앱** : React Native 또는 Flutter
- [ ] **추천 시스템** : 개인화 상품 추천
- [ ] **소셜 로그인** : 카카오, 네이버, 구글 로그인

## 팀원 (Contributors)
| 이름 | GitHub | 역할 |
|------|--------|------|
| 홍성훈 | [@callmehoon](https://github.com/callmehoon) |
| 김지승 | [@kkj5158](https://github.com/kkj5158) |
| 이우용 | [@dev365code](https://github.com/dev365code) |
| 손장호 | [@son-j-h](https://github.com/son-j-h) |
| 이지현 | [@leejihyun2](https://github.com/leejihyun2) |
