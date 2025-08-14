# Backend Development Portfolio

AI 백엔드 부트캠프 12기 학습 및 프로젝트 레포지토리

## Projects

### 1. Football Equipment E-commerce Platform
**축구용품 쇼핑몰** | Spring MVC + MyBatis + MySQL

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│    Database     │
│                 │     │                 │     │                 │
│ JSP/HTML/CSS    │     │ Spring MVC      │     │ MySQL 8         │
│ JavaScript      │     │ MyBatis         │     │ Connection Pool │
│ JSTL            │     │ Tomcat 9        │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**핵심 기능**
- 사용자 인증 및 권한 관리
- 상품 관리 (CRUD)
- 장바구니 및 주문 처리
- 게시판 시스템

**기술 스택**
- Java 17, Spring Framework 5
- MyBatis, MySQL 8
- JSP, JSTL, JavaScript

### 2. Crypto News Analysis Chatbot
**암호화폐 뉴스 분석 챗봇** | Spring Boot + LangChain + PostgreSQL

```
┌────────────────┐   ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
│  News Sources  │──▶│  Spring Boot    │──▶│   LangChain      │──▶│   PostgreSQL    │
│                │   │                 │   │                  │   │                 │
│ NewsData API   │   │ REST API        │   │ OpenAI GPT       │   │ Vector Store    │
│ RSS Feeds      │   │ Redis Cache     │   │ News Analysis    │   │ News Archive    │
│ CoinDesk       │   │ WebSocket       │   │ Price Tools      │   │                 │
└────────────────┘   └─────────────────┘   └──────────────────┘   └─────────────────┘
```

**핵심 기능**
- 실시간 암호화폐 뉴스 수집
- AI 기반 뉴스 분석 및 요약
- 가격 정보 통합 제공
- 실시간 채팅 인터페이스

**기술 스택**
- Spring Boot, FastAPI (Python)
- PostgreSQL + pgvector, Redis
- OpenAI API, LangChain
- WebSocket, REST API

## Algorithm Practice

**백준 온라인 저지**: 46문제 해결 (진행 중)
- Bronze → Silver 단계별 진행
- Java 17 기반 문법 복습 겸용

## Tech Stack

**Languages**
- Java 17/21
- Python 3.11+
- JavaScript (ES6+)

**Frameworks**
- Spring Framework 5
- Spring Boot 3
- FastAPI
- LangChain

**Databases**
- MySQL 8
- PostgreSQL (with pgvector)
- Redis

**Tools**
- IntelliJ IDEA
- Docker
- Git/GitHub
