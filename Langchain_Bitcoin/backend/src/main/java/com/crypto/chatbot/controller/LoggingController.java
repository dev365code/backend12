package com.crypto.chatbot.controller;

import com.crypto.chatbot.service.LoggingService;
import com.crypto.chatbot.service.LoggingService.LogEntry;
import com.crypto.chatbot.service.NewsPipelineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

@Controller
@RequestMapping("/logs")
public class LoggingController {
    
    @Autowired
    private LoggingService loggingService;
    
    @Autowired
    private NewsPipelineService newsPipelineService;
    
    private final Map<String, SseEmitter> sseEmitters = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    /**
     * 로깅 모니터링 페이지
     */
    @GetMapping("")
    public String logsPage(Model model) {
        model.addAttribute("title", "뉴스 파이프라인 로깅 모니터");
        return "logs";
    }
    
    /**
     * 모든 로그 조회 API
     */
    @GetMapping("/api/all")
    @ResponseBody
    public ResponseEntity<List<LogEntry>> getAllLogs() {
        List<LogEntry> logs = loggingService.getAllLogs();
        return ResponseEntity.ok(logs);
    }
    
    /**
     * 최근 N개 로그 조회 API
     */
    @GetMapping("/api/recent")
    @ResponseBody
    public ResponseEntity<List<LogEntry>> getRecentLogs(@RequestParam(defaultValue = "50") int count) {
        List<LogEntry> logs = loggingService.getRecentLogs(count);
        return ResponseEntity.ok(logs);
    }
    
    /**
     * 카테고리별 로그 조회 API
     */
    @GetMapping("/api/category/{category}")
    @ResponseBody
    public ResponseEntity<List<LogEntry>> getLogsByCategory(@PathVariable String category) {
        List<LogEntry> logs = loggingService.getLogsByCategory(category);
        return ResponseEntity.ok(logs);
    }
    
    /**
     * 레벨별 로그 조회 API
     */
    @GetMapping("/api/level/{level}")
    @ResponseBody
    public ResponseEntity<List<LogEntry>> getLogsByLevel(@PathVariable String level) {
        List<LogEntry> logs = loggingService.getLogsByLevel(level);
        return ResponseEntity.ok(logs);
    }
    
    /**
     * 로그 통계 조회 API
     */
    @GetMapping("/api/statistics")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getLogStatistics() {
        Map<String, Object> stats = loggingService.getLogStatistics();
        return ResponseEntity.ok(stats);
    }
    
    /**
     * 로그 초기화 API
     */
    @PostMapping("/api/clear")
    @ResponseBody
    public ResponseEntity<String> clearLogs() {
        loggingService.clearLogs();
        return ResponseEntity.ok("로그가 초기화되었습니다.");
    }
    
    /**
     * 실시간 로그 스트리밍 (Server-Sent Events)
     */
    @GetMapping(value = "/api/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @ResponseBody
    public SseEmitter streamLogs(@RequestParam(required = false) String category,
                                @RequestParam(required = false) String level) {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        String emitterId = java.util.UUID.randomUUID().toString();
        sseEmitters.put(emitterId, emitter);
        
        // 연결 종료 시 정리
        emitter.onCompletion(() -> sseEmitters.remove(emitterId));
        emitter.onTimeout(() -> sseEmitters.remove(emitterId));
        emitter.onError((ex) -> sseEmitters.remove(emitterId));
        
        // 초기 데이터 전송
        try {
            List<LogEntry> recentLogs = loggingService.getRecentLogs(10);
            for (LogEntry log : recentLogs) {
                if (shouldSendLog(log, category, level)) {
                    emitter.send(SseEmitter.event()
                            .name("log")
                            .data(log));
                }
            }
        } catch (IOException e) {
            emitter.completeWithError(e);
        }
        
        return emitter;
    }
    
    /**
     * 테스트 로그 생성 API
     */
    @PostMapping("/api/test")
    @ResponseBody
    public ResponseEntity<String> createTestLog(@RequestParam String level,
                                              @RequestParam String category,
                                              @RequestParam String message) {
        loggingService.addLog(level, category, message, "테스트 로그입니다.");
        
        // 실시간 스트리밍으로 전송
        LogEntry testLog = new LoggingService.LogEntry(level, category, message, "테스트 로그입니다.");
        broadcastLogToEmitters(testLog);
        
        return ResponseEntity.ok("테스트 로그가 생성되었습니다.");
    }
    
    /**
     * 뉴스 파이프라인 실행 트리거 API
     */
    @PostMapping("/api/trigger-pipeline")
    @ResponseBody
    public ResponseEntity<String> triggerNewsPipeline() {
        try {
            // 파이프라인 실행 로그
            loggingService.logNewsCollection("뉴스 파이프라인 수동 실행 시작", Map.of("triggeredBy", "manual"));
            
            // 비동기로 파이프라인 실행
            newsPipelineService.runNewsPipelineAsync(24)
                .thenAccept(result -> {
                    loggingService.logNewsCollection("뉴스 파이프라인 수동 실행 완료", result);
                })
                .exceptionally(throwable -> {
                    loggingService.logError("NEWS_COLLECTION", "뉴스 파이프라인 수동 실행 실패", 
                        (Exception) throwable);
                    return null;
                });
            
            return ResponseEntity.ok("뉴스 파이프라인이 시작되었습니다. 로그에서 진행 상황을 확인하세요.");
            
        } catch (Exception e) {
            loggingService.logError("NEWS_COLLECTION", "뉴스 파이프라인 실행 요청 실패", e);
            return ResponseEntity.status(500).body("파이프라인 실행 요청 실패: " + e.getMessage());
        }
    }
    
    /**
     * 로그 필터링 조건 확인
     */
    private boolean shouldSendLog(LogEntry log, String category, String level) {
        if (category != null && !category.isEmpty() && !category.equals(log.getCategory())) {
            return false;
        }
        if (level != null && !level.isEmpty() && !level.equalsIgnoreCase(log.getLevel())) {
            return false;
        }
        return true;
    }
    
    /**
     * 모든 SSE 클라이언트에 로그 브로드캐스트
     */
    public void broadcastLogToEmitters(LogEntry logEntry) {
        sseEmitters.entrySet().removeIf(entry -> {
            try {
                entry.getValue().send(SseEmitter.event()
                        .name("log")
                        .data(logEntry));
                return false;
            } catch (IOException e) {
                return true; // 실패한 emitter 제거
            }
        });
    }
    
    /**
     * 정기적으로 새로운 로그를 브로드캐스트 (실제로는 LoggingService에서 호출해야 함)
     */
    private void startLogBroadcasting() {
        scheduler.scheduleAtFixedRate(() -> {
            // 실제 구현에서는 새로운 로그만 전송하도록 개선 필요
            List<LogEntry> recentLogs = loggingService.getRecentLogs(1);
            if (!recentLogs.isEmpty() && !sseEmitters.isEmpty()) {
                LogEntry latestLog = recentLogs.get(recentLogs.size() - 1);
                broadcastLogToEmitters(latestLog);
            }
        }, 1, 1, TimeUnit.SECONDS);
    }
}