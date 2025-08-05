"""
통합 데이터베이스 연결 관리자
연결 풀링, 캐싱, 예외 처리를 통합 관리
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncpg
import redis
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """뉴스 기사 데이터 모델"""
    id: Optional[int] = None
    title: str = ""
    summary: str = ""
    content: str = ""
    url: str = ""
    source: str = ""
    published_date: datetime = None
    keywords: List[str] = None
    sentiment: str = "neutral"
    relevance_score: float = 0.0
    embedding: List[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        if self.published_date:
            data['published_date'] = self.published_date.isoformat()
        return data

class DatabaseManager:
    """통합 데이터베이스 연결 관리자"""
    
    def __init__(self):
        self.pgvector_pool: Optional[asyncpg.Pool] = None
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = 300  # 5분 캐시
        
        # DB 설정
        self.pgvector_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5435)),
            'database': os.getenv('DB_NAME', 'mydb'),
            'user': os.getenv('DB_USER', 'myuser'),
            'password': os.getenv('DB_PASSWORD', 'mypassword'),
            'min_size': 5,
            'max_size': 20
        }
        
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'leewooyong'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
            'min_size': 5,
            'max_size': 20
        }
        
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        try:
            logger.info("🔧 통합 데이터베이스 매니저 초기화 중...")
            
            # PgVector 연결 풀 생성
            self.pgvector_pool = await asyncpg.create_pool(**self.pgvector_config)
            logger.info("✅ PgVector 연결 풀 생성 완료")
            
            # PostgreSQL 연결 풀 생성
            try:
                self.postgres_pool = await asyncpg.create_pool(**self.postgres_config)
                logger.info("✅ PostgreSQL 연결 풀 생성 완료")
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL 연결 실패, PgVector만 사용: {e}")
                self.postgres_pool = None
            
            # Redis 연결
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # 연결 테스트
                self.redis_client.ping()
                logger.info("✅ Redis 연결 완료")
            except Exception as e:
                logger.warning(f"⚠️ Redis 연결 실패, 캐시 비활성화: {e}")
                self.redis_client = None
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 매니저 초기화 실패: {e}")
            raise
    
    async def close(self):
        """연결 풀 정리"""
        if self.pgvector_pool:
            await self.pgvector_pool.close()
        if self.postgres_pool:
            await self.postgres_pool.close()
        if self.redis_client:
            self.redis_client.close()
    
    @asynccontextmanager
    async def get_pgvector_connection(self):
        """PgVector 연결 컨텍스트 매니저"""
        if not self.pgvector_pool:
            raise RuntimeError("PgVector 연결 풀이 초기화되지 않았습니다")
        
        conn = await self.pgvector_pool.acquire()
        try:
            yield conn
        finally:
            await self.pgvector_pool.release(conn)
    
    @asynccontextmanager
    async def get_postgres_connection(self):
        """PostgreSQL 연결 컨텍스트 매니저"""
        if not self.postgres_pool:
            # 폴백: PgVector 사용
            async with self.get_pgvector_connection() as conn:
                yield conn
            return
                
        conn = await self.postgres_pool.acquire()
        try:
            yield conn
        finally:
            await self.postgres_pool.release(conn)
    
    def get_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """캐시 키 생성"""
        import hashlib
        params_str = json.dumps(params, sort_keys=True, default=str)
        hash_str = hashlib.md5(params_str.encode()).hexdigest()[:10]
        return f"{prefix}:{hash_str}"
    
    async def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """캐시에서 결과 조회"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.debug(f"캐시 조회 실패: {e}")
        return None
    
    async def set_cached_result(self, cache_key: str, result: Any, ttl: int = None):
        """결과를 캐시에 저장"""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.cache_ttl
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str, ensure_ascii=False)
            )
        except Exception as e:
            logger.debug(f"캐시 저장 실패: {e}")
    
    async def search_news_advanced(
        self, 
        query: str, 
        limit: int = 10,
        use_vector_search: bool = True,
        similarity_threshold: float = 0.3
    ) -> List[NewsArticle]:
        """고급 뉴스 검색 (벡터 + 키워드 하이브리드)"""
        
        # 캐시 확인
        cache_key = self.get_cache_key("news_search", {
            "query": query, 
            "limit": limit,
            "use_vector": use_vector_search,
            "threshold": similarity_threshold
        })
        
        cached_result = await self.get_cached_result(cache_key)
        if cached_result:
            logger.debug(f"캐시에서 뉴스 검색 결과 반환: {len(cached_result)}개")
            return [NewsArticle(**article) for article in cached_result]
        
        try:
            async with self.get_pgvector_connection() as conn:
                results = []
                
                if use_vector_search:
                    # 벡터 검색 시도
                    try:
                        # OpenAI 임베딩 생성
                        from openai import OpenAI
                        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                        
                        embedding_response = client.embeddings.create(
                            model="text-embedding-ada-002",
                            input=query
                        )
                        query_embedding = embedding_response.data[0].embedding
                        
                        # 벡터 검색 실행
                        vector_query = """
                            SELECT id, title, summary, url, source, published_date,
                                   1 - (embedding <=> $1::vector) as similarity_score
                            FROM crypto_news 
                            WHERE embedding IS NOT NULL
                            ORDER BY embedding <=> $1::vector
                            LIMIT $2
                        """
                        
                        rows = await conn.fetch(vector_query, query_embedding, limit)
                        
                        for row in rows:
                            if row['similarity_score'] >= similarity_threshold:
                                article = NewsArticle(
                                    id=row['id'],
                                    title=row['title'],
                                    summary=row['summary'] or "",
                                    url=row['url'],
                                    source=row['source'],
                                    published_date=row['published_date'],
                                    relevance_score=float(row['similarity_score'])
                                )
                                results.append(article)
                        
                        logger.info(f"벡터 검색 완료: {len(results)}개 결과")
                        
                    except Exception as vector_error:
                        logger.warning(f"벡터 검색 실패, 키워드 검색으로 폴백: {vector_error}")
                        use_vector_search = False
                
                # 벡터 검색 실패 또는 결과 부족 시 키워드 검색
                if not use_vector_search or len(results) < limit // 2:
                    keyword_query = """
                        SELECT id, title, summary, url, source, published_date,
                               CASE 
                                   WHEN title ILIKE $1 THEN 0.9
                                   WHEN summary ILIKE $1 THEN 0.7
                                   WHEN title ILIKE $2 OR summary ILIKE $2 THEN 0.5
                                   ELSE 0.3
                               END as relevance_score
                        FROM crypto_news 
                        WHERE title ILIKE $2 OR summary ILIKE $2
                        ORDER BY relevance_score DESC, published_date DESC
                        LIMIT $3
                    """
                    
                    exact_pattern = f"%{query}%"
                    broad_pattern = f"%{' '.join(query.split()[:2])}%"
                    
                    keyword_rows = await conn.fetch(
                        keyword_query, 
                        exact_pattern, 
                        broad_pattern, 
                        limit - len(results)
                    )
                    
                    for row in keyword_rows:
                        # 중복 제거
                        if not any(r.id == row['id'] for r in results):
                            article = NewsArticle(
                                id=row['id'],
                                title=row['title'],
                                summary=row['summary'] or "",
                                url=row['url'],
                                source=row['source'],
                                published_date=row['published_date'],
                                relevance_score=float(row['relevance_score'])
                            )
                            results.append(article)
                    
                    logger.info(f"키워드 검색 추가: 총 {len(results)}개 결과")
                
                # 관련도 순으로 정렬
                results.sort(key=lambda x: x.relevance_score, reverse=True)
                
                # 캐시에 저장
                cache_data = [article.to_dict() for article in results]
                await self.set_cached_result(cache_key, cache_data)
                
                return results[:limit]
                
        except Exception as e:
            logger.error(f"고급 뉴스 검색 실패: {e}")
            return []
    
    async def get_recent_news(self, hours: int = 24, limit: int = 10) -> List[NewsArticle]:
        """최근 뉴스 조회"""
        cache_key = self.get_cache_key("recent_news", {"hours": hours, "limit": limit})
        
        cached_result = await self.get_cached_result(cache_key)
        if cached_result:
            return [NewsArticle(**article) for article in cached_result]
        
        try:
            async with self.get_pgvector_connection() as conn:
                since_time = datetime.now() - timedelta(hours=hours)
                
                query = """
                    SELECT id, title, summary, url, source, published_date
                    FROM crypto_news 
                    WHERE published_date >= $1
                    ORDER BY published_date DESC
                    LIMIT $2
                """
                
                rows = await conn.fetch(query, since_time, limit)
                
                results = []
                for row in rows:
                    article = NewsArticle(
                        id=row['id'],
                        title=row['title'],
                        summary=row['summary'] or "",
                        url=row['url'],
                        source=row['source'],
                        published_date=row['published_date'],
                        relevance_score=0.8
                    )
                    results.append(article)
                
                # 캐시에 저장
                cache_data = [article.to_dict() for article in results]
                await self.set_cached_result(cache_key, cache_data, ttl=120)  # 2분 캐시
                
                return results
                
        except Exception as e:
            logger.error(f"최근 뉴스 조회 실패: {e}")
            return []
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계 조회"""
        cache_key = "db_stats"
        cached_result = await self.get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        try:
            async with self.get_pgvector_connection() as conn:
                stats_query = """
                    SELECT 
                        COUNT(*) as total_news,
                        COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as news_with_embedding,
                        COUNT(CASE WHEN published_date >= NOW() - INTERVAL '24 hours' THEN 1 END) as news_24h,
                        COUNT(CASE WHEN published_date >= NOW() - INTERVAL '7 days' THEN 1 END) as news_7d
                    FROM crypto_news
                """
                
                row = await conn.fetchrow(stats_query)
                
                stats = {
                    'total_news': row['total_news'],
                    'news_with_embedding': row['news_with_embedding'],
                    'news_24h': row['news_24h'],
                    'news_7d': row['news_7d'],
                    'embedding_coverage': (row['news_with_embedding'] / max(row['total_news'], 1)) * 100,
                    'last_updated': datetime.now().isoformat()
                }
                
                await self.set_cached_result(cache_key, stats, ttl=600)  # 10분 캐시
                return stats
                
        except Exception as e:
            logger.error(f"데이터베이스 통계 조회 실패: {e}")
            return {}

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()