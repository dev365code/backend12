"""
벡터 데이터베이스 서비스
기존 vector_db.py와 crypto_test.py 코드를 활용하여 구현
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from openai import OpenAI

logger = logging.getLogger(__name__)

class VectorService:
    """벡터 데이터베이스 서비스 클래스"""
    
    def __init__(self):
        """초기화"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5433)),
            'user': os.getenv('DB_USER', 'myuser'),
            'password': os.getenv('DB_PASSWORD', 'mypassword'),
            'dbname': os.getenv('DB_NAME', 'mydb')
        }
        
        # OpenAI 클라이언트 초기화
        self.openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            logger.info("✅ OpenAI 클라이언트 초기화 완료")
        else:
            logger.error("❌ OpenAI API 키가 설정되지 않았습니다")
    
    async def initialize(self):
        """서비스 초기화"""
        try:
            logger.info("🔧 벡터 서비스 초기화 중...")
            
            # 데이터베이스 연결 테스트
            await self._test_db_connection()
            
            # pgvector 확장 확인
            await self._check_pgvector_extension()
            
            logger.info("✅ 벡터 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 벡터 서비스 초기화 실패: {e}")
            raise
    
    async def _test_db_connection(self):
        """데이터베이스 연결 테스트"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            logger.info(f"🐘 PostgreSQL 연결 성공: {version.split(',')[0]}")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            raise
    
    async def _check_pgvector_extension(self):
        """pgvector 확장 확인"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # pgvector 확장 확인
            cur.execute("SELECT * FROM pg_extension WHERE extname='vector';")
            result = cur.fetchone()
            
            if result:
                logger.info("✅ pgvector 확장 확인됨")
            else:
                logger.warning("⚠️ pgvector 확장이 설치되지 않았습니다")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ pgvector 확장 확인 실패: {e}")
            raise
    
    async def vector_search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        벡터 유사도 검색 (DualDatabaseService 연동)
        
        Args:
            query: 검색 쿼리
            limit: 결과 개수 제한
            
        Returns:
            검색 결과 리스트
        """
        try:
            logger.debug(f"🔍 벡터 검색 실행: {query}")
            
            # DualDatabaseService 사용
            from .dual_db_service import DualDatabaseService
            dual_db = DualDatabaseService()
            
            # 벡터 검색 실행
            search_results = dual_db.search_similar_articles(
                query=query, 
                limit=limit, 
                similarity_threshold=0.2
            )
            
            # 결과 형식 변환
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    'id': result.get('id'),
                    'title': result.get('title'),
                    'content': result.get('summary'),  # summary를 content로 사용
                    'source': result.get('source'),
                    'published_date': result.get('published_date').isoformat() if result.get('published_date') else None,
                    'similarity': float(result.get('similarity', 0))
                })
            
            logger.debug(f"✅ 벡터 검색 완료: {len(formatted_results)}개 결과")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 벡터 검색 실패: {e}")
            return []
    
    async def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """
        최신 뉴스 조회 (DualDatabaseService 연동)
        
        Args:
            limit: 결과 개수 제한
            
        Returns:
            최신 뉴스 리스트
        """
        try:
            logger.debug(f"📰 최신 뉴스 조회: {limit}개")
            
            # DualDatabaseService 사용
            from .dual_db_service import DualDatabaseService
            dual_db = DualDatabaseService()
            
            # 최근 뉴스 조회 (24시간)
            news_results = dual_db.get_recent_articles(hours=24, limit=limit)
            
            # 결과 형식 변환
            formatted_results = []
            for result in news_results:
                formatted_results.append({
                    'id': result.get('id'),
                    'title': result.get('title'),
                    'content': result.get('summary'),  # summary를 content로 사용
                    'source': result.get('source'),
                    'published_date': result.get('published_date').isoformat() if result.get('published_date') else None,
                    'created_at': result.get('created_at').isoformat() if result.get('created_at') else None
                })
            
            logger.debug(f"✅ 최신 뉴스 조회 완료: {len(formatted_results)}개")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 최신 뉴스 조회 실패: {e}")
            return []
    
    async def get_database_stats(self) -> Dict:
        """
        데이터베이스 통계 정보 조회 (DualDatabaseService 연동)
        
        Returns:
            데이터베이스 통계 딕셔너리
        """
        try:
            # DualDatabaseService 사용
            from .dual_db_service import DualDatabaseService
            dual_db = DualDatabaseService()
            
            # 통계 조회
            stats = dual_db.get_statistics()
            
            result = {
                'total_news': stats.get('summary_count', 0),
                'news_with_embedding': stats.get('summary_count', 0),
                'news_without_embedding': 0,
                'embedding_coverage': 100.0 if stats.get('summary_count', 0) > 0 else 0.0,
                'content_count': stats.get('content_count', 0)
            }
            
            logger.debug(f"📊 데이터베이스 통계: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 통계 조회 실패: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """
        서비스 상태 확인
        
        Returns:
            서비스 정상 여부
        """
        try:
            # 데이터베이스 연결 확인
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.fetchone()
            cur.close()
            conn.close()
            
            # OpenAI 클라이언트 확인
            if not self.openai_client:
                return False
            
            logger.debug("✅ 벡터 서비스 상태 정상")
            return True
            
        except Exception as e:
            logger.error(f"❌ 벡터 서비스 상태 확인 실패: {e}")
            return False
