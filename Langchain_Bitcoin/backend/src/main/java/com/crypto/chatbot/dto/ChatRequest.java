package com.crypto.chatbot.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 채팅 요청 DTO
 * 사용자의 질문을 받는 데이터 전송 객체
 */
public class ChatRequest {
    
    @JsonProperty("message")
    private String message;
    
    @JsonProperty("session_id")
    private String sessionId;
    
    @JsonProperty("use_rag")
    private boolean useRag = true; // 기본적으로 RAG 사용
    
    // 기본 생성자
    public ChatRequest() {}
    
    // 모든 필드 생성자
    public ChatRequest(String message, String sessionId, boolean useRag) {
        this.message = message;
        this.sessionId = sessionId;
        this.useRag = useRag;
    }
    
    // Getter와 Setter
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public String getSessionId() {
        return sessionId;
    }
    
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    
    public boolean isUseRag() {
        return useRag;
    }
    
    public void setUseRag(boolean useRag) {
        this.useRag = useRag;
    }
    
    @Override
    public String toString() {
        return "ChatRequest{" +
                "message='" + message + '\'' +
                ", sessionId='" + sessionId + '\'' +
                ", useRag=" + useRag +
                '}';
    }
}
