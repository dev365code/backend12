
import re
import logging
import sys
import os
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai
from dataclasses import dataclass

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

@dataclass
class NewsArticle:
    title: str
    content: str
    url: str
    published_date: datetime
    source: str
    summary: str = ""
    keywords: List[str] = None
    sentiment: str = ""

class NewsPreprocessor:
    def __init__(self, openai_api_key: str = None):
        """뉴스 전처리기 초기화"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        self.logger = logging.getLogger(__name__)
        
        # 코인 관련 키워드
        self.crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'cryptocurrency', 'crypto',
            'blockchain', 'defi', 'nft', 'altcoin', 'binance', 'coinbase',
            '비트코인', '이더리움', '가상화폐', '암호화폐', '블록체인', '코인'
        ]
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 특수문자 정리
        text = re.sub(r'[^\w\s\.,!?;:\-()%$]', '', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        keywords = []
        text_lower = text.lower()
        
        for keyword in self.crypto_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        # 추가적인 키워드 추출 로직
        words = re.findall(r'\b[A-Za-z가-힣]{3,}\b', text)
        word_freq = {}
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'was', 'one', 'our', 'has', 'have']:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # 빈도수 기준 상위 키워드 추가
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords.extend([word for word, freq in sorted_words[:5] if freq > 1])
        
        return list(set(keywords))
    
    def analyze_sentiment(self, text: str) -> str:
        """감정 분석 (간단한 키워드 기반)"""
        positive_words = ['상승', '증가', '호재', '긍정', 'bull', 'rise', 'increase', 'positive', 'growth']
        negative_words = ['하락', '감소', '악재', '부정', 'bear', 'fall', 'decrease', 'negative', 'crash']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def summarize_with_openai(self, text: str) -> str:
        """OpenAI를 사용한 뉴스 요약"""
        if not self.openai_api_key:
            self.logger.warning("OpenAI API key not found. Using basic summarization.")
            return self.basic_summarize(text)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 암호화폐 뉴스 전문 요약가입니다. 주어진 뉴스를 2-3문장으로 핵심 내용만 요약해주세요."
                    },
                    {
                        "role": "user",
                        "content": f"다음 뉴스를 요약해주세요:\n\n{text}"
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"OpenAI summarization failed: {e}")
            return self.basic_summarize(text)
    
    def basic_summarize(self, text: str, sentences_count: int = 3) -> str:
        """기본 요약 (첫 3문장 추출)"""
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= sentences_count:
            return '. '.join(sentences) + '.'
        
        return '. '.join(sentences[:sentences_count]) + '.'
    
    def is_crypto_related(self, text: str) -> bool:
        """암호화폐 관련 뉴스인지 확인"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crypto_keywords)
    
    def preprocess_article(self, article_data: Dict[str, Any]) -> NewsArticle:
        """뉴스 기사 전처리"""
        # 기본 정보 추출
        title = self.clean_text(article_data.get('title', ''))
        content = self.clean_text(article_data.get('content', ''))
        url = article_data.get('url', '')
        source = article_data.get('source', '')
        
        # 날짜 처리
        published_date = article_data.get('published_date')
        if isinstance(published_date, str):
            try:
                published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
            except:
                published_date = datetime.now()
        elif published_date is None:
            published_date = datetime.now()
        
        # 암호화폐 관련성 확인
        full_text = f"{title} {content}"
        if not self.is_crypto_related(full_text):
            self.logger.info(f"Article not crypto-related: {title[:50]}...")
        
        # 키워드 추출
        keywords = self.extract_keywords(full_text)
        
        # 감정 분석
        sentiment = self.analyze_sentiment(full_text)
        
        # 요약 생성
        summary = self.summarize_with_openai(content) if content else title
        
        return NewsArticle(
            title=title,
            content=content,
            url=url,
            published_date=published_date,
            source=source,
            summary=summary,
            keywords=keywords,
            sentiment=sentiment
        )
    
    def preprocess_articles(self, articles: List[Dict[str, Any]]) -> List[NewsArticle]:
        """여러 뉴스 기사 일괄 전처리"""
        processed_articles = []
        
        for article_data in articles:
            try:
                processed_article = self.preprocess_article(article_data)
                processed_articles.append(processed_article)
                self.logger.info(f"Processed: {processed_article.title[:50]}...")
                
            except Exception as e:
                self.logger.error(f"Failed to process article: {e}")
                continue
        
        return processed_articles

# 사용 예시
if __name__ == "__main__":
    # 테스트용 샘플 데이터
    sample_articles = [
        {
            "title": "비트코인 가격이 5만 달러를 돌파했습니다",
            "content": "비트코인이 오늘 5만 달러를 돌파하며 새로운 기록을 세웠습니다. 전문가들은 이번 상승이 기관 투자자들의 관심 증가와 관련이 있다고 분석했습니다.",
            "url": "https://example.com/news1",
            "source": "CryptoNews",
            "published_date": "2024-01-15T10:30:00Z"
        }
    ]
    
    preprocessor = NewsPreprocessor()
    processed = preprocessor.preprocess_articles(sample_articles)
    
    for article in processed:
        print(f"Title: {article.title}")
        print(f"Summary: {article.summary}")
        print(f"Keywords: {article.keywords}")
        print(f"Sentiment: {article.sentiment}")
        print("-" * 50)