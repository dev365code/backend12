import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import sys
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from dataclasses import asdict

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class PgVectorService:
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 5435, 
                 database: str = "mydb",
                 user: str = "myuser", 
                 password: str = "mypassword"):
        """PgVector 서비스 초기화"""
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
        self.logger = logging.getLogger(__name__)
        
        # 임베딩 모델 초기화
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384  # all-MiniLM-L6-v2의 차원
        
        # 데이터베이스 연결 및 초기 설정
        self.init_database()
    
    def get_connection(self):
        """데이터베이스 연결 반환"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # pgvector 확장 활성화
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
                    # 뉴스 테이블 생성
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS crypto_news (
                            id SERIAL PRIMARY KEY,
                            title TEXT NOT NULL,
                            content TEXT,
                            summary TEXT,
                            url TEXT UNIQUE NOT NULL,
                            source TEXT,
                            published_date TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            keywords TEXT[],
                            sentiment VARCHAR(20),
                            embedding vector(384),
                            raw_data JSONB
                        );
                    """)
                    
                    # 인덱스 생성
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_crypto_news_embedding 
                        ON crypto_news USING ivfflat (embedding vector_cosine_ops) 
                        WITH (lists = 100);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_crypto_news_published_date 
                        ON crypto_news (published_date DESC);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_crypto_news_source 
                        ON crypto_news (source);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_crypto_news_sentiment 
                        ON crypto_news (sentiment);
                    """)
                    
                    conn.commit()
                    self.logger.info("Database initialized successfully")
                    
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """텍스트 임베딩 생성"""
        try:
            if not text.strip():
                return [0.0] * self.embedding_dimension
            
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            return [0.0] * self.embedding_dimension
    
    def insert_news_article(self, article_data: Dict[str, Any]) -> bool:
        """뉴스 기사 삽입"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 중복 확인
                    cur.execute("SELECT id FROM crypto_news WHERE url = %s", (article_data['url'],))
                    if cur.fetchone():
                        self.logger.info(f"Article already exists: {article_data['url']}")
                        return False
                    
                    # 임베딩 생성 (제목 + 요약 + 내용)
                    embedding_text = f"{article_data.get('title', '')} {article_data.get('summary', '')} {article_data.get('content', '')}"
                    embedding = self.generate_embedding(embedding_text)
                    
                    # 날짜 처리
                    published_date = article_data.get('published_date')
                    if isinstance(published_date, str):
                        try:
                            published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                        except:
                            published_date = datetime.now()
                    elif published_date is None:
                        published_date = datetime.now()
                    
                    # 데이터 삽입
                    cur.execute("""
                        INSERT INTO crypto_news 
                        (title, content, summary, url, source, published_date, 
                         keywords, sentiment, embedding, raw_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        article_data.get('title', ''),
                        article_data.get('content', ''),
                        article_data.get('summary', ''),
                        article_data['url'],
                        article_data.get('source', ''),
                        published_date,
                        article_data.get('keywords', []),
                        article_data.get('sentiment', 'neutral'),
                        embedding,
                        json.dumps(article_data.get('raw_data', {}))
                    ))
                    
                    conn.commit()
                    self.logger.info(f"Article inserted: {article_data.get('title', '')[:50]}...")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to insert article: {e}")
            return False
    
    def batch_insert_articles(self, articles: List[Dict[str, Any]]) -> int:
        """뉴스 기사 일괄 삽입"""
        success_count = 0
        
        for article in articles:
            if self.insert_news_article(article):
                success_count += 1
        
        self.logger.info(f"Successfully inserted {success_count}/{len(articles)} articles")
        return success_count
    
    def search_similar_articles(self, query: str, limit: int = 10, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """유사한 기사 검색"""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.generate_embedding(query)
            
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, summary, url, source, published_date, 
                               keywords, sentiment, created_at,
                               1 - (embedding <=> %s) as similarity
                        FROM crypto_news
                        WHERE 1 - (embedding <=> %s) > %s
                        ORDER BY embedding <=> %s
                        LIMIT %s
                    """, (query_embedding, query_embedding, similarity_threshold, query_embedding, limit))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            self.logger.error(f"Similar articles search failed: {e}")
            return []
    
    def get_recent_articles(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 기사 조회"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, summary, url, source, published_date, 
                               keywords, sentiment, created_at
                        FROM crypto_news
                        WHERE published_date >= NOW() - INTERVAL '%s hours'
                        ORDER BY published_date DESC
                        LIMIT %s
                    """, (hours, limit))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            self.logger.error(f"Recent articles query failed: {e}")
            return []
    
    def get_articles_by_sentiment(self, sentiment: str, limit: int = 20) -> List[Dict[str, Any]]:
        """감정별 기사 조회"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, summary, url, source, published_date, 
                               keywords, sentiment, created_at
                        FROM crypto_news
                        WHERE sentiment = %s
                        ORDER BY published_date DESC
                        LIMIT %s
                    """, (sentiment, limit))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            self.logger.error(f"Sentiment articles query failed: {e}")
            return []
    
    def get_articles_by_keywords(self, keywords: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """키워드별 기사 조회"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, summary, url, source, published_date, 
                               keywords, sentiment, created_at
                        FROM crypto_news
                        WHERE keywords && %s
                        ORDER BY published_date DESC
                        LIMIT %s
                    """, (keywords, limit))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            self.logger.error(f"Keyword articles query failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """뉴스 통계 조회"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 총 기사 수
                    cur.execute("SELECT COUNT(*) as total_articles FROM crypto_news")
                    total_articles = cur.fetchone()['total_articles']
                    
                    # 오늘 기사 수
                    cur.execute("""
                        SELECT COUNT(*) as today_articles 
                        FROM crypto_news 
                        WHERE DATE(published_date) = CURRENT_DATE
                    """)
                    today_articles = cur.fetchone()['today_articles']
                    
                    # 감정별 분포
                    cur.execute("""
                        SELECT sentiment, COUNT(*) as count 
                        FROM crypto_news 
                        GROUP BY sentiment
                    """)
                    sentiment_distribution = {row['sentiment']: row['count'] for row in cur.fetchall()}
                    
                    # 소스별 분포
                    cur.execute("""
                        SELECT source, COUNT(*) as count 
                        FROM crypto_news 
                        GROUP BY source 
                        ORDER BY count DESC 
                        LIMIT 10
                    """)
                    source_distribution = {row['source']: row['count'] for row in cur.fetchall()}
                    
                    return {
                        'total_articles': total_articles,
                        'today_articles': today_articles,
                        'sentiment_distribution': sentiment_distribution,
                        'source_distribution': source_distribution
                    }
                    
        except Exception as e:
            self.logger.error(f"Statistics query failed: {e}")
            return {}
    
    def delete_old_articles(self, days: int = 30) -> int:
        """오래된 기사 삭제"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM crypto_news 
                        WHERE published_date < NOW() - INTERVAL '%s days'
                    """, (days,))
                    
                    deleted_count = cur.rowcount
                    conn.commit()
                    
                    self.logger.info(f"Deleted {deleted_count} old articles")
                    return deleted_count
                    
        except Exception as e:
            self.logger.error(f"Failed to delete old articles: {e}")
            return 0

# 사용 예시
if __name__ == "__main__":
    service = PgVectorService()
    
    # 테스트용 샘플 데이터
    sample_article = {
        'title': '비트코인 가격 상승 전망',
        'content': '비트코인이 최근 기관 투자자들의 관심 증가로 인해 상승세를 보이고 있습니다.',
        'summary': '비트코인 가격이 기관 투자자 관심으로 상승세',
        'url': 'https://example.com/bitcoin-rise',
        'source': 'TestNews',
        'published_date': datetime.now().isoformat(),
        'keywords': ['bitcoin', 'btc', '상승', '기관투자자'],
        'sentiment': 'positive',
        'raw_data': {}
    }
    
    # 기사 삽입 테스트
    success = service.insert_news_article(sample_article)
    print(f"Article insertion: {'Success' if success else 'Failed'}")
    
    # 유사 기사 검색 테스트
    similar_articles = service.search_similar_articles('비트코인 가격')
    print(f"Found {len(similar_articles)} similar articles")
    
    # 통계 조회
    stats = service.get_statistics()
    print(f"Statistics: {stats}")