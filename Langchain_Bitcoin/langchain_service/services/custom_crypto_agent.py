"""
Custom Crypto Agent - LangChain 완전 우회
규칙 기반 처리로 도구 결과 강제 사용
"""

import logging
import os
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain_openai import ChatOpenAI

# 로컬 imports
from langchain_service.tools.news_tools import CryptoNewsSearchTool, LatestNewsLookupTool, DatabaseStatsTool
from langchain_service.tools.price_tools import CryptoPriceChecker, MultiCoinPriceChecker, CoinMarketCapTool

logger = logging.getLogger(__name__)

class CustomCryptoAgent:
    """완전 커스텀 암호화폐 AI 에이전트 - LangChain 우회"""

    def __init__(self, vector_service):
        """초기화"""
        self.vector_service = vector_service
        self.llm = None
        
        # 도구들 초기화
        self.news_search_tool = None
        self.latest_news_tool = None
        self.db_stats_tool = None
        self.price_checker = None
        self.multi_price_checker = None
        self.market_cap_tool = None
        
        # 세션별 메모리 (간단한 대화 기록)
        self.session_histories = {}
        
        # 세션별 언어 설정 (기본값: 한글)
        self.session_languages = {}
        
        # Intent 분류를 위한 예시 문장들 (Sentence Embedding용)
        self.intent_examples = {
            'news_sentiment': [
                '비트코인 최신뉴스 알려줘',
                '암호화폐 관련 소식이 궁금해',
                '비트코인 뉴스 요약해줘',
                '최근 비트코인 기사 보여줘',
                '비트코인 트럼프 관련 뉴스',
                '코인 시장 분석 기사',
                'Bitcoin latest news please',
                'crypto news headlines today'
            ],
            'price_lookup': [
                '비트코인 지금 얼마야?',
                'BTC 현재 가격이 궁금해',
                '비트코인 시세 알려줘',
                '암호화폐 가격 확인하고 싶어',
                '비트코인 값 얼마인지 알려줘',
                '코인 현재 시세 보여줘',
                'What is Bitcoin price now?',
                'How much is BTC today?'
            ],
            'historical_data': [
                '어제 비트코인 종가가 어땠어?',
                '과거 비트코인 데이터 보고 싶어',
                '지난주 암호화폐 시세는?',
                '이전 가격 정보 알려줘',
                '작년 비트코인 최고가는?',
                '과거 통계 데이터 확인하고 싶어',
                'Yesterday Bitcoin closing price',
                'Historical crypto data'
            ],  
            'technical_analysis': [
                '20일 이평선과 현재 가격 차이 보여줘',
                '비트코인 차트 분석해줘',
                '기술적 지표 확인하고 싶어',
                'RSI 지수는 어떻게 돼?',
                'MACD 패턴 분석 부탁해',
                '추세선 분석 결과는?',
                'Bitcoin technical analysis',
                'Chart pattern analysis'
            ],
            'casual_chat': [
                '안녕하세요',
                '고마워요',
                '도움이 되었어요',
                '안녕히 가세요',
                '반갑습니다',
                '오늘 날씨 어때요?',
                'Hello there',
                'Thank you so much',
                'Good morning',
                'How are you?'
            ],
            'language_change': [
                '아니 한글말고 영어로 대답해줘',
                '영어로 답변해줘',
                '영어로 말해줘',
                'Please answer in English',
                'Switch to English',
                'Respond in English'
            ]
        }
        
        # 예시 문장들의 임베딩 저장소 (초기화 후 설정)
        self.intent_embeddings = {}

    async def initialize(self):
        """에이전트 초기화"""
        try:
            logger.info("🔥 Custom Crypto Agent 초기화 중...")

            # OpenAI LLM 초기화 (백업용)
            await self._initialize_llm()

            # 도구들 초기화
            await self._initialize_tools()

            # Intent 예시 문장들의 임베딩 초기화
            await self._initialize_intent_embeddings()

            logger.info("✅ Custom Crypto Agent 초기화 완료")

        except Exception as e:
            logger.error(f"❌ Custom Agent 초기화 실패: {e}")
            raise

    async def _initialize_llm(self):
        """OpenAI LLM 초기화 (백업용)"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다")

            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,  # 일관성을 위해 낮은 온도
                max_tokens=1500,  # ChatGPT 스타일 긴 응답을 위해 증가
                openai_api_key=api_key
            )

            logger.info("✅ Backup LLM 초기화 완료")

        except Exception as e:
            logger.error(f"❌ Backup LLM 초기화 실패: {e}")
            raise

    async def _initialize_tools(self):
        """도구들 초기화"""
        try:
            # 벡터 서비스 기반 도구들
            self.news_search_tool = CryptoNewsSearchTool(vector_service=self.vector_service)
            self.latest_news_tool = LatestNewsLookupTool(vector_service=self.vector_service)
            self.db_stats_tool = DatabaseStatsTool(vector_service=self.vector_service)

            # API 기반 도구들
            self.price_checker = CryptoPriceChecker()
            self.multi_price_checker = MultiCoinPriceChecker()
            self.market_cap_tool = CoinMarketCapTool()

            logger.info("✅ 모든 도구 초기화 완료")

        except Exception as e:
            logger.error(f"❌ 도구 초기화 실패: {e}")
            raise

    async def _initialize_intent_embeddings(self):
        """Intent 예시 문장들의 임베딩 초기화"""
        try:
            logger.info("🧠 Intent 임베딩 초기화 중...")
            
            for intent, examples in self.intent_examples.items():
                embeddings = []
                for example in examples:
                    try:
                        embedding = await self._get_sentence_embedding(example)
                        if embedding:
                            embeddings.append(embedding)
                    except Exception as e:
                        logger.warning(f"예시 문장 임베딩 실패: {example[:30]}... - {e}")
                        continue
                
                self.intent_embeddings[intent] = embeddings
                logger.debug(f"'{intent}' Intent: {len(embeddings)}개 임베딩 생성")
            
            total_embeddings = sum(len(embs) for embs in self.intent_embeddings.values())
            logger.info(f"✅ Intent 임베딩 초기화 완료: 총 {total_embeddings}개")
            
        except Exception as e:
            logger.error(f"❌ Intent 임베딩 초기화 실패: {e}")
            raise

    async def _get_sentence_embedding(self, text: str):
        """text-embedding-ada-002로 문장 임베딩 생성"""
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"임베딩 생성 실패 [{text[:30]}...]: {e}")
            return None

    def _cosine_similarity(self, vec1, vec2):
        """코사인 유사도 계산"""
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        except Exception as e:
            logger.error(f"유사도 계산 실패: {e}")
            return 0.0

    async def classify_intent_semantic(self, user_input: str) -> Dict[str, Any]:
        """Sentence Embedding 기반 Intent 분류"""
        try:
            logger.debug(f"🧠 의미 기반 Intent 분류 시작: '{user_input[:50]}...'")
            
            # 사용자 입력의 임베딩 생성
            user_embedding = await self._get_sentence_embedding(user_input)
            if not user_embedding:
                logger.warning("사용자 입력 임베딩 생성 실패, 키워드 방식으로 폴백")
                return self.classify_intent_fallback(user_input)
            
            # 각 Intent별 최대 유사도 계산
            intent_similarities = {}
            
            for intent, example_embeddings in self.intent_embeddings.items():
                max_similarity = 0.0
                best_example_idx = -1
                
                for idx, example_embedding in enumerate(example_embeddings):
                    if example_embedding:
                        similarity = self._cosine_similarity(user_embedding, example_embedding)
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_example_idx = idx
                
                intent_similarities[intent] = {
                    'similarity': max_similarity,
                    'best_example_idx': best_example_idx
                }
            
            # 가장 유사한 Intent 선택
            best_intent = max(intent_similarities.keys(), 
                            key=lambda x: intent_similarities[x]['similarity'])
            best_similarity = intent_similarities[best_intent]['similarity']
            
            # 신뢰도가 너무 낮으면 키워드 방식으로 폴백
            if best_similarity < 0.5:
                logger.info(f"의미 분류 신뢰도 낮음 ({best_similarity:.3f}), 키워드 방식으로 폴백")
                return self.classify_intent_fallback(user_input)
            
            # 최고 유사도 예시 문장 로깅
            best_example_idx = intent_similarities[best_intent]['best_example_idx']
            if best_example_idx >= 0:
                best_example = self.intent_examples[best_intent][best_example_idx]
                logger.debug(f"가장 유사한 예시: '{best_example}' (유사도: {best_similarity:.3f})")
            
            logger.info(f"🎯 의미 기반 Intent 분류: {best_intent} (신뢰도: {best_similarity:.3f})")
            
            return {
                'intent': best_intent,
                'score': best_similarity,
                'confidence': best_similarity,
                'method': 'semantic_embedding',
                'similarities': {k: v['similarity'] for k, v in intent_similarities.items()},
                'matched_patterns': [f"semantic_match_{best_similarity:.3f}"]
            }
            
        except Exception as e:
            logger.error(f"의미 기반 분류 실패: {e}")
            return self.classify_intent_fallback(user_input)

    def classify_intent_fallback(self, user_input: str) -> Dict[str, Any]:
        """키워드 기반 폴백 분류 (간단한 규칙)"""
        user_input_lower = user_input.lower()
        
        # 특정 문장 정확히 매칭 (언어 변경)
        if user_input.strip() == "아니 한글말고 영어로 대답해줘":
            intent = 'language_change'
        # 간단한 키워드 매칭
        elif any(word in user_input_lower for word in ['뉴스', 'news', '소식', '기사', '트럼프']):
            intent = 'news_sentiment'
        elif any(word in user_input_lower for word in ['가격', '얼마', '시세', 'price', 'btc', '비트코인']):
            intent = 'price_lookup' 
        elif any(word in user_input_lower for word in ['어제', '과거', 'yesterday', 'historical']):
            intent = 'historical_data'
        elif any(word in user_input_lower for word in ['차트', '분석', 'chart', 'technical', '이평선', '종합', 'rsi', 'macd', '그래프', '캔들', '거래량']):
            intent = 'technical_analysis'
        elif any(word in user_input_lower for word in ['안녕', 'hello', '감사', 'thank', '고마워']):
            intent = 'casual_chat'
        else:
            intent = 'casual_chat'  # 기본값
        
        return {
            'intent': intent,
            'score': 0.6,
            'confidence': 0.6,
            'method': 'keyword_fallback',
            'matched_patterns': ['fallback_rule']
        }

    async def classify_intent(self, user_input: str) -> Dict[str, Any]:
        """Intent 분류 - Sentence Embedding 기반 (기본)"""
        return await self.classify_intent_semantic(user_input)

    async def process_message(self, message: str, session_id: str, use_rag: bool = True) -> Dict:
        """메시지 처리 메인 메서드 - 완전 커스텀 로직"""
        try:
            logger.info(f"🔥 Custom Agent 메시지 처리 시작: {message[:50]}...")

            # 1단계: Intent 분류
            intent_result = await self.classify_intent(message)
            intent = intent_result['intent']
            confidence = intent_result['confidence']

            logger.info(f"📊 분류된 Intent: {intent} (신뢰도: {confidence:.2f})")

            # 2단계: Intent별 직접 처리
            response_text = await self._process_by_intent(intent, message, session_id)

            # 3단계: 응답 구성
            result = {
                'message': response_text,
                'session_id': session_id,
                'data_sources': self._get_data_sources(intent),
                'confidence_score': confidence,
                'intent': intent,
                'processing_method': 'custom_agent'
            }

            logger.info(f"✅ Custom Agent 처리 완료: {len(response_text)}자 응답")
            return result

        except Exception as e:
            logger.error(f"💥 Custom Agent 처리 중 오류: {e}")
            
            # 오류 응답
            error_response = {
                'message': "죄송합니다. 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                'session_id': session_id,
                'data_sources': [],
                'error': str(e)
            }
            return error_response

    async def _process_by_intent(self, intent: str, message: str, session_id: str) -> str:
        """Intent별 직접 처리"""
        
        if intent == 'news_sentiment':
            return self._handle_news_query(message, session_id)
        
        elif intent == 'price_lookup':
            return self._handle_price_query(message)
        
        elif intent == 'historical_data':
            return self._handle_historical_query(message)
        
        elif intent == 'technical_analysis':
            return self._handle_chart_query(message)
        
        elif intent == 'casual_chat':
            return self._handle_casual_chat(message, session_id)
        
        elif intent == 'language_change':
            return self._handle_language_change(message, session_id)
        
        else:
            return "죄송합니다. 질문을 이해하지 못했습니다. 다시 한번 말씀해주세요."

    def _handle_news_query(self, message: str, session_id: str) -> str:
        """뉴스 관련 질문 처리 - 뉴스만 응답"""
        try:
            logger.info(f"📰 뉴스 쿼리 처리: {message}")
            
            # 차트 관련 키워드가 있으면 차트 생성
            if any(keyword in message.lower() for keyword in ['차트', 'chart', '그래프', '이동평균', 'rsi', 'macd']):
                return self._handle_chart_query(message)
            
            # 뉴스만 검색
            raw_news_data = self.news_search_tool._run(message)
            
            # 세션 언어 확인
            session_language = self.session_languages.get(session_id, 'ko')  # 기본값: 한글
            
            # ChatGPT 스타일로 뉴스 재구성
            enhanced_response = self._enhance_news_response(raw_news_data, message, session_language)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"❌ 뉴스 처리 실패: {e}")
            return f"죄송합니다. 뉴스 검색 중 오류가 발생했습니다: {str(e)}"
    
    def _handle_chart_query(self, message: str) -> str:
        """차트 관련 질문 처리 - Upbit API + Plotly 전문 차트"""
        try:
            logger.info(f"📊 차트 쿼리 처리: {message}")
            
            from langchain_service.services.upbit_chart_generator import UpbitChartGenerator
            from datetime import datetime
            
            chart_gen = UpbitChartGenerator()
            
            # 차트 기간 결정
            days = 30  # 기본값
            if '1년' in message or '365일' in message or '12개월' in message:
                days = 365
            elif '6개월' in message or '180일' in message:
                days = 180
            elif '3개월' in message or '90일' in message:
                days = 90
            elif '1개월' in message or '30일' in message:
                days = 30
            elif '1주일' in message or '7일' in message:
                days = 7
            
            # 차트 타입 결정
            if any(keyword in message.lower() for keyword in ['종합', '전체', 'rsi', 'macd', '거래량', '지표']):
                # 종합 차트 (모든 지표 포함)
                chart_base64 = chart_gen.generate_comprehensive_chart("KRW-BTC", days)
                chart_type = "종합 기술 분석"
            else:
                # 간단 차트 (가격 + 이동평균)
                chart_base64 = chart_gen.generate_simple_price_chart("KRW-BTC", days)
                chart_type = "가격 & 이동평균"
            
            if chart_base64.startswith("data:image"):
                # 시장 분석 데이터 추가
                analysis = chart_gen.get_market_analysis("KRW-BTC", days)
                
                chart_response = f"""📊 비트코인 {chart_type} 차트

차트 기간: 최근 {days}일  
생성 시간: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")}  
데이터 소스: Upbit API (실시간)

{chart_base64}

💰 현재 시장 상황

"""
                
                # 분석 데이터가 있으면 추가
                if analysis:
                    current_price = analysis.get('current_price', 0)
                    price_change = analysis.get('price_change_24h', 0)
                    change_emoji = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
                    
                    chart_response += f"""- **현재가**: {current_price:,.0f}원
- **24시간 변동**: {change_emoji} {price_change:+.2f}%
- **24시간 거래량**: {analysis.get('volume_24h', 0):,.2f} BTC

### 📊 **이동평균선 현황**
- **5일선**: {analysis.get('ma5', 0):,.0f}원
- **20일선**: {analysis.get('ma20', 0):,.0f}원  
- **60일선**: {analysis.get('ma60', 0):,.0f}원
- **120일선**: {analysis.get('ma120', 0):,.0f}원

### 🎯 **기술적 지표**
- **RSI(14)**: {analysis.get('rsi', 0):.1f} - {"과매수" if analysis.get('rsi', 50) > 70 else "과매도" if analysis.get('rsi', 50) < 30 else "중립"}
- **MACD**: {analysis.get('macd', 0):.2f}
- **Signal**: {analysis.get('macd_signal', 0):.2f}

"""

                chart_response += f"""## 📊 **차트 구성 요소**

### 🕯️ **캔들스틱 차트**
- 빨간색: 상승 (종가 > 시가)
- 파란색: 하락 (종가 < 시가)

### 📈 **이동평균선**
- 🔴 **5일선**: 초단기 추세
- 🟢 **20일선**: 단기 추세  
- 🔵 **60일선**: 중기 추세
- 🟡 **120일선**: 장기 추세

### 📊 **기술적 지표** (종합 차트인 경우)
- **거래량**: 시장 참여도 표시
- **RSI**: 과매수(70↑)/과매도(30↓) 판단
- **MACD**: 추세 전환 시점 포착

## 💡 **차트 분석 가이드**

### 🎯 **이동평균선 활용법**
- 가격이 모든 이평선 위 → 강한 상승세
- 가격이 모든 이평선 아래 → 강한 하락세
- 단기선이 장기선 상향 돌파 → 골든크로스 (매수 신호)
- 단기선이 장기선 하향 돌파 → 데드크로스 (매도 신호)

### ⚡ **RSI 활용법**
- 70 이상: 과매수 구간 (조정 가능성)
- 30 이하: 과매도 구간 (반등 가능성)
- 50 근처: 중립 구간

### 🔄 **MACD 활용법**
- MACD > Signal: 상승 모멘텀
- MACD < Signal: 하락 모멘텀
- 히스토그램이 0선 상향 돌파: 매수 신호

---

*🚀 Upbit API 실시간 데이터 기반 전문 차트 분석*"""
                
                return chart_response
            else:
                return f"차트 생성 실패: {chart_base64}"
                
        except Exception as e:
            logger.error(f"❌ 차트 처리 실패: {e}")
            return f"차트 생성 중 오류가 발생했습니다: {str(e)}"

    def _handle_price_query(self, message: str) -> str:
        """가격 관련 질문 처리"""
        try:
            logger.info(f"💰 가격 쿼리 처리: {message}")
            
            # 코인 이름 추출 (간단한 규칙)
            coin_name = self._extract_coin_name(message)
            
            # 가격 도구 직접 호출
            tool_result = self.price_checker._run(coin_name)
            
            logger.info(f"✅ 가격 도구 결과: {tool_result[:100]}...")
            
            return tool_result
            
        except Exception as e:
            logger.error(f"❌ 가격 처리 실패: {e}")
            return f"죄송합니다. 가격 조회 중 오류가 발생했습니다: {str(e)}"

    def _handle_historical_query(self, message: str) -> str:
        """과거 데이터 관련 질문 처리"""
        try:
            logger.info(f"📊 과거 데이터 쿼리 처리: {message}")
            
            # 데이터베이스 통계 도구 사용
            tool_result = self.db_stats_tool._run("")
            
            return f"📊 **데이터베이스 통계 정보**\n\n{tool_result}"
            
        except Exception as e:
            logger.error(f"❌ 과거 데이터 처리 실패: {e}")
            return f"죄송합니다. 과거 데이터 조회 중 오류가 발생했습니다: {str(e)}"

    def _handle_technical_query(self, message: str) -> str:
        """기술적 분석 관련 질문 처리"""
        try:
            logger.info(f"📈 기술 분석 쿼리 처리: {message}")
            
            # 시장 정보 도구 사용
            tool_result = self.market_cap_tool._run("bitcoin")
            
            return f"📈 **기술 분석 정보**\n\n{tool_result}"
            
        except Exception as e:
            logger.error(f"❌ 기술 분석 처리 실패: {e}")
            return f"죄송합니다. 기술 분석 중 오류가 발생했습니다: {str(e)}"

    def _handle_casual_chat(self, message: str, session_id: str) -> str:
        """일반 대화 처리"""
        try:
            logger.info(f"💬 일반 대화 처리: {message}")
            
            # 간단한 규칙 기반 응답
            message_lower = message.lower()
            
            if any(greeting in message_lower for greeting in ['안녕', 'hello', 'hi']):
                return "안녕하세요! 😊 암호화폐에 대해 궁금한 것이 있으시면 언제든 물어보세요!"
            
            elif any(thanks in message_lower for thanks in ['감사', '고마워', 'thanks', 'thank you']):
                return "천만에요! 😊 도움이 되어서 기쁩니다. 또 다른 질문이 있으시면 언제든 말씀해주세요!"
            
            elif any(help_word in message_lower for help_word in ['도움', 'help', '뭐해']):
                return """💡 **저는 이런 것들을 도와드릴 수 있어요:**

📰 **뉴스 검색**: "비트코인 최신뉴스", "암호화폐 소식"
💰 **가격 조회**: "비트코인 가격", "이더리움 얼마야"
📊 **데이터 분석**: "과거 데이터", "통계 정보"
📈 **기술 분석**: "차트 분석", "기술적 지표"

무엇을 도와드릴까요? 😊"""
            
            else:
                return "네, 말씀해주세요! 암호화폐 관련해서 궁금한 것이 있으시면 언제든 물어보세요. 😊"
                
        except Exception as e:
            logger.error(f"❌ 일반 대화 처리 실패: {e}")
            return "안녕하세요! 😊 무엇을 도와드릴까요?"

    def _handle_language_change(self, message: str, session_id: str) -> str:
        """언어 변경 처리"""
        try:
            logger.info(f"🌐 언어 변경 요청: {message} (세션: {session_id})")
            
            # 세션의 언어를 영어로 변경
            self.session_languages[session_id] = 'en'
            
            return "Sure! I'll respond in English from now on. Feel free to ask me about cryptocurrency news, prices, or technical analysis! 🚀"
            
        except Exception as e:
            logger.error(f"❌ 언어 변경 처리 실패: {e}")
            return "알겠습니다! 앞으로 영어로 대답하겠습니다."

    def _extract_coin_name(self, message: str) -> str:
        """메시지에서 코인 이름 추출"""
        message_lower = message.lower()
        
        # 코인 이름 매핑
        coin_mapping = {
            'btc': 'BTC',
            'bitcoin': 'BTC', 
            '비트코인': 'BTC',
            'eth': 'ETH',
            'ethereum': 'ETH',
            '이더리움': 'ETH',
            'xrp': 'XRP',
            '리플': 'XRP'
        }
        
        for keyword, coin_code in coin_mapping.items():
            if keyword in message_lower:
                return coin_code
        
        # 기본값
        return 'BTC'

    def _create_integrated_analysis(self, news_data: str, price_data: str, user_query: str) -> str:
        """통합 Claude 수준 분석 보고서 생성 (차트 포함)"""
        try:
            from datetime import datetime
            current_date = datetime.now().strftime("%Y년 %m월 %d일")
            current_time = datetime.now().strftime("%H:%M")
            
            # 차트 생성 여부 확인
            chart_html = ""
            if any(keyword in user_query.lower() for keyword in ['차트', 'chart', '그래프', '가격', '시세']):
                try:
                    from services.chart_generator import ChartGenerator
                    chart_gen = ChartGenerator()
                    chart_base64 = chart_gen.generate_simple_price_chart("BTC", 7)
                    if chart_base64.startswith("data:image"):
                        chart_html = f'<img src="{chart_base64}" alt="비트코인 가격 차트" style="max-width:100%; height:auto;">'
                except Exception as chart_error:
                    logger.warning(f"차트 생성 실패: {chart_error}")
                    chart_html = "📊 차트 생성 중 오류가 발생했습니다."
            
            # 통합 분석 보고서
            integrated_report = f"""# 🔍 비트코인 종합 분석 보고서

**분석 기준**: {current_date} {current_time} | **AI 분석**: Claude 수준 엔진

---

## 📰 **최신 뉴스 분석**

{news_data}

---

## 💰 **실시간 가격 정보**

{price_data}

---

## 📊 **가격 차트**

{chart_html}

---

## 📈 **시장 종합 평가**

### 🎯 **핵심 포인트**
• 최신 뉴스 동향을 반영한 시장 분석
• 실시간 가격 데이터와 뉴스의 상관관계 파악
• 기술적 분석을 통한 차트 패턴 확인
• 투자자 관점에서의 시사점 도출

### 💡 **투자 인사이트**
현재 수집된 뉴스와 가격 데이터를 종합하면, 시장 참여자들은 다양한 요인들을 고려한 신중한 접근이 필요한 상황입니다.

### ⚠️ **주의사항**
이 분석은 AI가 수집된 데이터를 기반으로 생성한 것으로, 투자 결정 시 추가적인 정보 확인과 전문가 상담이 필요합니다.

---

*🤖 Claude 수준 AI 분석 엔진으로 생성된 종합 보고서*"""

            return integrated_report
            
        except Exception as e:
            logger.error(f"통합 분석 생성 실패: {e}")
            return news_data  # 실패 시 기본 뉴스 데이터 반환

    def _enhance_news_response(self, raw_news_data: str, user_query: str, language: str = 'ko') -> str:
        """뉴스 데이터를 ChatGPT 스타일로 고급화"""
        try:
            logger.info(f"🎨 뉴스 응답 고급화 시작 (언어: {language})")
            
            # LLM이 없으면 원본 반환
            if not self.llm:
                logger.warning("LLM이 초기화되지 않아 원본 뉴스 데이터 반환")
                return raw_news_data
            
            # 현재 날짜 가져오기
            if language == 'en':
                current_date = datetime.now().strftime("%B %d, %Y")
            else:
                current_date = datetime.now().strftime("%Y년 %m월 %d일")
            
            # 언어별 ChatGPT 스타일 변환 프롬프트
            if language == 'en':
                enhancement_prompt = f"""Please reorganize the following Bitcoin news data in a professional ChatGPT style.

User Question: "{user_query}"
Raw News Data:
{raw_news_data}

**Requirements:**
1. Write an intro based on today's date ({current_date})
2. Structure as follows:
   - Intro: "Here's a summary of the latest Bitcoin-related news as of {current_date}:"
   - Divider: "⸻"
   - "📰 Latest News Headlines" section
   - Summarize each news item with numbers (1-2 sentences, concise)
   - Add insights with "→" arrows for important points
   - Divider: "⸻"  
   - "📈 Market Trends & Insights" section
   - Summarize overall trends in 2-3 bullet points

3. **Style Guide:**
   - Use emojis appropriately (📰, 📈, →, •)
   - Clean structure and spacing
   - Professional and trustworthy tone
   - Concise key information only
   - Keep original news links/sources but integrate naturally

Please respond in English only."""
            else:
                enhancement_prompt = f"""다음 비트코인 뉴스 데이터를 ChatGPT 스타일로 전문적이고 예쁘게 재구성해주세요.

사용자 질문: "{user_query}"
원본 뉴스 데이터:
{raw_news_data}

**요구사항:**
1. 오늘 날짜({current_date}) 기준으로 인트로 작성
2. 다음 구조로 구성:
   - 인트로: "다음은 오늘 기준({current_date}) 최신 비트코인 관련 주요 뉴스 요약입니다:"
   - 구분선: "⸻"
   - "📰 주요 최신 뉴스" 섹션
   - 각 뉴스를 번호와 함께 요약 (1-2문장으로 간결하게)
   - 중요한 포인트는 "→" 화살표로 인사이트 추가
   - 구분선: "⸻"
   - "📈 시장 동향 & 인사이트" 섹션
   - 전체적인 트렌드를 2-3개 불릿 포인트로 요약

3. **스타일 가이드:**
   - 이모지 적절히 사용 (📰, 📈, →, •)
   - 깔끔한 구조와 간격
   - 전문적이고 신뢰할 수 있는 톤
   - 핵심 정보만 간결하게
   - 원본 뉴스의 링크나 출처는 유지하되 자연스럽게 통합

4. **번역 및 현지화:**
   - 영문 뉴스는 자연스러운 한국어로 번역
   - 금액은 한국 독자가 이해하기 쉽게 표현
   - 전문 용어는 한국어 병기

한국어로만 답변해주세요."""

            # LLM으로 뉴스 재구성
            enhanced_response = self.llm.predict(enhancement_prompt)
            
            logger.info(f"✅ 뉴스 응답 고급화 완료: {len(enhanced_response)}자")
            return enhanced_response.strip()
            
        except Exception as e:
            logger.error(f"❌ 뉴스 응답 고급화 실패: {e}")
            # 실패 시 원본 데이터 반환
            return raw_news_data

    def _get_data_sources(self, intent: str) -> List[str]:
        """Intent별 데이터 소스 반환"""
        source_mapping = {
            'news_sentiment': ['Vector DB', 'PostgreSQL', 'News APIs', 'OpenAI GPT-3.5'],
            'price_lookup': ['Real-time Price APIs', 'CoinMarketCap'],
            'historical_data': ['PostgreSQL Database', 'Historical Data'],
            'technical_analysis': ['Market Data APIs', 'Technical Indicators'],
            'casual_chat': ['Rule-based Responses']
        }
        
        return source_mapping.get(intent, ['Custom Agent'])

    async def health_check(self) -> bool:
        """에이전트 상태 확인"""
        try:
            # 도구들 상태 확인
            if not (self.news_search_tool and self.price_checker):
                return False

            logger.debug("✅ Custom Agent 상태 정상")
            return True

        except Exception as e:
            logger.error(f"❌ Custom Agent 상태 확인 실패: {e}")
            return False

# 기존 ChatbotAgent 클래스와 호환성을 위한 별칭
ChatbotAgent = CustomCryptoAgent
CryptoChatbotAgent = CustomCryptoAgent