package com.crypto.chatbot.controller;

import com.crypto.chatbot.dto.ChatRequest;
import com.crypto.chatbot.dto.ChatResponse;
import com.crypto.chatbot.service.ChatService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class ChatController {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);
    
    private final ChatService chatService;
    
    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }
    
    /**
     * 채팅 처리 엔드포인트
     */
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        try {
            logger.info("📨 채팅 요청 수신: {}", request.getMessage().substring(0, 
                Math.min(request.getMessage().length(), 50)) + "...");
            
            ChatResponse response = chatService.processChat(request);
            
            logger.info("📤 채팅 응답 전송: {}자", response.getMessage().length());
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("💥 채팅 처리 중 오류: ", e);
            
            ChatResponse errorResponse = new ChatResponse();
            errorResponse.setMessage("죄송합니다. 서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
            errorResponse.setSessionId(request.getSessionId());
            errorResponse.setError(e.getMessage());
            
            return ResponseEntity.ok(errorResponse);
        }
    }
    
    /**
     * 시스템 상태 확인
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> status = new HashMap<>();
        status.put("status", "healthy");
        status.put("service", "Spring Boot Crypto Chatbot");
        status.put("timestamp", LocalDateTime.now());
        status.put("langchain_service", chatService.isLangChainServiceHealthy() ? "connected" : "disconnected");
        
        return ResponseEntity.ok(status);
    }
    
    /**
     * LangChain 서비스 통계
     */
    @GetMapping("/langchain/stats")
    public ResponseEntity<Object> getLangChainStats() {
        Object stats = chatService.getLangChainStats();
        
        if (stats != null) {
            return ResponseEntity.ok(stats);
        } else {
            Map<String, String> error = new HashMap<>();
            error.put("error", "LangChain 서비스 통계를 조회할 수 없습니다");
            return ResponseEntity.ok(error);
        }
    }
    
    /**
     * 시스템 정보
     */
    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> info() {
        Map<String, Object> info = new HashMap<>();
        info.put("name", "Crypto Chatbot Backend");
        info.put("version", "1.0.0");
        info.put("description", "Spring Boot + LangChain 기반 암호화폐 챗봇");
        info.put("features", new String[]{
            "LangChain 서비스 연동",
            "실시간 채팅 API",
            "정적 리소스 서빙",
            "CORS 지원"
        });
        info.put("timestamp", LocalDateTime.now());
        
        return ResponseEntity.ok(info);
    }
}
