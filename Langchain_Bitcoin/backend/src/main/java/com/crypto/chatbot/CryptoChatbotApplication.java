package com.crypto.chatbot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * 비트코인 챗봇 Spring Boot 메인 애플리케이션
 * 
 * 주요 기능:
 * - RESTful API 제공
 * - WebSocket 실시간 통신
 * - Python LangChain 서비스와 연동
 * - PostgreSQL + pgvector 데이터베이스 연결
 */
@SpringBootApplication
public class CryptoChatbotApplication {

    public static void main(String[] args) {
        System.out.println("🚀 비트코인 챗봇 서버 시작 중...");
        SpringApplication.run(CryptoChatbotApplication.class, args);
        System.out.println("✅ 서버가 성공적으로 시작되었습니다!");
        System.out.println("📱 웹 인터페이스: http://localhost:8080");
        System.out.println("🔗 API 문서: http://localhost:8080/api/health");
    }
}
