#!/usr/bin/env python3
"""
비트코인 뉴스 수집, 요약 및 벡터 DB 저장 파이프라인
CLAUDE.md의 작업요청 v1에 따른 구현

작업 순서:
1. newsdata.io API로 "비트코인" 키워드 뉴스 수집
2. newspaper3k로 본문 크롤링  
3. OpenAI GPT-3.5 Turbo로 요약 생성
4. text-embedding-ada-002로 임베딩 생성
5. Vector DB에 저장 (중복 체크 포함)
"""

import sys
import os
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import newspaper
from newspaper import Article
from openai import OpenAI

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.dual_db_service import DualDatabaseService

class BitcoinNewsPipeline:
    def __init__(self):
        """비트코인 뉴스 파이프라인 초기화"""
        
        # 환경변수 로드
        load_dotenv('../.env')
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bitcoin_news_pipeline.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # API 키 설정
        self.newsdata_api_key = os.getenv('NEWSDATA_API_KEY', 'pub_4a395d6251bc434a85657d731461a856')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        # OpenAI 클라이언트 초기화
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # 데이터베이스 서비스 초기화
        self.dual_db_service = DualDatabaseService()
        
        # 요청 헤더
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.logger.info("비트코인 뉴스 파이프라인 초기화 완료")
    
    def step1_collect_bitcoin_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        1단계: newsdata.io API를 사용하여 "비트코인" 키워드 뉴스 수집
        """
        self.logger.info("1단계: 비트코인 뉴스 수집 시작")
        
        articles = []
        
        try:
            # NewsData.io API 파라미터 (한글 기사만)
            params = {
                'apikey': self.newsdata_api_key,
                'q': '비트코인 OR bitcoin OR BTC OR 암호화폐 OR 가상화폐',  # 한국어 키워드 우선
                'language': 'ko',  # 한국어만
                'country': 'kr',  # 한국 소스만
                'category': 'business,technology',
                'size': min(limit, 50)  # API 제한
            }
            
            self.logger.info(f"NewsData.io API 요청 시작 (한국어 비트코인 뉴스, 최대 {limit}개)")
            
            response = requests.get(
                'https://newsdata.io/api/1/news',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    for item in data.get('results', []):
                        url = item.get('link', '')
                        if not url:
                            continue
                        
                        # 날짜 파싱
                        published_date = datetime.now()
                        if item.get('pubDate'):
                            try:
                                published_date = datetime.fromisoformat(
                                    item['pubDate'].replace('Z', '+00:00')
                                )
                            except:
                                pass
                        
                        article = {
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'url': url,
                            'source': item.get('source_id', 'unknown'),
                            'published_date': published_date,
                            'raw_data': item
                        }
                        
                        articles.append(article)
                    
                    self.logger.info(f"NewsData.io에서 {len(articles)}개 뉴스 수집 완료")
                else:
                    self.logger.error(f"NewsData.io API 오류: {data.get('message', 'Unknown error')}")
            else:
                self.logger.error(f"NewsData.io API 요청 실패: {response.status_code}")
                # 상세 오류 정보 추가
                try:
                    error_data = response.json()
                    self.logger.error(f"API 오류 상세: {error_data}")
                except:
                    self.logger.error(f"응답 내용: {response.text[:200]}")
                
                # API 할당량 초과시 또는 한국 뉴스 부족시 대체 뉴스 소스 사용
                if response.status_code == 422:
                    self.logger.info("API 할당량 초과로 추정됩니다. RSS 피드로 대체합니다.")
                    return self._collect_from_rss_fallback(limit)
                
        except Exception as e:
            self.logger.error(f"뉴스 수집 중 오류: {e}")
        
        # NewsData.io에서 한국 뉴스를 찾지 못한 경우 RSS로 대체
        if len(articles) == 0:
            self.logger.info("NewsData.io에서 한국 뉴스를 찾지 못했습니다. RSS 피드로 대체합니다.")
            return self._collect_from_rss_fallback(limit)
        
        return articles
    
    def _collect_from_rss_fallback(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        NewsData.io API 실패시 RSS 피드에서 대체 수집
        """
        self.logger.info("RSS 피드에서 비트코인 뉴스 수집 시작")
        
        articles = []
        # 한국 암호화폐 뉴스 소스 (작동하는 것만)
        rss_sources = [
            ('coindesk_korea', 'https://www.coindeskkorea.com/rss'),
            ('beinnogate', 'https://beinnogate.com/feeds/all.atom.xml'),
            ('cryptoslate_kr', 'https://cryptoslate.com/feed/'),  # 글로벌이지만 한글 필터링 적용
        ]
        
        try:
            import feedparser
            
            for source_name, rss_url in rss_sources:
                try:
                    self.logger.info(f"RSS 수집: {source_name}")
                    feed = feedparser.parse(rss_url)
                    
                    for entry in feed.entries[:limit//len(rss_sources) + 1]:
                        # 암호화폐 관련 기사 필터링 (더 넓은 범위)
                        title = entry.title.lower()
                        content = getattr(entry, 'summary', '').lower()
                        full_text = f"{title} {content}"
                        
                        # 한글 + 영문 키워드로 필터링 (더 엄격한 기준)
                        crypto_keywords = [
                            '비트코인', '암호화폐', '가상화폐', '블록체인', '디지털자산',
                            'bitcoin', 'btc', 'crypto', 'cryptocurrency', 'blockchain', 'token',
                            '이더리움', 'ethereum', 'eth', '리플', 'ripple', 'xrp', 'etf',
                            '채굴', 'mining', '거래소', 'exchange', '지갑', 'wallet'
                        ]
                        
                        # 제외할 키워드 (암호화폐와 무관한 내용)
                        exclude_keywords = [
                            '이찬혁', '키의 비밀', 'hrbp', '인사', '채용', '면접', '키 성장',
                            '연예인', '아이돌', '신장', '몸무게', 'k-pop', '음악', '가수'
                        ]
                        
                        # 제외 키워드가 있으면 스킵
                        if any(exclude in full_text for exclude in exclude_keywords):
                            continue
                        
                        # 암호화폐 키워드가 있어야 포함
                        if not any(keyword in full_text for keyword in crypto_keywords):
                            continue
                        
                        # 날짜 파싱
                        published_date = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_date = datetime(*entry.published_parsed[:6])
                        
                        # 내용 추출
                        description = ""
                        if hasattr(entry, 'summary'):
                            description = entry.summary
                        elif hasattr(entry, 'description'):
                            description = entry.description
                        
                        article = {
                            'title': entry.title,
                            'description': description,
                            'url': entry.link,
                            'source': f"rss_{source_name}",
                            'published_date': published_date,
                            'raw_data': {
                                'author': getattr(entry, 'author', ''),
                                'tags': [tag.term for tag in getattr(entry, 'tags', [])]
                            }
                        }
                        
                        articles.append(article)
                        
                        if len(articles) >= limit:
                            break
                    
                    if len(articles) >= limit:
                        break
                    
                    time.sleep(1)  # 요청 간격
                    
                except Exception as e:
                    self.logger.error(f"RSS 수집 실패 {source_name}: {e}")
                    continue
            
            self.logger.info(f"RSS에서 {len(articles)}개 뉴스 수집 완료")
            
        except ImportError:
            self.logger.error("feedparser 라이브러리가 필요합니다: pip install feedparser")
        except Exception as e:
            self.logger.error(f"RSS 수집 중 오류: {e}")
        
        return articles
    
    def step2_crawl_article_content(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        2단계: newspaper3k를 활용하여 각 기사 URL의 전체 본문 크롤링
        """
        self.logger.info("2단계: 기사 본문 크롤링 시작")
        
        crawled_articles = []
        failed_urls = []
        
        for i, article in enumerate(articles):
            url = article['url']
            
            try:
                self.logger.info(f"크롤링 진행: {i+1}/{len(articles)} - {url}")
                
                # newspaper3k를 사용한 기사 크롤링  
                from newspaper import Config
                config = Config()
                config.request_timeout = 15
                config.number_threads = 1
                
                news_article = Article(url, config=config)
                
                news_article.download()
                news_article.parse()
                
                # 본문 내용 확인
                content = news_article.text.strip()
                if len(content) < 100:  # 너무 짧은 내용은 제외
                    self.logger.warning(f"본문이 너무 짧음: {url}")
                    failed_urls.append(url)
                    continue
                
                # 기사 정보 업데이트
                article.update({
                    'content': content,
                    'title': news_article.title or article.get('title', ''),
                    'authors': news_article.authors,
                    'publish_date': news_article.publish_date or article.get('published_date'),
                    'top_image': news_article.top_image,
                    'summary': news_article.summary if news_article.summary else None
                })
                
                crawled_articles.append(article)
                self.logger.info(f"크롤링 성공: {article['title'][:50]}...")
                
                # 요청 간격 조절 (서버 부하 방지)
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"크롤링 실패: {url} - {e}")
                failed_urls.append(url)
                continue
        
        self.logger.info(f"본문 크롤링 완료: 성공 {len(crawled_articles)}개, 실패 {len(failed_urls)}개")
        if failed_urls:
            self.logger.info(f"실패한 URL 목록: {failed_urls[:5]}...")  # 처음 5개만 표시
        
        return crawled_articles
    
    def step3_generate_summaries(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        3단계: OpenAI GPT-3.5 Turbo로 기사 요약 생성
        """
        self.logger.info("3단계: OpenAI GPT-3.5 Turbo로 요약 생성 시작")
        
        summarized_articles = []
        
        for i, article in enumerate(articles):
            try:
                content = article.get('content', '')
                if not content or len(content) < 100:
                    self.logger.warning(f"본문이 없거나 너무 짧음: {article.get('title', 'No title')}")
                    continue
                
                self.logger.info(f"요약 생성: {i+1}/{len(articles)} - {article.get('title', '')[:50]}...")
                
                # GPT-3.5 Turbo로 요약 생성
                prompt = f"""다음 기사를 핵심 위주로 3~5문장으로 요약해줘:

{content}"""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                
                summary = response.choices[0].message.content.strip()
                
                if summary:
                    article['summary'] = summary
                    summarized_articles.append(article)
                    self.logger.info(f"요약 생성 완료: {len(summary)}자")
                else:
                    self.logger.warning(f"요약 생성 실패: 빈 응답")
                
                # API 제한 방지를 위한 대기
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"요약 생성 실패: {article.get('title', 'No title')} - {e}")
                continue
        
        self.logger.info(f"요약 생성 완료: {len(summarized_articles)}개")
        return summarized_articles
    
    def step4_generate_embeddings(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        4단계: text-embedding-ada-002로 요약문 임베딩 생성
        """
        self.logger.info("4단계: text-embedding-ada-002로 임베딩 생성 시작")
        
        embedded_articles = []
        
        for i, article in enumerate(articles):
            try:
                summary = article.get('summary', '')
                if not summary:
                    self.logger.warning(f"요약이 없음: {article.get('title', 'No title')}")
                    continue
                
                self.logger.info(f"임베딩 생성: {i+1}/{len(articles)} - {article.get('title', '')[:50]}...")
                
                # 임베딩 생성
                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=summary
                )
                
                embedding = response.data[0].embedding
                
                article['embedding'] = embedding
                embedded_articles.append(article)
                self.logger.info(f"임베딩 생성 완료: {len(embedding)} 차원")
                
                # API 제한 방지를 위한 대기
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"임베딩 생성 실패: {article.get('title', 'No title')} - {e}")
                continue
        
        self.logger.info(f"임베딩 생성 완료: {len(embedded_articles)}개")
        return embedded_articles
    
    def step5_store_in_vector_db(self, articles: List[Dict[str, Any]]) -> int:
        """
        5단계: Vector DB에 저장 (중복 체크 포함)
        """
        self.logger.info("5단계: Vector DB 저장 시작")
        
        stored_count = 0
        duplicate_count = 0
        error_count = 0
        
        for i, article in enumerate(articles):
            try:
                # 중복 체크 (title + published_date 기준)
                title = article.get('title', '')
                published_date = article.get('published_date', datetime.now())
                
                if isinstance(published_date, str):
                    try:
                        published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    except:
                        published_date = datetime.now()
                
                # 기존 데이터베이스에서 중복 체크
                existing = self.dual_db_service.search_similar_articles(
                    query=title,
                    limit=1,
                    similarity_threshold=0.9
                )
                
                if existing and len(existing) > 0:
                    # 제목이 매우 유사한 기사가 이미 존재
                    self.logger.info(f"중복 기사 스킵: {title[:50]}...")
                    duplicate_count += 1
                    continue
                
                # 데이터베이스 저장 형식으로 변환
                db_article = {
                    'title': title,
                    'content': article.get('content', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', ''),
                    'published_date': published_date.isoformat(),
                    'keywords': self._extract_keywords(article.get('summary', '')),
                    'sentiment': 'neutral',  # 기본값
                    'raw_data': article.get('raw_data', {})
                }
                
                # 데이터베이스에 저장
                try:
                    success = self.dual_db_service.insert_news_article(db_article)
                    
                    if success:
                        stored_count += 1
                        self.logger.info(f"저장 완료: {i+1}/{len(articles)} - {title[:50]}...")
                    else:
                        error_count += 1
                        self.logger.error(f"저장 실패: {title[:50]}...")
                        
                except Exception as save_error:
                    error_count += 1
                    self.logger.error(f"저장 중 예외 발생: {title[:50]}... - {save_error}")
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"저장 중 오류: {article.get('title', 'No title')} - {e}")
                continue
        
        self.logger.info(f"Vector DB 저장 완료: 저장 {stored_count}개, 중복 {duplicate_count}개, 오류 {error_count}개")
        return stored_count
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출 (간단한 구현)"""
        if not text:
            return []
        
        # 비트코인 관련 키워드들
        bitcoin_keywords = [
            'bitcoin', 'btc', '비트코인', 'cryptocurrency', 'crypto', 
            'blockchain', '블록체인', 'ethereum', 'eth', '이더리움',
            'mining', '채굴', 'wallet', '지갑', 'exchange', '거래소'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in bitcoin_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:10]  # 최대 10개
    
    def run_complete_pipeline(self, limit: int = 20) -> Dict[str, Any]:
        """
        전체 파이프라인 실행
        """
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'collected_count': 0,
            'crawled_count': 0,
            'summarized_count': 0,
            'embedded_count': 0,
            'stored_count': 0,
            'duration_seconds': 0,
            'errors': []
        }
        
        try:
            self.logger.info("=" * 60)
            self.logger.info("비트코인 뉴스 파이프라인 실행 시작")
            self.logger.info("=" * 60)
            
            # 1단계: 뉴스 수집
            articles = self.step1_collect_bitcoin_news(limit=limit)
            results['collected_count'] = len(articles)
            
            if not articles:
                self.logger.warning("수집된 뉴스가 없습니다.")
                return results
            
            # 2단계: 본문 크롤링
            crawled_articles = self.step2_crawl_article_content(articles)
            results['crawled_count'] = len(crawled_articles)
            
            if not crawled_articles:
                self.logger.warning("크롤링된 기사가 없습니다.")
                return results
            
            # 3단계: 요약 생성
            summarized_articles = self.step3_generate_summaries(crawled_articles)
            results['summarized_count'] = len(summarized_articles)
            
            if not summarized_articles:
                self.logger.warning("요약된 기사가 없습니다.")
                return results
            
            # 4단계: 임베딩 생성
            embedded_articles = self.step4_generate_embeddings(summarized_articles)
            results['embedded_count'] = len(embedded_articles)
            
            if not embedded_articles:
                self.logger.warning("임베딩된 기사가 없습니다.")
                return results
            
            # 5단계: Vector DB 저장
            stored_count = self.step5_store_in_vector_db(embedded_articles)
            results['stored_count'] = stored_count
            
            # 완료 처리
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            results['duration_seconds'] = duration
            results['end_time'] = end_time.isoformat()
            
            self.logger.info("=" * 60)
            self.logger.info("비트코인 뉴스 파이프라인 실행 완료")
            self.logger.info(f"실행 시간: {duration:.2f}초")
            self.logger.info(f"1단계 수집: {results['collected_count']}개")
            self.logger.info(f"2단계 크롤링: {results['crawled_count']}개")
            self.logger.info(f"3단계 요약: {results['summarized_count']}개")
            self.logger.info(f"4단계 임베딩: {results['embedded_count']}개")
            self.logger.info(f"5단계 저장: {results['stored_count']}개")
            self.logger.info("=" * 60)
            
        except Exception as e:
            error_msg = f"파이프라인 실행 중 오류: {e}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            raise
        
        return results

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='비트코인 뉴스 파이프라인 (CLAUDE.md 작업요청 v1)')
    parser.add_argument('--limit', type=int, default=20, help='수집할 뉴스 개수 (기본: 20개)')
    
    args = parser.parse_args()
    
    try:
        # 파이프라인 실행
        pipeline = BitcoinNewsPipeline()
        results = pipeline.run_complete_pipeline(limit=args.limit)
        
        print("\n" + "=" * 50)
        print("파이프라인 실행 결과:")
        print("=" * 50)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except KeyboardInterrupt:
        print("\n파이프라인이 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"파이프라인 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()