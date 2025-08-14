"""
고급 뉴스 분석 및 요약 도구
Claude 수준의 분석과 인사이트 제공
"""

import logging
import os
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from pydantic import Field
from openai import OpenAI
import json
import re

from langchain_service.core.database_manager import db_manager, NewsArticle

logger = logging.getLogger(__name__)

class AdvancedNewsAnalyzer(BaseTool):
    """고급 뉴스 분석 도구 - Claude 수준의 분석"""
    
    name: str = "advanced_news_analyzer"
    description: str = """
    암호화폐 뉴스를 심층 분석하여 Claude 수준의 인사이트를 제공합니다.
    
    특징:
    - 시장 트렌드 분석
    - 감정 분석 및 시장 심리 파악
    - 주요 이벤트와 영향도 평가
    - 전문가 수준의 해석 제공
    - 투자 관점에서의 시사점 분석
    
    사용 예시:
    - "비트코인 최신 동향 분석해줘"
    - "암호화폐 시장 심리는 어때?"
    - "ETF 승인이 시장에 미치는 영향"
    """
    
    def __init__(self):
        super().__init__()
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def _run(self, query: str) -> str:
        """비동기 실행을 동기로 래핑"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._arun(query))
        finally:
            loop.close()
    
    async def _arun(self, query: str) -> str:
        """고급 뉴스 분석 실행"""
        try:
            logger.info(f"🔍 고급 뉴스 분석 시작: {query}")
            
            # 1단계: 관련 뉴스 수집
            news_articles = await self._collect_relevant_news(query)
            
            if not news_articles:
                return "📰 현재 관련된 뉴스를 찾을 수 없습니다. 뉴스 파이프라인을 실행하여 최신 뉴스를 수집해보세요."
            
            # 2단계: 뉴스 내용 심층 분석
            analysis_result = await self._analyze_news_content(news_articles, query)
            
            # 3단계: 시장 데이터와 연계 분석
            market_context = await self._get_market_context()
            
            # 4단계: Claude 스타일 종합 분석 보고서 생성
            comprehensive_report = await self._generate_comprehensive_report(
                query, news_articles, analysis_result, market_context
            )
            
            logger.info(f"✅ 고급 뉴스 분석 완료: {len(comprehensive_report)}자")
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"❌ 고급 뉴스 분석 실패: {e}")
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _collect_relevant_news(self, query: str, limit: int = 10) -> List[NewsArticle]:
        """관련 뉴스 수집"""
        # 키워드 확장
        expanded_queries = await self._expand_search_keywords(query)
        
        all_articles = []
        for expanded_query in expanded_queries:
            articles = await db_manager.search_news_advanced(
                query=expanded_query,
                limit=limit // len(expanded_queries) + 1,
                use_vector_search=True,
                similarity_threshold=0.2
            )
            all_articles.extend(articles)
        
        # 중복 제거 및 관련도 순 정렬
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            title_key = article.title.lower().strip()
            if title_key not in seen_titles and len(title_key) > 10:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        # 최신순 + 관련도순 정렬
        unique_articles.sort(key=lambda x: (x.relevance_score, x.published_date or datetime.min), reverse=True)
        
        return unique_articles[:limit]
    
    async def _expand_search_keywords(self, query: str) -> List[str]:
        """검색 키워드 확장"""
        base_queries = [query]
        
        # 비트코인 관련 키워드 확장
        if any(keyword in query.lower() for keyword in ['비트코인', 'bitcoin', 'btc']):
            base_queries.extend([
                'bitcoin price analysis',
                'btc market trend',
                'bitcoin institutional adoption',
                '비트코인 시장 분석',
                '비트코인 제도권 진입'
            ])
        
        # ETF 관련 키워드 확장
        if 'etf' in query.lower():
            base_queries.extend([
                'bitcoin etf approval',
                'crypto etf impact',
                'institutional crypto investment'
            ])
        
        # 규제 관련 키워드 확장
        if any(keyword in query.lower() for keyword in ['규제', 'regulation', 'sec']):
            base_queries.extend([
                'crypto regulation news',
                'sec bitcoin decision',
                'cryptocurrency legal framework'
            ])
        
        return base_queries[:5]  # 최대 5개 쿼리
    
    async def _analyze_news_content(self, articles: List[NewsArticle], user_query: str) -> Dict[str, Any]:
        """뉴스 내용 심층 분석"""
        if not articles:
            return {}
        
        # 뉴스 내용 준비
        news_content = []
        for i, article in enumerate(articles[:5], 1):  # 상위 5개 기사만
            content = f"{i}. **{article.title}**\n"
            content += f"   출처: {article.source}\n"
            content += f"   날짜: {article.published_date}\n"
            if article.summary:
                content += f"   요약: {article.summary}\n"
            news_content.append(content)
        
        analysis_prompt = f"""다음 암호화폐 뉴스들을 전문 애널리스트 관점에서 심층 분석해주세요.

사용자 질문: "{user_query}"

뉴스 자료:
{chr(10).join(news_content)}

분석 요구사항:
1. **시장 트렌드 파악**: 현재 시장의 주요 흐름과 방향성
2. **감정 분석**: 시장 참여자들의 심리 상태 (강세/약세/관망)
3. **핵심 이벤트**: 가격에 영향을 미칠 수 있는 주요 사건들
4. **리스크 요인**: 잠재적 위험 요소들
5. **기회 요인**: 긍정적 성장 동력들

JSON 형식으로 답변해주세요:
{{
    "market_trend": "현재 시장 트렌드 분석",
    "sentiment_analysis": "시장 감정 분석",
    "key_events": ["주요 이벤트 1", "주요 이벤트 2"],
    "risk_factors": ["리스크 요인 1", "리스크 요인 2"],
    "opportunity_factors": ["기회 요인 1", "기회 요인 2"],
    "overall_assessment": "종합 평가"
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",  # 더 정확한 분석을 위해 GPT-4 사용
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON 파싱 시도
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트 분석
                return {"raw_analysis": result_text}
                
        except Exception as e:
            logger.error(f"뉴스 내용 분석 실패: {e}")
            return {"error": str(e)}
    
    async def _get_market_context(self) -> Dict[str, Any]:
        """시장 맥락 정보 수집"""
        try:
            # 데이터베이스 통계 조회
            db_stats = await db_manager.get_database_stats()
            
            # 최근 뉴스 트렌드 분석
            recent_news = await db_manager.get_recent_news(hours=24, limit=20)
            
            # 뉴스 빈도 분석
            news_frequency = {
                '24h': len([n for n in recent_news if n.published_date and 
                           (datetime.now() - n.published_date).total_seconds() < 86400]),
                '7d': db_stats.get('news_7d', 0)
            }
            
            return {
                'database_stats': db_stats,
                'news_frequency': news_frequency,
                'data_freshness': db_stats.get('last_updated'),
                'total_articles_analyzed': len(recent_news)
            }
            
        except Exception as e:
            logger.error(f"시장 맥락 정보 수집 실패: {e}")
            return {}
    
    async def _generate_comprehensive_report(
        self, 
        query: str, 
        articles: List[NewsArticle], 
        analysis: Dict[str, Any], 
        market_context: Dict[str, Any]
    ) -> str:
        """Claude 스타일 종합 분석 보고서 생성"""
        
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        current_time = datetime.now().strftime("%H:%M")
        
        # 기사 요약 생성
        top_articles = articles[:3]
        article_summaries = []
        for i, article in enumerate(top_articles, 1):
            summary = f"{i}. **{article.title}**"
            if article.published_date:
                date_str = article.published_date.strftime("%m/%d %H:%M")
                summary += f" ({date_str})"
            if article.summary:
                summary += f"\n   {article.summary[:100]}..."
            summary += f"\n   📊 관련도: {article.relevance_score:.2f} | 출처: {article.source}"
            article_summaries.append(summary)
        
        # 분석 결과 정리
        market_trend = analysis.get('market_trend', '시장 트렌드 분석 데이터 부족')
        sentiment = analysis.get('sentiment_analysis', '시장 감정 데이터 부족')
        key_events = analysis.get('key_events', [])
        risks = analysis.get('risk_factors', [])
        opportunities = analysis.get('opportunity_factors', [])
        
        # 데이터 신뢰도 표시
        total_articles = market_context.get('database_stats', {}).get('total_news', 0)
        recent_articles = market_context.get('news_frequency', {}).get('24h', 0)
        
        comprehensive_report = f"""# 🔍 암호화폐 시장 종합 분석 보고서

**분석 기준시점**: {current_date} {current_time}  
**분석 대상**: "{query}"  
**데이터 기반**: 총 {total_articles}개 기사 (최근 24시간 {recent_articles}개)

---

## 📊 **핵심 시장 동향**

{market_trend}

### 🎯 **시장 심리 분석**
{sentiment}

---

## 📰 **주요 뉴스 분석**

{chr(10).join(article_summaries)}

---

## ⚡ **주요 이벤트 & 촉매**

{chr(10).join([f"• **{event}**" for event in key_events]) if key_events else "• 현재 특별한 시장 이벤트는 감지되지 않았습니다."}

---

## ⚠️ **리스크 요인**

{chr(10).join([f"• {risk}" for risk in risks]) if risks else "• 현재 주요 리스크 요인이 명확히 식별되지 않았습니다."}

---

## 🚀 **기회 요인**

{chr(10).join([f"• {opp}" for opp in opportunities]) if opportunities else "• 현재 명확한 기회 요인이 식별되지 않았습니다."}

---

## 🎯 **종합 평가 및 전망**

{analysis.get('overall_assessment', '현재 이용 가능한 데이터를 종합해보면, 시장은 여러 요인들의 영향을 받고 있으며, 투자자들은 신중한 접근이 필요한 상황입니다.')}

---

## 📋 **데이터 신뢰도**

- **분석 기사 수**: {len(articles)}개
- **벡터 검색 정확도**: 평균 {sum(a.relevance_score for a in articles) / len(articles):.2f}
- **데이터 신선도**: 최근 24시간 내 {recent_articles}개 뉴스 업데이트
- **임베딩 처리율**: {market_context.get('database_stats', {}).get('embedding_coverage', 0):.1f}%

*💡 이 분석은 AI가 수집된 뉴스 데이터를 기반으로 생성한 것으로, 투자 결정 시 추가적인 정보 확인이 필요합니다.*"""

        return comprehensive_report

class MarketSentimentAnalyzer(BaseTool):
    """시장 감정 분석 전용 도구"""
    
    name: str = "market_sentiment_analyzer"
    description: str = """
    암호화폐 시장의 전반적인 감정과 심리를 분석합니다.
    
    특징:
    - 뉴스 기반 감정 분석
    - 시장 참여자 심리 파악
    - Fear & Greed 지수 해석
    - 투자자 행동 패턴 분석
    """
    
    def __init__(self):
        super().__init__()
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def _run(self, query: str = "시장 감정 분석") -> str:
        """시장 감정 분석 실행"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._analyze_market_sentiment())
        finally:
            loop.close()
    
    async def _analyze_market_sentiment(self) -> str:
        """시장 감정 분석"""
        try:
            logger.info("📊 시장 감정 분석 시작")
            
            # 최근 24시간 뉴스 수집
            recent_news = await db_manager.get_recent_news(hours=24, limit=15)
            
            if not recent_news:
                return "📊 최근 24시간 내 뉴스가 부족하여 정확한 시장 감정 분석이 어렵습니다."
            
            # 뉴스 제목과 요약으로 감정 분석
            news_texts = []
            for article in recent_news:
                text = f"{article.title}"
                if article.summary:
                    text += f" {article.summary}"
                news_texts.append(text)
            
            sentiment_prompt = f"""다음 최근 24시간 암호화폐 뉴스들을 분석하여 시장 감정을 평가해주세요:

뉴스 데이터:
{chr(10).join([f"- {text[:150]}..." for text in news_texts])}

분석 기준:
1. 전반적인 시장 감정 (매우 부정적 ~ 매우 긍정적)
2. 투자자 심리 상태
3. 주요 감정 동인 (무엇이 감정을 주도하는가)
4. 단기 전망 (향후 1-7일)

시장 감정을 다음 형식으로 분석해주세요:

📊 **시장 감정 지수**: [점수]/10 (1=극도 공포, 10=극도 탐욕)

🎭 **현재 심리 상태**: 
[상세 분석]

⚡ **주요 감정 동인**:
• [동인 1]
• [동인 2] 
• [동인 3]

🔮 **단기 전망**:
[향후 전망]

📈 **투자자 행동 권고**:
[행동 가이드]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": sentiment_prompt}],
                max_tokens=800,
                temperature=0.2
            )
            
            result = response.choices[0].message.content.strip()
            
            # 분석 메타데이터 추가
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            footer = f"\n\n---\n*📅 분석 시점: {current_time} | 📰 분석 기사: {len(recent_news)}개*"
            
            return result + footer
            
        except Exception as e:
            logger.error(f"❌ 시장 감정 분석 실패: {e}")
            return f"시장 감정 분석 중 오류가 발생했습니다: {str(e)}"

class TrendAnalyzer(BaseTool):
    """트렌드 분석 도구"""
    
    name: str = "trend_analyzer"  
    description: str = """
    암호화폐 시장의 트렌드와 패턴을 분석합니다.
    
    특징:
    - 시간대별 뉴스 트렌드 분석
    - 키워드 빈도 분석
    - 이슈의 생명주기 추적
    - 새로운 트렌드 발굴
    """
    
    def _run(self, period: str = "7d") -> str:
        """트렌드 분석 실행"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._analyze_trends(period))
        finally:
            loop.close()
    
    async def _analyze_trends(self, period: str) -> str:
        """트렌드 분석"""
        try:
            logger.info(f"📈 트렌드 분석 시작: {period}")
            
            # 기간별 뉴스 수집
            hours_map = {"24h": 24, "7d": 168, "30d": 720}
            hours = hours_map.get(period, 168)
            
            news_articles = await db_manager.get_recent_news(hours=hours, limit=50)
            
            if not news_articles:
                return f"📈 최근 {period} 기간의 뉴스가 부족하여 트렌드 분석이 어렵습니다."
            
            # 키워드 빈도 분석
            keyword_analysis = self._extract_trending_keywords(news_articles)
            
            # 시간대별 분포 분석
            temporal_analysis = self._analyze_temporal_distribution(news_articles)
            
            # 트렌드 보고서 생성
            report = f"""# 📈 암호화폐 시장 트렌드 분석 ({period})

## 🔥 **핫 키워드 TOP 10**
{chr(10).join([f"{i}. **{keyword}** ({count}회 언급)" for i, (keyword, count) in enumerate(keyword_analysis[:10], 1)])}

## ⏰ **시간대별 뉴스 분포**
- 총 뉴스 개수: {len(news_articles)}개
- 일평균 뉴스: {len(news_articles) / (hours / 24):.1f}개
- 최신 뉴스: {temporal_analysis.get('latest', '정보 없음')}

## 📊 **트렌드 인사이트**
{self._generate_trend_insights(keyword_analysis, temporal_analysis)}

---
*📅 분석 기간: 최근 {period} | 분석 기사: {len(news_articles)}개*"""

            return report
            
        except Exception as e:
            logger.error(f"❌ 트렌드 분석 실패: {e}")
            return f"트렌드 분석 중 오류가 발생했습니다: {str(e)}"
    
    def _extract_trending_keywords(self, articles: List[NewsArticle]) -> List[Tuple[str, int]]:
        """트렌딩 키워드 추출"""
        keyword_count = {}
        
        # 중요 키워드 목록
        important_keywords = [
            'bitcoin', 'btc', '비트코인', 'ethereum', 'eth', '이더리움',
            'etf', 'sec', '규제', 'regulation', 'trump', '트럼프',
            'mining', '채굴', 'halving', '반감기', 'institutional',
            'adoption', '제도권', 'whale', '고래', 'defi', 'nft'
        ]
        
        for article in articles:
            text = (article.title + " " + (article.summary or "")).lower()
            
            for keyword in important_keywords:
                count = text.count(keyword.lower())
                if count > 0:
                    keyword_count[keyword] = keyword_count.get(keyword, 0) + count
        
        # 빈도순 정렬
        return sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
    
    def _analyze_temporal_distribution(self, articles: List[NewsArticle]) -> Dict[str, Any]:
        """시간대별 분포 분석"""
        if not articles:
            return {}
        
        # 최신 기사 찾기
        latest_article = max(articles, key=lambda x: x.published_date or datetime.min)
        
        # 날짜별 분포
        daily_counts = {}
        for article in articles:
            if article.published_date:
                date_key = article.published_date.strftime("%Y-%m-%d")
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
        
        return {
            'latest': latest_article.published_date.strftime("%m/%d %H:%M") if latest_article.published_date else None,
            'daily_distribution': daily_counts,
            'peak_day': max(daily_counts.keys(), key=lambda x: daily_counts[x]) if daily_counts else None
        }
    
    def _generate_trend_insights(self, keywords: List[Tuple[str, int]], temporal: Dict[str, Any]) -> str:
        """트렌드 인사이트 생성"""
        insights = []
        
        if keywords:
            top_keyword = keywords[0][0]
            insights.append(f"• 현재 가장 주목받는 키워드는 '{top_keyword}'입니다.")
        
        if temporal.get('peak_day'):
            insights.append(f"• {temporal['peak_day']}에 가장 많은 뉴스가 발생했습니다.")
        
        # ETF 관련 트렌드
        etf_mentions = sum(count for keyword, count in keywords if 'etf' in keyword.lower())
        if etf_mentions > 0:
            insights.append(f"• ETF 관련 이슈가 {etf_mentions}회 언급되어 높은 관심을 보이고 있습니다.")
        
        # 규제 관련 트렌드  
        reg_mentions = sum(count for keyword, count in keywords if keyword.lower() in ['sec', '규제', 'regulation'])
        if reg_mentions > 0:
            insights.append(f"• 규제 관련 뉴스가 {reg_mentions}회 언급되어 주의 깊게 모니터링이 필요합니다.")
        
        return "\n".join(insights) if insights else "• 현재 특별한 트렌드가 감지되지 않았습니다."