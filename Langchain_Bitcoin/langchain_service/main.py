"""
비트코인 챗봇 LangChain 서비스
Spring Boot 백엔드와 연동되는 RAG 기반 챗봇 서비스

주요 기능:
- RAG (Retrieval-Augmented Generation) 파이프라인
- 실시간 비트코인 가격 조회
- 크립토 뉴스 벡터 검색
- LangChain Tools 기반 멀티모달 처리
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import asyncio

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="Crypto Chatbot LangChain Service",
    description="LangChain + RAG를 활용한 비트코인 챗봇 AI 서비스",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 요청/응답 모델 정의
class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str
    session_id: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    message: str
    session_id: str
    data_sources: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    intent: Optional[str] = None
    processing_method: Optional[str] = None
    analysis_depth: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class PipelineRequest(BaseModel):
    """파이프라인 요청 모델"""
    hours_back: int = 24

class SearchRequest(BaseModel):
    """뉴스 검색 요청 모델"""
    query: str
    limit: int = 10

# 전역 변수들
chatbot_agent = None
vector_db = None
news_pipeline = None

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 초기화"""
    global chatbot_agent, vector_db, news_pipeline
    
    logger.info("🚀 LangChain 서비스 초기화 중...")
    
    try:
        # 환경 변수 로드
        from dotenv import load_dotenv
        load_dotenv()
        
        # OpenAI API 키 확인
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("❌ OPENAI_API_KEY가 설정되지 않았습니다!")
            raise ValueError("OpenAI API 키가 필요합니다.")
        
        logger.info("✅ 환경변수 확인 완료")
        
        # 벡터 DB 초기화
        logger.info("🔧 벡터 서비스 초기화 중...")
        from langchain_service.services.vector_service import VectorService
        vector_db = VectorService()
        await vector_db.initialize()
        logger.info("✅ 벡터 서비스 초기화 완료")
        
        # Custom 챗봇 에이전트 초기화 (안정적)
        logger.info("🔥 Custom 챗봇 에이전트 초기화 중...")
        from langchain_service.services.custom_crypto_agent import CustomCryptoAgent
        chatbot_agent = CustomCryptoAgent(vector_db)
        await chatbot_agent.initialize()
        logger.info("✅ Custom 챗봇 에이전트 초기화 완료")
        
        # 뉴스 파이프라인 초기화
        try:
            logger.info("📰 뉴스 파이프라인 초기화 중...")
            from news_pipeline import NewsPipeline
            news_pipeline = NewsPipeline()
            logger.info("✅ 뉴스 파이프라인 초기화 완료")
        except Exception as pipeline_error:
            logger.warning(f"⚠️ 뉴스 파이프라인 초기화 실패 (일부 기능 제한): {pipeline_error}")
        
        logger.info("🎉 LangChain 서비스 초기화 완료!")
        
    except Exception as e:
        logger.error(f"💥 서비스 초기화 실패: {e}")
        logger.error("서비스가 정상적으로 작동하지 않을 수 있습니다.")
        # 완전히 중단하지 않고 계속 실행 (일부 기능은 제한됨)

@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    try:
        # 기본 상태
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "LangChain Crypto Chatbot",
            "version": "1.0.0"
        }
        
        # 벡터 DB 상태 확인
        if vector_db:
            try:
                db_status = await vector_db.health_check()
                status["vector_db"] = "healthy" if db_status else "unhealthy"
                
                # 데이터베이스 통계 추가
                stats = await vector_db.get_database_stats()
                if stats:
                    status["database_stats"] = stats
            except Exception as e:
                status["vector_db"] = f"error: {str(e)}"
        else:
            status["vector_db"] = "not_initialized"
            
        # 챗봇 에이전트 상태 확인
        if chatbot_agent:
            try:
                agent_status = await chatbot_agent.health_check()
                if isinstance(agent_status, dict):
                    status["chatbot_agent"] = agent_status
                else:
                    status["chatbot_agent"] = "healthy" if agent_status else "unhealthy"
            except Exception as e:
                status["chatbot_agent"] = f"error: {str(e)}"
        else:
            status["chatbot_agent"] = "not_initialized"
        
        # 전체 상태 평가
        if (status.get("vector_db") == "healthy" and 
            status.get("chatbot_agent") == "healthy"):
            status["overall_status"] = "fully_operational"
        elif (status.get("vector_db") != "not_initialized" or 
              status.get("chatbot_agent") != "not_initialized"):
            status["overall_status"] = "partially_operational"
        else:
            status["overall_status"] = "limited_functionality"
            
        logger.debug(f"🏥 상태 확인: {status['overall_status']}")
        return status
        
    except Exception as e:
        logger.error(f"❌ 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """채팅 처리 엔드포인트"""
    try:
        logger.info(f"💬 채팅 요청 수신: {request.message[:50]}...")
        
        # 챗봇 에이전트가 초기화되지 않은 경우
        if not chatbot_agent:
            # 기본 응답 제공 (제한된 기능)
            return ChatResponse(
                message="현재 AI 에이전트가 초기화되지 않아 기본 응답만 제공할 수 있습니다. 서버 관리자에게 문의해주세요.",
                session_id=request.session_id,
                data_sources=["fallback"],
                error="Agent not initialized"
            )
        
        # 메시지 처리
        response_data = await chatbot_agent.process_message(
            message=request.message,
            session_id=request.session_id,
            use_rag=request.use_rag
        )
        
        # 딕셔너리에서 ChatResponse 객체로 변환
        if isinstance(response_data, dict):
            response = ChatResponse(
                message=response_data.get('message', '응답을 생성할 수 없습니다.'),
                session_id=response_data.get('session_id', request.session_id),
                data_sources=response_data.get('data_sources'),
                confidence_score=response_data.get('confidence_score'),
                intent=response_data.get('intent'),
                processing_method=response_data.get('processing_method'),
                analysis_depth=response_data.get('analysis_depth'),
                timestamp=response_data.get('timestamp'),
                error=response_data.get('error')
            )
        else:
            # 이미 ChatResponse 객체인 경우
            response = response_data
        
        logger.info(f"✅ 채팅 응답 생성 완료: {len(response.message)}자")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 채팅 처리 중 오류: {e}")
        
        # 오류 응답 생성
        error_response = ChatResponse(
            message="죄송합니다. 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            session_id=request.session_id,
            error=str(e)
        )
        return error_response

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🤖 Crypto Chatbot LangChain Service",
        "version": "1.0.0",
        "status": "running",
        "description": "LangChain + RAG 기반 암호화폐 챗봇 서비스",
        "features": [
            "실시간 암호화폐 가격 조회",
            "벡터 기반 뉴스 검색",
            "Multi-Tool AI Agent",
            "세션별 대화 메모리"
        ],
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "docs": "GET /docs"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
async def get_stats():
    """서비스 통계 정보"""
    try:
        stats = {
            "service": "LangChain Crypto Chatbot",
            "timestamp": datetime.now().isoformat()
        }
        
        # 벡터 DB 통계
        if vector_db:
            db_stats = await vector_db.get_database_stats()
            stats["database"] = db_stats
        
        # 챗봇 에이전트 정보
        if chatbot_agent:
            stats["agent"] = {
                "tools_count": 6,  # Custom Agent는 6개 도구 사용
                "active_sessions": len(chatbot_agent.session_histories),
                "agent_type": "CustomCryptoAgent",
                "status": "operational"
            }
        else:
            stats["agent"] = {
                "status": "not_initialized"
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_available_tools():
    """사용 가능한 도구 목록"""
    try:
        if not chatbot_agent:
            return {
                "status": "no_tools_available",
                "message": "챗봇 에이전트가 초기화되지 않았습니다."
            }
        
        # Custom Agent의 도구 목록
        tools_info = [
            {
                "name": "crypto_news_search",
                "description": "암호화폐 관련 뉴스를 벡터 유사도 기반으로 검색합니다."
            },
            {
                "name": "latest_news_lookup", 
                "description": "최신 암호화폐 뉴스를 시간순으로 조회합니다."
            },
            {
                "name": "crypto_price_checker",
                "description": "개별 암호화폐의 실시간 가격을 조회합니다."
            },
            {
                "name": "multi_coin_price_checker",
                "description": "여러 암호화폐의 가격을 한번에 조회합니다."
            },
            {
                "name": "coinmarketcap_info",
                "description": "CoinMarketCap에서 시가총액 및 시장 정보를 조회합니다."
            },
            {
                "name": "database_stats",
                "description": "데이터베이스 통계 및 상태 정보를 조회합니다."
            }
        ]
        
        return {
            "tools_count": len(tools_info),
            "tools": tools_info,
            "agent_type": "CustomCryptoAgent",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 도구 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== 뉴스 파이프라인 관련 엔드포인트 =====

@app.post("/pipeline/run")
async def run_news_pipeline(request: PipelineRequest):
    """뉴스 파이프라인 실행"""
    try:
        if not news_pipeline:
            raise HTTPException(status_code=503, detail="뉴스 파이프라인이 초기화되지 않았습니다.")
        
        logger.info(f"📰 뉴스 파이프라인 실행 시작 (최근 {request.hours_back}시간)")
        
        result = news_pipeline.run_pipeline(hours_back=request.hours_back, use_cache=False)
        
        logger.info(f"✅ 뉴스 파이프라인 실행 완료: 수집={result.get('collected_count', 0)}, 처리={result.get('processed_count', 0)}, 저장={result.get('saved_count', 0)}")
        
        return {
            "success": True,
            "message": "뉴스 파이프라인 실행 완료",
            **result
        }
        
    except Exception as e:
        logger.error(f"❌ 뉴스 파이프라인 실행 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파이프라인 실행 실패: {str(e)}")

@app.post("/pipeline/incremental")
async def run_incremental_update(request: PipelineRequest):
    """증분 뉴스 업데이트"""
    try:
        if not news_pipeline:
            raise HTTPException(status_code=503, detail="뉴스 파이프라인이 초기화되지 않았습니다.")
        
        logger.info(f"🔄 증분 뉴스 업데이트 시작 (최근 {request.hours_back}시간)")
        
        result = news_pipeline.run_incremental_update(hours_back=request.hours_back)
        
        logger.info(f"✅ 증분 업데이트 완료: 수집={result.get('collected_count', 0)}, 처리={result.get('processed_count', 0)}, 저장={result.get('saved_count', 0)}")
        
        return {
            "success": True,
            "message": "증분 업데이트 완료",
            **result
        }
        
    except Exception as e:
        logger.error(f"❌ 증분 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=f"증분 업데이트 실패: {str(e)}")

@app.get("/pipeline/status")
async def get_pipeline_status():
    """뉴스 파이프라인 상태 조회"""
    try:
        if not news_pipeline:
            return {
                "success": False,
                "message": "뉴스 파이프라인이 초기화되지 않았습니다.",
                "services_initialized": False
            }
        
        status = news_pipeline.get_pipeline_status()
        
        return {
            "success": True,
            "message": "파이프라인 상태 조회 완료",
            **status
        }
        
    except Exception as e:
        logger.error(f"❌ 파이프라인 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@app.post("/news/search")
async def search_news(request: SearchRequest):
    """뉴스 검색 (벡터 유사도 기반)"""
    try:
        if not news_pipeline:
            raise HTTPException(status_code=503, detail="뉴스 파이프라인이 초기화되지 않았습니다.")
        
        logger.info(f"🔍 뉴스 검색: '{request.query}' (limit={request.limit})")
        
        results = news_pipeline.pgvector_service.search_similar_articles(
            query=request.query,
            limit=request.limit,
            similarity_threshold=0.2
        )
        
        logger.info(f"✅ 뉴스 검색 완료: {len(results)}개 결과")
        
        return {
            "success": True,
            "message": f"'{request.query}' 검색 완료",
            "query": request.query,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ 뉴스 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"뉴스 검색 실패: {str(e)}")

@app.get("/news/statistics")
async def get_news_statistics():
    """뉴스 통계 조회"""
    try:
        if not news_pipeline:
            raise HTTPException(status_code=503, detail="뉴스 파이프라인이 초기화되지 않았습니다.")
        
        stats = news_pipeline.pgvector_service.get_statistics()
        
        return {
            "success": True,
            "message": "뉴스 통계 조회 완료",
            **stats
        }
        
    except Exception as e:
        logger.error(f"❌ 뉴스 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@app.get("/news/recent")
async def get_recent_news(hours: int = 24, limit: int = 50):
    """최근 뉴스 조회"""
    try:
        if not news_pipeline:
            raise HTTPException(status_code=503, detail="뉴스 파이프라인이 초기화되지 않았습니다.")
        
        results = news_pipeline.pgvector_service.get_recent_articles(hours=hours, limit=limit)
        
        return {
            "success": True,
            "message": f"최근 {hours}시간 뉴스 조회 완료",
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ 최근 뉴스 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"최근 뉴스 조회 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌟 LangChain 서비스 시작...")
    print("=" * 60)
    print("🤖 Crypto Chatbot LangChain Service")
    print("📡 서버 주소: http://localhost:8001")
    print("📚 API 문서: http://localhost:8001/docs")
    print("🔧 서비스 상태: http://localhost:8001/health")
    print("📊 통계 정보: http://localhost:8001/stats")
    print("🛠️ 도구 목록: http://localhost:8001/tools")
    print("=" * 60)
    
    # 포트 8001이 사용 중인 경우 8002로 대체
    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    port = 8001
    if is_port_in_use(port):
        port = 8002
        print(f"⚠️ 포트 8001이 사용 중입니다. 포트 {port}로 시작합니다.")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 서비스가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"💥 서버 시작 실패: {e}")
