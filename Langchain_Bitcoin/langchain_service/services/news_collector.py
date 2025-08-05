import requests
import feedparser
import logging
import sys
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import json
import redis
from dataclasses import asdict

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class NewsCollector:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        """뉴스 수집기 초기화"""
        self.logger = logging.getLogger(__name__)
        
        # Redis 연결
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
            self.logger.info("Redis connected successfully")
        except Exception as e:
            self.logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
        
        # NewsData.io API 키
        self.newsdata_api_key = os.getenv('NEWSDATA_API_KEY', 'pub_6310825edf31fee9b01e55b7de1bb63c8a3bc')
        
        # 뉴스 소스 설정
        self.news_sources = {
            'newsdata_io': {
                'url': 'https://newsdata.io/api/1/news',
                'type': 'api',
                'params': {
                    'apikey': self.newsdata_api_key,
                    'q': 'bitcoin OR cryptocurrency OR crypto OR ethereum OR blockchain',
                    'language': 'en',
                    'category': 'business,technology',
                    'size': 50
                }
            },
            'coindesk': {
                'rss_url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'type': 'rss'
            },
            'cointelegraph': {
                'rss_url': 'https://cointelegraph.com/rss',
                'type': 'rss'
            },
            'bitcoin_magazine': {
                'rss_url': 'https://bitcoinmagazine.com/.rss/full/',
                'type': 'rss'
            },
            'decrypt': {
                'rss_url': 'https://decrypt.co/feed',
                'type': 'rss'
            }
        }
        
        # 한국 뉴스 소스
        self.korean_sources = {
            'coinness': {
                'url': 'https://coinness.com/news',
                'type': 'web_scraping'
            },
            'tokenpost': {
                'url': 'https://www.tokenpost.kr/news',
                'type': 'web_scraping'
            }
        }
        
        # 요청 헤더
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def is_duplicate(self, article_url: str) -> bool:
        """중복 기사 확인"""
        if not self.redis_client:
            return False
        
        key = f"news:url:{hash(article_url)}"
        return self.redis_client.exists(key)
    
    def mark_as_processed(self, article_url: str, expiry_hours: int = 168):  # 7일
        """처리된 기사로 표시"""
        if not self.redis_client:
            return
        
        key = f"news:url:{hash(article_url)}"
        self.redis_client.setex(key, timedelta(hours=expiry_hours), "processed")
    
    def collect_from_rss(self, source_name: str, rss_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """RSS 피드에서 뉴스 수집"""
        articles = []
        
        try:
            self.logger.info(f"Collecting from RSS: {source_name}")
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:limit]:
                # 중복 체크
                if self.is_duplicate(entry.link):
                    continue
                
                # 날짜 파싱
                published_date = datetime.now()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])
                
                # 내용 추출
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                article = {
                    'title': entry.title,
                    'content': content,
                    'url': entry.link,
                    'source': source_name,
                    'published_date': published_date.isoformat(),
                    'raw_data': {
                        'author': getattr(entry, 'author', ''),
                        'tags': [tag.term for tag in getattr(entry, 'tags', [])]
                    }
                }
                
                articles.append(article)
                self.mark_as_processed(entry.link)
            
            self.logger.info(f"Collected {len(articles)} articles from {source_name}")
            
        except Exception as e:
            self.logger.error(f"Error collecting from {source_name}: {e}")
        
        return articles
    
    def extract_article_content(self, url: str) -> str:
        """웹페이지에서 기사 본문 추출"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 일반적인 기사 본문 선택자들
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '[data-module="ArticleBody"]'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    # 불필요한 요소 제거
                    for unwanted in element.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                        unwanted.decompose()
                    
                    content = element.get_text(strip=True)
                    if len(content) > 200:  # 충분한 내용이 있으면 사용
                        break
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return ""
    
    def collect_from_web(self, source_name: str, base_url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """웹 스크래핑으로 뉴스 수집"""
        articles = []
        
        try:
            self.logger.info(f"Collecting from web: {source_name}")
            response = requests.get(base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 뉴스 링크 추출 (일반적인 패턴)
            link_selectors = [
                'a[href*="/news/"]',
                'a[href*="/article/"]',
                'a[href*="/post/"]',
                '.news-item a',
                '.article-item a'
            ]
            
            links = set()
            for selector in link_selectors:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        if href.startswith('/'):
                            href = base_url.rstrip('/') + href
                        links.add(href)
                        
                        if len(links) >= limit:
                            break
                
                if len(links) >= limit:
                    break
            
            # 각 링크에서 기사 수집
            for link in list(links)[:limit]:
                if self.is_duplicate(link):
                    continue
                
                try:
                    response = requests.get(link, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 제목 추출
                    title = ""
                    title_selectors = ['h1', '.title', '.article-title', 'title']
                    for selector in title_selectors:
                        element = soup.select_one(selector)
                        if element:
                            title = element.get_text(strip=True)
                            if title:
                                break
                    
                    # 내용 추출
                    content = self.extract_article_content(link)
                    
                    if title and content:
                        article = {
                            'title': title,
                            'content': content,
                            'url': link,
                            'source': source_name,
                            'published_date': datetime.now().isoformat(),
                            'raw_data': {}
                        }
                        
                        articles.append(article)
                        self.mark_as_processed(link)
                    
                    # 요청 간격 조절
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error processing article {link}: {e}")
                    continue
            
            self.logger.info(f"Collected {len(articles)} articles from {source_name}")
            
        except Exception as e:
            self.logger.error(f"Error collecting from {source_name}: {e}")
        
        return articles
    
    def collect_newsdata_api(self, source_config: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """NewsData.io API에서 뉴스 수집"""
        articles = []
        
        try:
            self.logger.info("Collecting from NewsData.io API")
            
            response = requests.get(
                source_config['url'],
                params=source_config['params'],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    for item in data.get('results', [])[:limit]:
                        # 중복 체크
                        url = item.get('link', '')
                        if not url or self.is_duplicate(url):
                            continue
                        
                        # 날짜 파싱
                        published_date = datetime.now()
                        if item.get('pubDate'):
                            try:
                                published_date = datetime.fromisoformat(item['pubDate'].replace('Z', '+00:00'))
                            except:
                                pass
                        
                        article = {
                            'title': item.get('title', ''),
                            'content': item.get('content', '') or item.get('description', ''),
                            'url': url,
                            'source': f"newsdata_io_{item.get('source_id', 'unknown')}",
                            'published_date': published_date.isoformat(),
                            'raw_data': {
                                'category': item.get('category', []),
                                'country': item.get('country', []),
                                'language': item.get('language', ''),
                                'image_url': item.get('image_url', ''),
                                'keywords': item.get('keywords', [])
                            }
                        }
                        
                        articles.append(article)
                        self.mark_as_processed(url)
                    
                    self.logger.info(f"Collected {len(articles)} articles from NewsData.io")
                else:
                    self.logger.error(f"NewsData.io API error: {data.get('message', 'Unknown error')}")
            else:
                self.logger.error(f"NewsData.io API request failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error collecting from NewsData.io: {e}")
        
        return articles

    def collect_all_news(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """모든 소스에서 뉴스 수집"""
        all_articles = []
        
        # NewsData.io API에서 우선 수집
        if 'newsdata_io' in self.news_sources:
            articles = self.collect_newsdata_api(self.news_sources['newsdata_io'])
            all_articles.extend(articles)
            time.sleep(2)
        
        # RSS 소스에서 수집
        for source_name, config in self.news_sources.items():
            if config.get('type') == 'rss':
                articles = self.collect_from_rss(source_name, config['rss_url'])
                all_articles.extend(articles)
                time.sleep(2)  # API 제한 방지
        
        # 웹 스크래핑 소스에서 수집 (주의: 실제 사용시 robots.txt 확인 필요)
        # for source_name, config in self.korean_sources.items():
        #     articles = self.collect_from_web(source_name, config['url'])
        #     all_articles.extend(articles)
        #     time.sleep(3)  # 더 긴 간격
        
        # 최근 뉴스만 필터링
        cutoff_date = datetime.now() - timedelta(hours=hours_back)
        filtered_articles = []
        
        for article in all_articles:
            try:
                article_date = datetime.fromisoformat(article['published_date'].replace('Z', '+00:00'))
                if article_date >= cutoff_date:
                    filtered_articles.append(article)
            except:
                # 날짜 파싱 실패시 최근 뉴스로 간주
                filtered_articles.append(article)
        
        self.logger.info(f"Total collected articles: {len(filtered_articles)}")
        return filtered_articles
    
    def save_to_cache(self, articles: List[Dict[str, Any]], cache_key: str = "latest_news"):
        """수집된 뉴스를 캐시에 저장"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                cache_key,
                timedelta(hours=6),  # 6시간 캐시
                json.dumps(articles, default=str)
            )
            self.logger.info(f"Saved {len(articles)} articles to cache")
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")
    
    def load_from_cache(self, cache_key: str = "latest_news") -> List[Dict[str, Any]]:
        """캐시에서 뉴스 로드"""
        if not self.redis_client:
            return []
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                articles = json.loads(cached_data)
                self.logger.info(f"Loaded {len(articles)} articles from cache")
                return articles
        except Exception as e:
            self.logger.error(f"Error loading from cache: {e}")
        
        return []

# 사용 예시
if __name__ == "__main__":
    collector = NewsCollector()
    
    # 캐시에서 먼저 확인
    cached_articles = collector.load_from_cache()
    
    if not cached_articles:
        # 새로 수집
        articles = collector.collect_all_news(hours_back=24)
        collector.save_to_cache(articles)
    else:
        articles = cached_articles
    
    print(f"총 {len(articles)}개의 뉴스를 수집했습니다.")
    
    for article in articles[:3]:  # 처음 3개만 출력
        print(f"제목: {article['title']}")
        print(f"출처: {article['source']}")
        print(f"URL: {article['url']}")
        print("-" * 50)