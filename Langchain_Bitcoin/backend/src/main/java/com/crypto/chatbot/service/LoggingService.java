package com.crypto.chatbot.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;

@Service
public class LoggingService {
    
    private static final Logger logger = LoggerFactory.getLogger(LoggingService.class);
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    // 메모리에 최근 로그 저장 (최대 1000개)
    private final Queue<LogEntry> logQueue = new ConcurrentLinkedQueue<>();
    private static final int MAX_LOG_ENTRIES = 1000;
    
    // 로그 엔트리 클래스
    public static class LogEntry {
        private String timestamp;
        private String level;
        private String category;
        private String message;
        private String details;
        private Map<String, Object> metadata;
        
        public LogEntry() {}
        
        public LogEntry(String level, String category, String message, String details) {
            this.timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"));
            this.level = level;
            this.category = category;
            this.message = message;
            this.details = details;
            this.metadata = new HashMap<>();
        }
        
        // Getters and Setters
        public String getTimestamp() { return timestamp; }
        public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
        
        public String getLevel() { return level; }
        public void setLevel(String level) { this.level = level; }
        
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        
        public String getDetails() { return details; }
        public void setDetails(String details) { this.details = details; }
        
        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    }
    
    /**
     * 로그 추가
     */
    public void addLog(String level, String category, String message, String details) {
        LogEntry entry = new LogEntry(level, category, message, details);
        
        // 큐에 추가
        logQueue.offer(entry);
        
        // 최대 크기 초과시 오래된 로그 제거
        while (logQueue.size() > MAX_LOG_ENTRIES) {
            logQueue.poll();
        }
        
        // 실제 로거에도 기록
        switch (level.toUpperCase()) {
            case "ERROR":
                logger.error("[{}] {} - {}", category, message, details);
                break;
            case "WARN":
                logger.warn("[{}] {} - {}", category, message, details);
                break;
            case "INFO":
                logger.info("[{}] {} - {}", category, message, details);
                break;
            case "DEBUG":
                logger.debug("[{}] {} - {}", category, message, details);
                break;
            default:
                logger.info("[{}] {} - {}", category, message, details);
        }
    }
    
    /**
     * 메타데이터와 함께 로그 추가
     */
    public void addLog(String level, String category, String message, String details, Map<String, Object> metadata) {
        LogEntry entry = new LogEntry(level, category, message, details);
        entry.setMetadata(metadata != null ? metadata : new HashMap<>());
        
        logQueue.offer(entry);
        
        while (logQueue.size() > MAX_LOG_ENTRIES) {
            logQueue.poll();
        }
        
        // 메타데이터 포함하여 로깅
        try {
            String metadataStr = objectMapper.writeValueAsString(metadata);
            switch (level.toUpperCase()) {
                case "ERROR":
                    logger.error("[{}] {} - {} | Metadata: {}", category, message, details, metadataStr);
                    break;
                case "WARN":
                    logger.warn("[{}] {} - {} | Metadata: {}", category, message, details, metadataStr);
                    break;
                case "INFO":
                    logger.info("[{}] {} - {} | Metadata: {}", category, message, details, metadataStr);
                    break;
                case "DEBUG":
                    logger.debug("[{}] {} - {} | Metadata: {}", category, message, details, metadataStr);
                    break;
                default:
                    logger.info("[{}] {} - {} | Metadata: {}", category, message, details, metadataStr);
            }
        } catch (Exception e) {
            logger.error("Failed to serialize metadata", e);
        }
    }
    
    /**
     * 모든 로그 조회
     */
    public List<LogEntry> getAllLogs() {
        return new ArrayList<>(logQueue);
    }
    
    /**
     * 카테고리별 로그 조회
     */
    public List<LogEntry> getLogsByCategory(String category) {
        return logQueue.stream()
                .filter(entry -> category.equals(entry.getCategory()))
                .collect(ArrayList::new, (list, entry) -> list.add(entry), (list1, list2) -> list1.addAll(list2));
    }
    
    /**
     * 레벨별 로그 조회
     */
    public List<LogEntry> getLogsByLevel(String level) {
        return logQueue.stream()
                .filter(entry -> level.equalsIgnoreCase(entry.getLevel()))
                .collect(ArrayList::new, (list, entry) -> list.add(entry), (list1, list2) -> list1.addAll(list2));
    }
    
    /**
     * 최근 N개 로그 조회
     */
    public List<LogEntry> getRecentLogs(int count) {
        List<LogEntry> allLogs = new ArrayList<>(logQueue);
        int size = allLogs.size();
        int fromIndex = Math.max(0, size - count);
        return allLogs.subList(fromIndex, size);
    }
    
    /**
     * 로그 통계 조회
     */
    public Map<String, Object> getLogStatistics() {
        Map<String, Object> stats = new HashMap<>();
        
        // 총 로그 수
        stats.put("totalLogs", logQueue.size());
        
        // 레벨별 통계
        Map<String, Long> levelStats = new HashMap<>();
        Map<String, Long> categoryStats = new HashMap<>();
        
        for (LogEntry entry : logQueue) {
            levelStats.merge(entry.getLevel(), 1L, Long::sum);
            categoryStats.merge(entry.getCategory(), 1L, Long::sum);
        }
        
        stats.put("levelStats", levelStats);
        stats.put("categoryStats", categoryStats);
        
        // 최근 로그 시간
        if (!logQueue.isEmpty()) {
            LogEntry latest = ((ConcurrentLinkedQueue<LogEntry>) logQueue).stream()
                    .reduce((first, second) -> second)
                    .orElse(null);
            if (latest != null) {
                stats.put("latestLogTime", latest.getTimestamp());
            }
        }
        
        return stats;
    }
    
    /**
     * 로그 초기화
     */
    public void clearLogs() {
        logQueue.clear();
        logger.info("Log queue cleared");
    }
    
    // 편의 메소드들
    public void logNewsCollection(String message, Map<String, Object> metadata) {
        addLog("INFO", "NEWS_COLLECTION", message, "", metadata);
    }
    
    public void logNewsPreprocessing(String message, Map<String, Object> metadata) {
        addLog("INFO", "NEWS_PREPROCESSING", message, "", metadata);
    }
    
    public void logVectorStorage(String message, Map<String, Object> metadata) {
        addLog("INFO", "VECTOR_STORAGE", message, "", metadata);
    }
    
    public void logChatInteraction(String message, Map<String, Object> metadata) {
        addLog("INFO", "CHAT_INTERACTION", message, "", metadata);
    }
    
    public void logLLMResponse(String message, Map<String, Object> metadata) {
        addLog("INFO", "LLM_RESPONSE", message, "", metadata);
    }
    
    public void logError(String category, String message, Exception e) {
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("exception", e.getClass().getSimpleName());
        metadata.put("errorMessage", e.getMessage());
        addLog("ERROR", category, message, e.getMessage(), metadata);
    }
}