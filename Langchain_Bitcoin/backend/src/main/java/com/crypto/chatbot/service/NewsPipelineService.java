package com.crypto.chatbot.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
public class NewsPipelineService {
    
    private static final Logger logger = LoggerFactory.getLogger(NewsPipelineService.class);
    
    @Autowired
    private LoggingService loggingService;
    
    private final WebClient webClient;
    
    @Value("${langchain.service.url:http://localhost:8001}")
    private String pythonPipelineUrl;
    
    public NewsPipelineService(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(50 * 1024 * 1024)) // 50MB
                .build();
    }
    
    /**
     * 뉴스 파이프라인 실행 (비동기)
     */
    public CompletableFuture<Map<String, Object>> runNewsPipelineAsync(int hoursBack) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                loggingService.logNewsCollection("뉴스 파이프라인 실행 시작", 
                    Map.of("hoursBack", hoursBack, "type", "manual"));
                
                // Python 뉴스 파이프라인 실행
                Map<String, Object> result = webClient.post()
                        .uri(pythonPipelineUrl + "/pipeline/run")
                        .bodyValue(Map.of("hours_back", hoursBack))
                        .retrieve()
                        .bodyToMono(Map.class)
                        .timeout(Duration.ofMinutes(10)) // 10분 타임아웃
                        .block();
                
                if (result != null) {
                    // 성공 로깅
                    Map<String, Object> successMetadata = new HashMap<>(result);
                    successMetadata.put("executionType", "manual");
                    
                    loggingService.logNewsCollection("뉴스 파이프라인 실행 완료", successMetadata);
                    
                    // 각 단계별 상세 로깅
                    logPipelineStepResults(result);
                    
                    return result;
                } else {
                    throw new RuntimeException("파이프라인 실행 결과가 null입니다.");
                }
                
            } catch (Exception e) {
                logger.error("뉴스 파이프라인 실행 실패", e);
                loggingService.logError("NEWS_COLLECTION", "뉴스 파이프라인 실행 실패", e);
                
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("success", false);
                errorResult.put("error", e.getMessage());
                errorResult.put("collected_count", 0);
                errorResult.put("processed_count", 0);
                errorResult.put("saved_count", 0);
                
                return errorResult;
            }
        });
    }
    
    /**
     * 증분 뉴스 업데이트 실행
     */
    public CompletableFuture<Map<String, Object>> runIncrementalUpdateAsync(int hoursBack) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                loggingService.logNewsCollection("증분 뉴스 업데이트 시작", 
                    Map.of("hoursBack", hoursBack, "type", "incremental"));
                
                Map<String, Object> result = webClient.post()
                        .uri(pythonPipelineUrl + "/pipeline/incremental")
                        .bodyValue(Map.of("hours_back", hoursBack))
                        .retrieve()
                        .bodyToMono(Map.class)
                        .timeout(Duration.ofMinutes(5))
                        .block();
                
                if (result != null) {
                    Map<String, Object> metadata = new HashMap<>(result);
                    metadata.put("executionType", "incremental");
                    
                    loggingService.logNewsCollection("증분 뉴스 업데이트 완료", metadata);
                    logPipelineStepResults(result);
                    
                    return result;
                } else {
                    throw new RuntimeException("증분 업데이트 결과가 null입니다.");
                }
                
            } catch (Exception e) {
                logger.error("증분 뉴스 업데이트 실패", e);
                loggingService.logError("NEWS_COLLECTION", "증분 뉴스 업데이트 실패", e);
                
                Map<String, Object> errorResult = new HashMap<>();
                errorResult.put("success", false);
                errorResult.put("error", e.getMessage());
                
                return errorResult;
            }
        });
    }
    
    /**
     * 뉴스 검색 (벡터 유사도 기반)
     */
    public Map<String, Object> searchNews(String query, int limit) {
        try {
            loggingService.logVectorStorage("뉴스 검색 시작", 
                Map.of("query", query, "limit", limit));
            
            Map<String, Object> result = webClient.post()
                    .uri(pythonPipelineUrl + "/news/search")
                    .bodyValue(Map.of("query", query, "limit", limit))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(30))
                    .block();
            
            if (result != null) {
                loggingService.logVectorStorage("뉴스 검색 완료", 
                    Map.of("query", query, "resultCount", 
                        result.get("results") != null ? ((java.util.List) result.get("results")).size() : 0));
                
                return result;
            } else {
                throw new RuntimeException("검색 결과가 null입니다.");
            }
            
        } catch (Exception e) {
            logger.error("뉴스 검색 실패: query={}", query, e);
            loggingService.logError("VECTOR_STORAGE", "뉴스 검색 실패", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("error", e.getMessage());
            errorResult.put("results", java.util.List.of());
            
            return errorResult;
        }
    }
    
    /**
     * 뉴스 통계 조회
     */
    public Map<String, Object> getNewsStatistics() {
        try {
            Map<String, Object> result = webClient.get()
                    .uri(pythonPipelineUrl + "/news/statistics")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .timeout(Duration.ofSeconds(10))
                    .block();
            
            if (result != null) {
                loggingService.addLog("INFO", "VECTOR_STORAGE", "뉴스 통계 조회 완료", "", result);
                return result;
            } else {
                throw new RuntimeException("통계 결과가 null입니다.");
            }
            
        } catch (Exception e) {
            logger.error("뉴스 통계 조회 실패", e);
            loggingService.logError("VECTOR_STORAGE", "뉴스 통계 조회 실패", e);
            
            Map<String, Object> errorResult = new HashMap<>();
            errorResult.put("success", false);
            errorResult.put("error", e.getMessage());
            
            return errorResult;
        }
    }
    
    /**
     * Python 서비스 상태 확인
     */
    public boolean isPythonServiceHealthy() {
        try {
            String response = webClient.get()
                    .uri(pythonPipelineUrl + "/health")
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(5))
                    .block();
            
            boolean isHealthy = response != null && response.contains("healthy");
            
            loggingService.addLog(isHealthy ? "INFO" : "WARN", "NEWS_COLLECTION", 
                "Python 서비스 상태 확인", "상태: " + (isHealthy ? "정상" : "비정상"), 
                Map.of("healthy", isHealthy, "response", response != null ? response : "null"));
            
            return isHealthy;
            
        } catch (Exception e) {
            logger.warn("Python 서비스 상태 확인 실패: {}", e.getMessage());
            loggingService.logError("NEWS_COLLECTION", "Python 서비스 상태 확인 실패", e);
            return false;
        }
    }
    
    /**
     * 파이프라인 단계별 결과 로깅
     */
    private void logPipelineStepResults(Map<String, Object> result) {
        try {
            // 수집 단계 로깅
            Object collectedCount = result.get("collected_count");
            if (collectedCount != null) {
                loggingService.logNewsCollection("뉴스 수집 완료", 
                    Map.of("count", collectedCount));
            }
            
            // 전처리 단계 로깅
            Object processedCount = result.get("processed_count");
            if (processedCount != null) {
                loggingService.logNewsPreprocessing("뉴스 전처리 완료", 
                    Map.of("count", processedCount));
            }
            
            // 저장 단계 로깅
            Object savedCount = result.get("saved_count");
            if (savedCount != null) {
                loggingService.logVectorStorage("벡터 DB 저장 완료", 
                    Map.of("count", savedCount));
            }
            
            // 에러 로깅
            Object errors = result.get("errors");
            if (errors != null && errors instanceof java.util.List) {
                java.util.List errorList = (java.util.List) errors;
                if (!errorList.isEmpty()) {
                    for (Object error : errorList) {
                        loggingService.addLog("ERROR", "NEWS_PREPROCESSING", 
                            "파이프라인 처리 중 오류", error.toString(), 
                            Map.of("errorDetail", error));
                    }
                }
            }
            
            // 실행 시간 로깅
            Object duration = result.get("duration_seconds");
            if (duration != null) {
                loggingService.addLog("INFO", "NEWS_COLLECTION", 
                    "파이프라인 실행 시간", duration + "초", 
                    Map.of("durationSeconds", duration));
            }
            
        } catch (Exception e) {
            logger.warn("파이프라인 결과 로깅 중 오류", e);
        }
    }
    
    /**
     * 자동 뉴스 업데이트 스케줄러에서 호출할 메소드
     */
    public void runScheduledUpdate() {
        loggingService.logNewsCollection("스케줄된 뉴스 업데이트 시작", 
            Map.of("type", "scheduled"));
        
        runIncrementalUpdateAsync(6) // 최근 6시간
            .thenAccept(result -> {
                loggingService.logNewsCollection("스케줄된 뉴스 업데이트 완료", result);
            })
            .exceptionally(throwable -> {
                loggingService.logError("NEWS_COLLECTION", "스케줄된 뉴스 업데이트 실패", 
                    (Exception) throwable);
                return null;
            });
    }
}