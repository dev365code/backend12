"""
이중 데이터베이스 서비스 
- 기사 요약: Docker PgVector (5435포트)
- 기사 본문: Localhost PostgreSQL (5432포트)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import numpy as np
from openai import OpenAI

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class DualDatabaseService:
    def __init__(self, 
                 # PgVector (요약 저장용)
                 pgvector_host: str = None,
                 pgvector_port: int = None,
                 pgvector_database: str = None,
                 pgvector_user: str = None, 
                 pgvector_password: str = None,
                 # PostgreSQL (본문 저장용) - 환경변수에서 읽기
                 postgres_host: str = None,
                 postgres_port: int = None,
                 postgres_database: str = None,
                 postgres_user: str = None,
                 postgres_password: str = None):
        """이중 데이터베이스 서비스 초기화"""
        
        # PgVector 연결 설정 (요약용) - 환경변수에서 읽기
        self.pgvector_params = {
            'host': pgvector_host or os.getenv('DB_HOST', 'localhost'),
            'port': pgvector_port or int(os.getenv('DB_PORT', 5435)),
            'database': pgvector_database or os.getenv('DB_NAME', 'mydb'),
            'user': pgvector_user or os.getenv('DB_USER', 'myuser'),
            'password': pgvector_password or os.getenv('DB_PASSWORD', 'mypassword')
        }
        
        # PostgreSQL 연결 설정 (본문용) - 환경변수에서 읽기
        self.postgres_params = {
            'host': postgres_host or os.getenv('POSTGRES_HOST', 'localhost'),
            'port': postgres_port or int(os.getenv('POSTGRES_PORT', 5432)),
            'database': postgres_database or os.getenv('POSTGRES_DB', 'postgres'),
            'user': postgres_user or os.getenv('POSTGRES_USER', 'leewooyong'),
            'password': postgres_password or os.getenv('POSTGRES_PASSWORD', '')
        }
        
        # 백업 연결 설정 (PostgreSQL 연결 실패 시) - PgVector DB 사용
        self.backup_postgres_params = {
            'host': self.pgvector_params['host'],
            'port': self.pgvector_params['port'],
            'database': self.pgvector_params['database'],
            'user': self.pgvector_params['user'],
            'password': self.pgvector_params['password']
        }
        
        self.logger = logging.getLogger(__name__)
        
        # OpenAI 임베딩 모델 초기화
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_dimension = 1536
        
        # 데이터베이스 초기화
        self.init_databases()
    
    def get_pgvector_connection(self):
        """PgVector 데이터베이스 연결 반환"""
        try:
            conn = psycopg2.connect(**self.pgvector_params)
            return conn
        except Exception as e:
            self.logger.error(f"PgVector connection failed: {e}")
            raise
    
    def get_postgres_connection(self):
        """PostgreSQL 데이터베이스 연결 반환"""
        try:
            conn = psycopg2.connect(**self.postgres_params)
            return conn
        except Exception as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def init_databases(self):
        """두 데이터베이스 초기화"""
        self.init_pgvector_db()
        self.init_postgres_db()
    
    def init_pgvector_db(self):
        """PgVector 데이터베이스 초기화 (요약 저장용)"""
        try:
            with self.get_pgvector_connection() as conn:
                with conn.cursor() as cur:
                    # pgvector 확장 활성화
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
                    # 뉴스 요약 테이블 (벡터 검색용)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS crypto_news_summary (
                            id SERIAL PRIMARY KEY,
                            title TEXT NOT NULL,
                            summary TEXT,
                            url TEXT UNIQUE NOT NULL,
                            source TEXT,
                            published_date TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            keywords TEXT[],
                            sentiment VARCHAR(20),
                            embedding vector(1536),
                            metadata JSONB
                        );
                    """)
                    
                    # 벡터 유사도 검색을 위한 IVFFlat 인덱스 생성
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_summary_embedding 
                        ON crypto_news_summary 
                        USING ivfflat (embedding vector_cosine_ops) 
                        WITH (lists = 100);
                    """)
                    self.logger.info("Vector IVFFlat index created successfully")
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_summary_published_date 
                        ON crypto_news_summary (published_date DESC);
                    """)
                    
                    conn.commit()
                    self.logger.info("PgVector database initialized successfully")
                    
        except Exception as e:
            self.logger.error(f"PgVector database initialization failed: {e}")
            raise
    
    def init_postgres_db(self):
        """PostgreSQL 데이터베이스 초기화 (본문 저장용)"""
        try:
            with self.get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    # 뉴스 본문 테이블
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS crypto_news_content (
                            id SERIAL PRIMARY KEY,
                            url TEXT UNIQUE NOT NULL,
                            title TEXT NOT NULL,
                            content TEXT,
                            raw_html TEXT,
                            published_date TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            source TEXT,
                            raw_data JSONB
                        );
                    """)
                    
                    # 인덱스 생성
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_content_url 
                        ON crypto_news_content (url);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_content_published_date 
                        ON crypto_news_content (published_date DESC);
                    """)
                    
                    conn.commit()
                    self.logger.info("PostgreSQL database initialized successfully")
                    
        except Exception as e:
            self.logger.error(f"PostgreSQL database initialization failed: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """OpenAI 텍스트 임베딩 생성"""
        try:
            if not text.strip():
                return [0.0] * self.embedding_dimension
            
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"OpenAI embedding generation failed: {e}")
            return [0.0] * self.embedding_dimension
    
    def insert_news_article(self, article_data: Dict[str, Any]) -> bool:
        """뉴스 기사를 두 데이터베이스에 분리 저장"""
        url = article_data['url']
        success_summary = False
        success_content = False
        
        try:
            # 1. 요약을 PgVector에 저장
            with self.get_pgvector_connection() as conn:
                with conn.cursor() as cur:
                    # 중복 확인
                    cur.execute("SELECT id FROM crypto_news_summary WHERE url = %s", (url,))
                    if not cur.fetchone():
                        # 임베딩 생성 (제목 + 요약)
                        embedding_text = f"{article_data.get('title', '')} {article_data.get('summary', '')}"
                        embedding = self.generate_embedding(embedding_text)
                        
                        # 날짜 처리
                        published_date = self._process_date(article_data.get('published_date'))
                        
                        # 요약 데이터 삽입
                        cur.execute("""
                            INSERT INTO crypto_news_summary 
                            (title, summary, url, source, published_date, 
                             keywords, sentiment, embedding, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector, %s)
                        """, (
                            article_data.get('title', ''),
                            article_data.get('summary', ''),
                            url,
                            article_data.get('source', ''),
                            published_date,
                            article_data.get('keywords', []),
                            article_data.get('sentiment', 'neutral'),
                            embedding,
                            json.dumps({
                                'summary_length': len(article_data.get('summary', '')),
                                'keyword_count': len(article_data.get('keywords', []))
                            })
                        ))
                        
                        conn.commit()
                        success_summary = True
                        self.logger.info(f"Summary saved to PgVector: {article_data.get('title', '')[:50]}...")
            
            # 2. 본문을 PostgreSQL에 저장 (백업으로 PgVector 사용)
            try:
                with self.get_postgres_connection() as conn:
                    with conn.cursor() as cur:
                        # 중복 확인
                        cur.execute("SELECT id FROM crypto_news_content WHERE url = %s", (url,))
                        existing = cur.fetchone()
                        
                        if not existing:
                            # 날짜 처리
                            published_date = self._process_date(article_data.get('published_date'))
                            
                            # 본문 데이터 삽입
                            cur.execute("""
                                INSERT INTO crypto_news_content 
                                (url, title, content, raw_html, published_date, source, raw_data)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                url,
                                article_data.get('title', ''),
                                article_data.get('content', ''),
                                article_data.get('raw_html', ''),
                                published_date,
                                article_data.get('source', ''),
                                json.dumps(article_data.get('raw_data', {}))
                            ))
                            
                            conn.commit()
                            success_content = True
                            self.logger.info(f"Content saved to PostgreSQL: {article_data.get('title', '')[:50]}...")
                        else:
                            # 중복된 URL이므로 성공으로 처리
                            success_content = True
                            self.logger.info(f"Content already exists in PostgreSQL (skipped): {article_data.get('title', '')[:50]}...")
            except Exception as postgres_error:
                self.logger.warning(f"PostgreSQL 저장 실패, 백업 사용: {postgres_error}")
                # 백업: PgVector 컨테이너의 별도 DB 사용
                try:
                    backup_conn = psycopg2.connect(**self.backup_postgres_params)
                    with backup_conn:
                        with backup_conn.cursor() as cur:
                            cur.execute("SELECT id FROM crypto_news_content WHERE url = %s", (url,))
                            if not cur.fetchone():
                                published_date = self._process_date(article_data.get('published_date'))
                                cur.execute("""
                                    INSERT INTO crypto_news_content 
                                    (url, title, content, raw_html, published_date, source, raw_data)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    url,
                                    article_data.get('title', ''),
                                    article_data.get('content', ''),
                                    article_data.get('raw_html', ''),
                                    published_date,
                                    article_data.get('source', ''),
                                    json.dumps(article_data.get('raw_data', {}))
                                ))
                                backup_conn.commit()
                                success_content = True
                                self.logger.info(f"Content saved to backup DB: {article_data.get('title', '')[:50]}...")
                    backup_conn.close()
                except Exception as backup_error:
                    self.logger.error(f"백업 저장도 실패: {backup_error}")
            
            return success_summary and success_content
                    
        except Exception as e:
            self.logger.error(f"Failed to insert article: {e}")
            return False
    
    def _process_date(self, published_date):
        """날짜 처리 헬퍼 함수"""
        if isinstance(published_date, str):
            try:
                return datetime.fromisoformat(published_date.replace('Z', '+00:00'))
            except:
                return datetime.now()
        elif published_date is None:
            return datetime.now()
        return published_date
    
    def search_similar_articles(self, query: str, limit: int = 10, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """유사한 기사 검색 (PgVector에서)"""
        try:
            query_embedding = self.generate_embedding(query)
            
            with self.get_pgvector_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, summary, url, source, published_date, 
                               keywords, sentiment, created_at,
                               1 - (embedding <=> %s::vector) as similarity
                        FROM crypto_news_summary
                        WHERE 1 - (embedding <=> %s::vector) > %s
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (query_embedding, query_embedding, similarity_threshold, query_embedding, limit))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            self.logger.error(f"Similar articles search failed: {e}")
            return []
    
    def get_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """URL로 기사 본문 조회 (PostgreSQL에서)"""
        try:
            with self.get_postgres_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM crypto_news_content WHERE url = %s
                    """, (url,))
                    
                    result = cur.fetchone()
                    return dict(result) if result else None
                    
        except Exception as e:
            self.logger.error(f"Content retrieval failed: {e}")
            return None
    
    def get_recent_articles(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 기사 조회 (요약만)"""
        try:
            with self.get_pgvector_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, summary, url, source, published_date, 
                               keywords, sentiment, created_at
                        FROM crypto_news_summary
                        WHERE published_date >= NOW() - INTERVAL '%s hours'
                        ORDER BY published_date DESC
                        LIMIT %s
                    """, (hours, limit))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            self.logger.error(f"Recent articles query failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """양쪽 데이터베이스 통계 조회"""
        try:
            stats = {}
            
            # PgVector 통계
            with self.get_pgvector_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT COUNT(*) as summary_count FROM crypto_news_summary")
                    stats['summary_count'] = cur.fetchone()['summary_count']
            
            # PostgreSQL 통계
            with self.get_postgres_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT COUNT(*) as content_count FROM crypto_news_content")
                    stats['content_count'] = cur.fetchone()['content_count']
            
            return stats
                    
        except Exception as e:
            self.logger.error(f"Statistics query failed: {e}")
            return {}
    
    def batch_insert_articles(self, articles: List[Dict[str, Any]]) -> int:
        """뉴스 기사 일괄 삽입"""
        success_count = 0
        
        for article in articles:
            if self.insert_news_article(article):
                success_count += 1
        
        self.logger.info(f"Successfully inserted {success_count}/{len(articles)} articles to dual databases")
        return success_count

# 사용 예시
if __name__ == "__main__":
    service = DualDatabaseService()
    
    # 테스트용 샘플 데이터
    sample_article = {
        'title': '비트코인 가격 상승 전망',
        'content': '비트코인이 최근 기관 투자자들의 관심 증가로 인해 상승세를 보이고 있습니다. 전문가들은 이러한 추세가 계속될 것으로 예상한다고 밝혔습니다.',
        'summary': '비트코인 가격이 기관 투자자 관심으로 상승세',
        'url': 'https://example.com/bitcoin-rise-dual',
        'source': 'TestNews',
        'published_date': datetime.now().isoformat(),
        'keywords': ['bitcoin', 'btc', '상승', '기관투자자'],
        'sentiment': 'positive',
        'raw_data': {}
    }
    
    # 기사 삽입 테스트
    success = service.insert_news_article(sample_article)
    print(f"Article insertion: {'Success' if success else 'Failed'}")
    
    # 통계 조회
    stats = service.get_statistics()
    print(f"Statistics: {stats}")