package com.crypto.chatbot.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 채팅 응답 DTO
 * LangChain 서비스에서 받은 응답을 클라이언트에게 전달하는 데이터 전송 객체
 */
public class ChatResponse {
    
    @JsonProperty("message")
    private String message;
    
    @JsonProperty("sessionId")  // sessionId로 통일
    private String sessionId;
    
    @JsonProperty("timestamp")
    private LocalDateTime timestamp;
    
    @JsonProperty("responseTimeMs")
    private long responseTimeMs;
    
    @JsonProperty("dataSources")  // 카멜케이스로 통일
    private List<String> dataSources;
    
    @JsonProperty("confidenceScore")  // 카멜케이스로 통일
    private Double confidenceScore;
    
    @JsonProperty("error")
    private String error;
    
    // 기본 생성자
    public ChatResponse() {
        this.timestamp = LocalDateTime.now();
    }
    
    // 성공 응답 생성자
    public ChatResponse(String message, String sessionId) {
        this();
        this.message = message;
        this.sessionId = sessionId;
    }
    
    // 오류 응답 생성자 (순서 바꿈)
    public ChatResponse(String message, String sessionId, String error) {
        this();
        this.message = message;
        this.sessionId = sessionId;
        this.error = error;
    }
    
    // 전체 매개변수 생성자
    public ChatResponse(String message, String sessionId, List<String> dataSources, Double confidenceScore) {
        this();
        this.message = message;
        this.sessionId = sessionId;
        this.dataSources = dataSources;
        this.confidenceScore = confidenceScore;
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
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    public long getResponseTimeMs() {
        return responseTimeMs;
    }
    
    public void setResponseTimeMs(long responseTimeMs) {
        this.responseTimeMs = responseTimeMs;
    }
    
    public List<String> getDataSources() {
        return dataSources;
    }
    
    public void setDataSources(List<String> dataSources) {
        this.dataSources = dataSources;
    }
    
    public Double getConfidenceScore() {
        return confidenceScore;
    }
    
    public void setConfidenceScore(Double confidenceScore) {
        this.confidenceScore = confidenceScore;
    }
    
    public String getError() {
        return error;
    }
    
    public void setError(String error) {
        this.error = error;
    }
    
    @Override
    public String toString() {
        return "ChatResponse{" +
                "message='" + message + '\'' +
                ", sessionId='" + sessionId + '\'' +
                ", timestamp=" + timestamp +
                ", responseTimeMs=" + responseTimeMs +
                ", dataSources=" + dataSources +
                ", confidenceScore=" + confidenceScore +
                ", error='" + error + '\'' +
                '}';
    }
}
