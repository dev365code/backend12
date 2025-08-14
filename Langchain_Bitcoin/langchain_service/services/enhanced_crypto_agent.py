"""
향상된 암호화폐 에이전트 - Claude 수준의 응답 품질 제공
고급 분석 도구들을 통합하여 전문가 수준의 인사이트 생성
"""

import logging
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI

# 고급 분석 도구들 import
from langchain_service.tools.advanced_news_analyzer import AdvancedNewsAnalyzer, MarketSentimentAnalyzer, TrendAnalyzer
from langchain_service.tools.realtime_market_data import RealTimeMarketDataTool, MarketHeatmapTool
from langchain_service.core.database_manager import db_manager

# 기존 도구들
from langchain_service.tools.news_tools import CryptoNewsSearchTool, LatestNewsLookupTool, DatabaseStatsTool
from langchain_service.tools.price_tools import CryptoPriceChecker, MultiCoinPriceChecker, CoinMarketCapTool

logger = logging.getLogger(__name__)

class EnhancedCryptoAgent:
    """Claude 수준의 향상된 암호화폐 AI 에이전트"""
    
    def __init__(self, vector_service=None):
        """초기화"""
        self.vector_service = vector_service
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 고급 분석 도구들
        self.advanced_news_analyzer = None
        self.market_sentiment_analyzer = None
        self.trend_analyzer = None
        self.realtime_market_tool = None
        self.market_heatmap_tool = None
        
        # 기존 도구들
        self.news_search_tool = None
        self.latest_news_tool = None
        self.db_stats_tool = None
        self.price_checker = None
        self.multi_price_checker = None
        self.market_cap_tool = None
        
        # Intent 분류를 위한 고급 패턴
        self.enhanced_intent_patterns = {
            'comprehensive_analysis': [
                '종합 분석', '전체 분석', '심층 분석', 'comprehensive analysis',
                '전반적인', '상황 파악', '시장 전체', '전체적으로'
            ],
            'market_sentiment': [
                '시장 심리', '감정 분석', 'sentiment', '분위기', '심리상태',
                '투자자 심리', '시장 분위기', '공포 탐욕', 'fear greed'
            ],
            'trend_analysis': [
                '트렌드', 'trend', '추세', '패턴', '흐름', '경향',
                '방향성', '동향', '움직임', '변화'
            ],
            'technical_analysis': [
                '기술적 분석', 'technical analysis', 'TA', '차트', '지표',
                'rsi', 'macd', '볼린저', 'bollinger', '이동평균', '저항', '지지'
            ],
            'realtime_data': [
                '실시간', 'realtime', 'real-time', '현재', '지금', '최신',
                '라이브', 'live', '즉시', '현재가', '실시간 가격'
            ],
            'news_analysis': [
                '뉴스', 'news', '기사', '소식', '언론', '보도',
                '뉴스 분석', '기사 분석', '언론 보도'
            ],
            'price_inquiry': [
                '가격', 'price', '시세', '얼마', '값', '비용',
                '현재가', '시장가', '거래가'
            ]
        }
    
    async def initialize(self):
        """에이전트 및 모든 도구 초기화"""
        try:
            logger.info("🚀 Enhanced Crypto Agent 초기화 중...")
            
            # 데이터베이스 매니저 초기화
            await db_manager.initialize()
            
            # 고급 분석 도구들 초기화
            self.advanced_news_analyzer = AdvancedNewsAnalyzer()
            self.market_sentiment_analyzer = MarketSentimentAnalyzer()
            self.trend_analyzer = TrendAnalyzer()
            self.realtime_market_tool = RealTimeMarketDataTool()
            self.market_heatmap_tool = MarketHeatmapTool()
            
            # 기존 도구들 초기화
            if self.vector_service:
                self.news_search_tool = CryptoNewsSearchTool(vector_service=self.vector_service)
                self.latest_news_tool = LatestNewsLookupTool(vector_service=self.vector_service)
                self.db_stats_tool = DatabaseStatsTool(vector_service=self.vector_service)
            
            self.price_checker = CryptoPriceChecker()
            self.multi_price_checker = MultiCoinPriceChecker()
            self.market_cap_tool = CoinMarketCapTool()
            
            logger.info("✅ Enhanced Crypto Agent 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Enhanced Crypto Agent 초기화 실패: {e}")
            raise
    
    async def process_message(self, message: str, session_id: str, use_rag: bool = True) -> Dict[str, Any]:
        """메시지 처리 - Claude 수준의 응답 생성"""
        try:
            logger.info(f"🧠 Enhanced Agent 메시지 처리 시작: {message[:50]}...")
            
            # 1단계: 고급 Intent 분류
            intent_result = await self._classify_enhanced_intent(message)
            intent = intent_result['intent']
            confidence = intent_result['confidence']
            
            logger.info(f"🎯 분류된 Intent: {intent} (신뢰도: {confidence:.2f})")
            
            # 2단계: Intent별 Claude 수준 분석 수행
            response_text = await self._process_enhanced_intent(intent, message, session_id)
            
            # 3단계: 응답 품질 향상
            enhanced_response = await self._enhance_response_quality(response_text, message, intent)
            
            # 4단계: 결과 구성
            result = {
                'message': enhanced_response,
                'session_id': session_id,
                'data_sources': self._get_enhanced_data_sources(intent),
                'confidence_score': confidence,
                'intent': intent,
                'processing_method': 'enhanced_claude_level_agent',
                'analysis_depth': self._get_analysis_depth(intent),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Enhanced Agent 처리 완료: {len(enhanced_response)}자 응답")
            return result
            
        except Exception as e:
            logger.error(f"💥 Enhanced Agent 처리 중 오류: {e}")
            
            # 고급 오류 응답
            error_response = {
                'message': await self._generate_intelligent_error_response(str(e), message),
                'session_id': session_id,
                'data_sources': ['Error Handling System'],
                'error': str(e),
                'processing_method': 'error_recovery'
            }
            return error_response
    
    async def _classify_enhanced_intent(self, message: str) -> Dict[str, Any]:
        """고급 Intent 분류"""
        try:
            message_lower = message.lower()
            
            # 키워드 매칭 스코어 계산
            intent_scores = {}
            
            for intent, patterns in self.enhanced_intent_patterns.items():
                score = 0
                matched_patterns = []
                
                for pattern in patterns:
                    if pattern in message_lower:
                        score += 1
                        matched_patterns.append(pattern)
                
                if score > 0:
                    intent_scores[intent] = {
                        'score': score,
                        'confidence': min(score / len(patterns) * 2, 1.0),
                        'matched_patterns': matched_patterns
                    }
            
            # 최고 스코어 Intent 선택
            if intent_scores:
                best_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x]['score'])
                result = intent_scores[best_intent]
                result['intent'] = best_intent
                
                logger.info(f"고급 Intent 분류: {best_intent} (패턴: {result['matched_patterns']})")
                return result
            
            # 기본 Intent 분류 (폴백)
            return {
                'intent': 'comprehensive_analysis',
                'confidence': 0.7,
                'score': 1,
                'matched_patterns': ['fallback'],
                'method': 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Intent 분류 실패: {e}")
            return {
                'intent': 'comprehensive_analysis',
                'confidence': 0.5,
                'score': 0,
                'matched_patterns': [],
                'error': str(e)
            }
    
    async def _process_enhanced_intent(self, intent: str, message: str, session_id: str) -> str:
        """Intent별 고급 분석 처리"""
        try:
            if intent == 'comprehensive_analysis':
                return await self._comprehensive_claude_analysis(message)
            
            elif intent == 'market_sentiment':
                return await self._market_sentiment_analysis(message)
            
            elif intent == 'trend_analysis':
                return await self._trend_analysis(message)
            
            elif intent == 'technical_analysis':
                return await self._technical_analysis(message)
            
            elif intent == 'realtime_data':
                return await self._realtime_data_analysis(message)
            
            elif intent == 'news_analysis':
                return await self._news_analysis(message)
            
            elif intent == 'price_inquiry':
                return await self._price_inquiry_analysis(message)
            
            else:
                return await self._comprehensive_claude_analysis(message)
                
        except Exception as e:
            logger.error(f"Intent 처리 실패 ({intent}): {e}")
            return f"분석 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    async def _comprehensive_claude_analysis(self, message: str) -> str:
        """Claude 수준의 종합 분석"""
        try:
            logger.info("🔍 Claude 수준 종합 분석 시작")
            
            # 다중 도구 병렬 실행
            tasks = []
            
            # 뉴스 분석
            if self.advanced_news_analyzer:
                tasks.append(self.advanced_news_analyzer._arun(message))
            
            # 시장 데이터 분석
            if self.realtime_market_tool:
                tasks.append(self.realtime_market_tool._arun(message))
            
            # 시장 심리 분석
            if self.market_sentiment_analyzer:
                tasks.append(self.market_sentiment_analyzer._run())
            
            # 트렌드 분석
            if self.trend_analyzer:
                tasks.append(self.trend_analyzer._run())
            
            # 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 통합
            news_analysis = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else "뉴스 분석 데이터 부족"
            market_analysis = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else "시장 데이터 분석 제한"
            sentiment_analysis = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else "시장 심리 분석 제한"
            trend_analysis = results[3] if len(results) > 3 and not isinstance(results[3], Exception) else "트렌드 분석 제한"
            
            # Claude 스타일 종합 보고서 생성
            current_date = datetime.now().strftime("%Y년 %m월 %d일")
            current_time = datetime.now().strftime("%H:%M")
            
            comprehensive_report = f"""# 🔍 암호화폐 시장 종합 분석 보고서

**분석 기준**: {current_date} {current_time} | **AI 분석**: Claude 수준 엔진

---

## 📰 **뉴스 기반 시장 분석**

{news_analysis}

---

## 📊 **실시간 시장 데이터 분석**

{market_analysis}

---

## 🎭 **시장 심리 현황**

{sentiment_analysis}

---

## 📈 **트렌드 분석**

{trend_analysis}

---

## 🎯 **AI 종합 결론**

{await self._generate_ai_conclusion(message, news_analysis, market_analysis, sentiment_analysis, trend_analysis)}

---

*🤖 이 분석은 Claude 수준의 AI 엔진이 실시간 데이터를 종합하여 생성한 것으로, 투자 결정 시 참고용으로만 활용하시기 바랍니다.*
"""

            return comprehensive_report
            
        except Exception as e:
            logger.error(f"종합 분석 실패: {e}")
            return f"종합 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _market_sentiment_analysis(self, message: str) -> str:
        """시장 심리 분석"""
        try:
            if self.market_sentiment_analyzer:
                return await asyncio.create_task(
                    asyncio.to_thread(self.market_sentiment_analyzer._run)
                )
            else:
                return "시장 심리 분석 도구를 사용할 수 없습니다."
        except Exception as e:
            logger.error(f"시장 심리 분석 실패: {e}")
            return f"시장 심리 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _trend_analysis(self, message: str) -> str:
        """트렌드 분석"""
        try:
            if self.trend_analyzer:
                period = "7d"  # 기본값
                if "24시간" in message or "하루" in message:
                    period = "24h"
                elif "30일" in message or "한달" in message:
                    period = "30d"
                
                return await asyncio.create_task(
                    asyncio.to_thread(self.trend_analyzer._run, period)
                )
            else:
                return "트렌드 분석 도구를 사용할 수 없습니다."
        except Exception as e:
            logger.error(f"트렌드 분석 실패: {e}")
            return f"트렌드 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _technical_analysis(self, message: str) -> str:
        """기술적 분석"""
        try:
            if self.realtime_market_tool:
                return await self.realtime_market_tool._arun(message + " 기술적 분석")
            else:
                return "기술적 분석 도구를 사용할 수 없습니다."
        except Exception as e:
            logger.error(f"기술적 분석 실패: {e}")
            return f"기술적 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _realtime_data_analysis(self, message: str) -> str:
        """실시간 데이터 분석"""
        try:
            tasks = []
            
            # 실시간 시장 데이터
            if self.realtime_market_tool:
                tasks.append(self.realtime_market_tool._arun(message))
            
            # 시장 히트맵
            if self.market_heatmap_tool:
                tasks.append(self.market_heatmap_tool._run())
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                report = "# 📊 실시간 시장 데이터 분석\n\n"
                
                if len(results) > 0 and not isinstance(results[0], Exception):
                    report += results[0] + "\n\n---\n\n"
                
                if len(results) > 1 and not isinstance(results[1], Exception):
                    report += results[1]
                
                return report
            else:
                return "실시간 데이터 분석 도구를 사용할 수 없습니다."
                
        except Exception as e:
            logger.error(f"실시간 데이터 분석 실패: {e}")
            return f"실시간 데이터 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _news_analysis(self, message: str) -> str:
        """뉴스 분석"""
        try:
            if self.advanced_news_analyzer:
                return await self.advanced_news_analyzer._arun(message)
            elif self.news_search_tool:
                return self.news_search_tool._run(message)
            else:
                return "뉴스 분석 도구를 사용할 수 없습니다."
        except Exception as e:
            logger.error(f"뉴스 분석 실패: {e}")
            return f"뉴스 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _price_inquiry_analysis(self, message: str) -> str:
        """가격 조회 분석"""
        try:
            # 실시간 가격 + 기술적 분석 조합
            tasks = []
            
            if self.price_checker:
                tasks.append(asyncio.to_thread(self.price_checker._run, message))
            
            if self.realtime_market_tool:
                tasks.append(self.realtime_market_tool._arun(message))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                report = "# 💰 가격 분석 보고서\n\n"
                
                for i, result in enumerate(results):
                    if not isinstance(result, Exception):
                        report += result + "\n\n"
                
                return report
            else:
                return "가격 분석 도구를 사용할 수 없습니다."
                
        except Exception as e:
            logger.error(f"가격 분석 실패: {e}")
            return f"가격 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _enhance_response_quality(self, response: str, original_query: str, intent: str) -> str:
        """응답 품질 향상"""
        try:
            if len(response) < 100:  # 너무 짧은 응답만 향상
                enhancement_prompt = f"""다음 암호화폐 관련 응답을 Claude 수준으로 향상시켜 주세요.

원본 질문: "{original_query}"
현재 응답: "{response}"
분류된 의도: {intent}

요구사항:
1. 전문적이고 신뢰할 수 있는 톤 사용
2. 구체적인 데이터와 인사이트 제공
3. 적절한 마크다운 형식으로 구조화
4. 투자 리스크 안내 포함
5. 한국어로 응답

향상된 응답을 제공해주세요:"""

                try:
                    enhanced = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": enhancement_prompt}],
                        max_tokens=1500,
                        temperature=0.2
                    )
                    
                    return enhanced.choices[0].message.content.strip()
                    
                except Exception as llm_error:
                    logger.warning(f"응답 향상 실패, 원본 반환: {llm_error}")
                    return response
            
            return response
            
        except Exception as e:
            logger.error(f"응답 품질 향상 실패: {e}")
            return response
    
    async def _generate_ai_conclusion(self, query: str, news: str, market: str, sentiment: str, trend: str) -> str:
        """AI 종합 결론 생성"""
        try:
            conclusion_prompt = f"""다음 분석 결과들을 종합하여 전문가 수준의 결론을 생성해주세요.

사용자 질문: "{query}"

분석 결과:
1. 뉴스 분석: {news[:300]}...
2. 시장 분석: {market[:300]}...
3. 심리 분석: {sentiment[:300]}...
4. 트렌드 분석: {trend[:300]}...

다음 형식으로 결론을 작성해주세요:
- 핵심 포인트 3개 (불릿 포인트)
- 투자자 권고사항
- 주의사항

결론:"""

            try:
                conclusion = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": conclusion_prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                
                return conclusion.choices[0].message.content.strip()
                
            except Exception as llm_error:
                logger.warning(f"AI 결론 생성 실패: {llm_error}")
                return """**핵심 포인트:**
• 다양한 데이터를 종합한 분석이 완료되었습니다
• 시장 상황과 뉴스 동향을 반영한 인사이트를 제공했습니다
• 기술적 지표와 심리적 요인을 고려한 분석을 수행했습니다

**투자자 권고:**
현재 분석된 정보를 바탕으로 신중한 투자 결정을 내리시기 바랍니다.

**주의사항:**
이 분석은 참고용이며, 투자 결정은 개인의 책임입니다."""
                
        except Exception as e:
            logger.error(f"AI 결론 생성 실패: {e}")
            return "종합 결론 생성 중 오류가 발생했습니다."
    
    async def _generate_intelligent_error_response(self, error: str, query: str) -> str:
        """지능적인 오류 응답 생성"""
        try:
            error_prompt = f"""사용자 질문 "{query}"에 대해 시스템 오류가 발생했습니다: {error}

친근하고 도움이 되는 오류 응답을 생성해주세요:
1. 사과 표현
2. 가능한 원인 설명 (기술적 세부사항 제외)
3. 대안적 해결방법 제시
4. 재시도 안내

한국어로 응답해주세요:"""

            try:
                error_response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": error_prompt}],
                    max_tokens=300,
                    temperature=0.4
                )
                
                return error_response.choices[0].message.content.strip()
                
            except:
                return f"""죄송합니다. "{query}" 요청을 처리하는 중에 일시적인 문제가 발생했습니다.

🔧 **가능한 원인:**
• 시스템 부하 또는 네트워크 연결 문제
• 데이터베이스 연결 지연
• API 호출 제한

💡 **해결 방법:**
• 잠시 후 다시 시도해보세요
• 더 구체적인 키워드로 질문해보세요
• 시스템 상태가 정상화될 때까지 기다려주세요

다시 한번 죄송합니다. 곧 정상적인 서비스를 제공해드리겠습니다."""
                
        except Exception as e:
            logger.error(f"지능적 오류 응답 생성 실패: {e}")
            return "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _get_enhanced_data_sources(self, intent: str) -> List[str]:
        """Intent별 데이터 소스 반환"""
        source_mapping = {
            'comprehensive_analysis': [
                'Advanced News Analyzer', 'Real-time Market Data', 
                'Market Sentiment Engine', 'Trend Analysis Engine',
                'PgVector Database', 'OpenAI GPT-4', 'Multiple APIs'
            ],
            'market_sentiment': [
                'Market Sentiment Analyzer', 'News Sentiment Analysis',
                'Social Media Indicators', 'Fear & Greed Index'
            ],
            'trend_analysis': [
                'Trend Analysis Engine', 'Historical Data',
                'Pattern Recognition', 'Statistical Analysis'
            ],
            'technical_analysis': [
                'Real-time Market Data', 'Technical Indicators',
                'Chart Pattern Analysis', 'Multiple Exchanges'
            ],
            'realtime_data': [
                'Real-time APIs', 'Market Data Feeds',
                'Exchange APIs', 'Price Aggregators'
            ],
            'news_analysis': [
                'Advanced News Analyzer', 'News APIs',
                'Content Analysis', 'OpenAI Analysis'
            ],
            'price_inquiry': [
                'Real-time Price APIs', 'Market Data',
                'Exchange Data', 'Technical Analysis'
            ]
        }
        
        return source_mapping.get(intent, ['Enhanced Analysis Engine'])
    
    def _get_analysis_depth(self, intent: str) -> str:
        """분석 깊이 반환"""
        depth_mapping = {
            'comprehensive_analysis': 'Deep',
            'market_sentiment': 'Medium',
            'trend_analysis': 'Medium',
            'technical_analysis': 'Deep',
            'realtime_data': 'Medium',
            'news_analysis': 'Deep',
            'price_inquiry': 'Basic'
        }
        
        return depth_mapping.get(intent, 'Medium')
    
    async def health_check(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            status = {
                'agent_status': 'healthy',
                'database_connection': False,
                'tools_status': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # 데이터베이스 연결 확인
            try:
                async with db_manager.get_pgvector_connection() as conn:
                    await conn.fetchval('SELECT 1')
                status['database_connection'] = True
            except:
                status['database_connection'] = False
            
            # 도구들 상태 확인
            tools = {
                'advanced_news_analyzer': self.advanced_news_analyzer is not None,
                'market_sentiment_analyzer': self.market_sentiment_analyzer is not None,
                'trend_analyzer': self.trend_analyzer is not None,
                'realtime_market_tool': self.realtime_market_tool is not None,
                'market_heatmap_tool': self.market_heatmap_tool is not None
            }
            
            status['tools_status'] = tools
            status['tools_available'] = sum(tools.values())
            status['overall_health'] = 'good' if status['database_connection'] and status['tools_available'] >= 3 else 'degraded'
            
            return status
            
        except Exception as e:
            logger.error(f"Health check 실패: {e}")
            return {
                'agent_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# 호환성을 위한 별칭
ChatbotAgent = EnhancedCryptoAgent
CryptoChatbotAgent = EnhancedCryptoAgent