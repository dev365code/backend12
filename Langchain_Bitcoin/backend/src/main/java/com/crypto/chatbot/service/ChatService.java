package com.crypto.chatbot.service;

import com.crypto.chatbot.dto.ChatRequest;
import com.crypto.chatbot.dto.ChatResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

@Service
public class ChatService {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatService.class);
    
    private final WebClient webClient;
    private final ObjectMapper objectMapper;
    
    @Autowired
    private LoggingService loggingService;
    
    @Value("${langchain.service.url:http://localhost:8001}")
    private String langchainServiceUrl;
    
    public ChatService(WebClient.Builder webClientBuilder, ObjectMapper objectMapper) {
        this.webClient = webClientBuilder
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024)) // 10MB
                .build();
        this.objectMapper = objectMapper;
    }
    
    /**
     * LangChain 서비스로 채팅 요청 전달
     */
    public ChatResponse processChat(ChatRequest request) {
        String userMessage = request.getMessage();
        String truncatedMessage = userMessage.substring(0, Math.min(userMessage.length(), 50)) + "...";
        
        try {
            logger.info("💬 채팅 요청 처리 시작: {}", truncatedMessage);
            
            // 로깅 서비스에 채팅 상호작용 기록
            Map<String, Object> chatMetadata = new HashMap<>();
            chatMetadata.put("messageLength", userMessage.length());
            chatMetadata.put("sessionId", request.getSessionId());
            chatMetadata.put("userMessage", truncatedMessage);
            
            loggingService.logChatInteraction("사용자 메시지 수신", chatMetadata);
            
            // sessionId가 null인 경우 기본값 생성
            if (request.getSessionId() == null || request.getSessionId().isEmpty()) {
                request.setSessionId("session_" + System.currentTimeMillis());
                logger.info("✅ SessionId 자동 생성: {}", request.getSessionId());
                
                chatMetadata.put("sessionId", request.getSessionId());
                loggingService.logChatInteraction("세션 ID 자동 생성", chatMetadata);
            }
            
            // LangChain 서비스 상태 확인
            if (!isLangChainServiceHealthy()) {
                loggingService.logError("CHAT_INTERACTION", "LangChain 서비스 연결 실패", 
                    new RuntimeException("Service not healthy"));
                return createFallbackResponse(request, "LangChain 서비스에 연결할 수 없습니다.");
            }
            
            loggingService.logChatInteraction("LangChain 서비스로 요청 전송", chatMetadata);
            
            // LangChain 서비스로 요청 전달
            ChatResponse response = webClient.post()
                    .uri(langchainServiceUrl + "/chat")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(ChatResponse.class)
                    .timeout(Duration.ofSeconds(30))
                    .block();
            
            if (response != null) {
                logger.info("✅ LangChain 응답 수신: {}자", response.getMessage().length());
                
                // LLM 응답 로깅
                Map<String, Object> responseMetadata = new HashMap<>();
                responseMetadata.put("responseLength", response.getMessage().length());
                responseMetadata.put("confidenceScore", response.getConfidenceScore());
                responseMetadata.put("dataSources", response.getDataSources());
                responseMetadata.put("sessionId", response.getSessionId());
                
                loggingService.logLLMResponse("LangChain 응답 수신 완료", responseMetadata);
                
                return response;
            } else {
                loggingService.logError("LLM_RESPONSE", "LangChain 서비스 응답 없음", 
                    new RuntimeException("No response received"));
                return createFallbackResponse(request, "LangChain 서비스에서 응답을 받지 못했습니다.");
            }
            
        } catch (WebClientResponseException e) {
            logger.error("❌ LangChain 서비스 응답 오류: {} - {}", e.getStatusCode(), e.getResponseBodyAsString());
            
            Map<String, Object> errorMetadata = new HashMap<>();
            errorMetadata.put("statusCode", e.getStatusCode().value());
            errorMetadata.put("responseBody", e.getResponseBodyAsString());
            errorMetadata.put("sessionId", request.getSessionId());
            
            loggingService.addLog("ERROR", "LLM_RESPONSE", "LangChain 서비스 HTTP 오류", 
                e.getStatusCode() + ": " + e.getResponseBodyAsString(), errorMetadata);
            
            return createFallbackResponse(request, "LangChain 서비스에서 오류가 발생했습니다: " + e.getStatusCode());
            
        } catch (Exception e) {
            logger.error("💥 채팅 처리 중 예상치 못한 오류: ", e);
            
            loggingService.logError("CHAT_INTERACTION", "채팅 처리 중 예상치 못한 오류", e);
            
            return createFallbackResponse(request, "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
        }
    }
    
    /**
     * LangChain 서비스 상태 확인
     */
    public boolean isLangChainServiceHealthy() {
        try {
            String response = webClient.get()
                    .uri(langchainServiceUrl + "/health")
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(5))
                    .block();
            
            return response != null && response.contains("healthy");
            
        } catch (Exception e) {
            logger.warn("⚠️ LangChain 서비스 상태 확인 실패: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * LangChain 서비스 통계 정보 조회
     */
    public Object getLangChainStats() {
        try {
            return webClient.get()
                    .uri(langchainServiceUrl + "/stats")
                    .retrieve()
                    .bodyToMono(Object.class)
                    .timeout(Duration.ofSeconds(10))
                    .block();
                    
        } catch (Exception e) {
            logger.error("❌ LangChain 통계 조회 실패: ", e);
            return null;
        }
    }
    
    /**
     * 대체 응답 생성 (LangChain 서비스 실패 시)
     */
    private ChatResponse createFallbackResponse(ChatRequest request, String errorMessage) {
        ChatResponse response = new ChatResponse();
        response.setMessage(getFallbackMessage(request.getMessage()) + "\n\n" + errorMessage);
        response.setSessionId(request.getSessionId());
        response.setDataSources(List.of("Spring Boot Fallback"));
        response.setConfidenceScore(0.1);
        response.setError(errorMessage);
        
        return response;
    }
    
    /**
     * 기본 대체 응답 메시지
     */
    private String getFallbackMessage(String userMessage) {
        String message = userMessage.toLowerCase();
        
        if (message.contains("안녕") || message.contains("hello")) {
            return "안녕하세요! 👋 현재 AI 서비스에 일시적인 문제가 있어 기본 응답만 제공할 수 있습니다.";
        } else if (message.contains("가격") || message.contains("price")) {
            return "💰 가격 정보 조회 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.";
        } else if (message.contains("뉴스") || message.contains("news")) {
            return "📰 뉴스 검색 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.";
        } else {
            return "죄송합니다. 현재 AI 서비스가 일시적으로 사용할 수 없습니다.";
        }
    }
}
