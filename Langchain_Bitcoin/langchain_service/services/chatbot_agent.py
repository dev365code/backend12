"""
크립토 챗봇 에이전트
LangChain을 활용한 AI Agent 구현
"""

import logging
import os
from typing import Dict, List, Optional
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# 로컬 imports
from langchain_service.tools.news_tools import CryptoNewsSearchTool, LatestNewsLookupTool, DatabaseStatsTool
from langchain_service.tools.price_tools import CryptoPriceChecker, MultiCoinPriceChecker, CoinMarketCapTool

logger = logging.getLogger(__name__)

class CryptoChatbotAgent:
    """크립토 챗봇 AI 에이전트"""

    def __init__(self, vector_service):
        """초기화"""
        self.vector_service = vector_service
        self.llm = None
        self.agent = None
        self.memory = None
        self.tools = []

        # 세션별 메모리 저장소
        self.session_memories = {}

    async def initialize(self):
        """에이전트 초기화"""
        try:
            logger.info("🤖 챗봇 에이전트 초기화 중...")

            # OpenAI LLM 초기화
            self._initialize_llm()

            # Tools 초기화
            self._initialize_tools()

            # 에이전트 초기화
            self._initialize_agent()

            logger.info("✅ 챗봇 에이전트 초기화 완료")

        except Exception as e:
            logger.error(f"❌ 챗봇 에이전트 초기화 실패: {e}")
            raise

    def _initialize_llm(self):
        """OpenAI LLM 초기화"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다")

            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,  # 정확성을 위해 낮은 온도
                max_tokens=1000,
                openai_api_key=api_key
            )

            logger.info("✅ OpenAI LLM 초기화 완료")

        except Exception as e:
            logger.error(f"❌ OpenAI LLM 초기화 실패: {e}")
            raise

    def _initialize_tools(self):
        """Tools 초기화"""
        try:
            # 벡터 서비스를 사용하는 도구들
            news_search_tool = CryptoNewsSearchTool(vector_service=self.vector_service)
            latest_news_tool = LatestNewsLookupTool(vector_service=self.vector_service)
            db_stats_tool = DatabaseStatsTool(vector_service=self.vector_service)

            # API 기반 도구들
            price_checker = CryptoPriceChecker()
            multi_price_checker = MultiCoinPriceChecker()
            market_cap_tool = CoinMarketCapTool()

            self.tools = [
                news_search_tool,
                latest_news_tool,
                db_stats_tool,
                price_checker,
                multi_price_checker,
                market_cap_tool
            ]

            logger.info(f"✅ {len(self.tools)}개 도구 초기화 완료")

        except Exception as e:
            logger.error(f"❌ Tools 초기화 실패: {e}")
            raise

    def _initialize_agent(self):
        """LangChain Agent 초기화"""
        try:
            # 메모리 초기화
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )

            # Intent-based 시스템 프롬프트 설정
            system_message = """당신은 암호화폐 전문 AI 어시스턴트입니다. 

🎯 **Intent 분류 시스템**: 먼저 사용자 질문의 의도를 다음 카테고리로 분류하세요:

[가능한 카테고리]
1. 실시간 시세 조회 (price_lookup)
2. 과거 데이터 분석 (historical_data)  
3. 뉴스 및 심리 분석 (news_sentiment)
4. 기술 분석 요청 (technical_analysis)
5. 일반 대화 또는 인사 (casual_chat)

📚 **Few-shot 예시**:
예시 1:

질문: "비트코인 지금 얼마야?"
의도: price_lookup
신뢰도: 0.97
이유: '지금'이라는 단어와 가격 확인 의도가 명확함.

예시 2:
질문: "20일 이평선과 현재 가격 차이 보여줘"
의도: technical_analysis
신뢰도: 0.92
이유: 이동평균선은 대표적인 기술 분석 지표.

예시 3:
질문: "어제 비트코인 종가가 어땠어?"
의도: historical_data
신뢰도: 0.95
이유: '어제'는 과거 데이터 요청을 의미함.

예시 4:
질문: "오늘 비트코인 관련 뉴스 요약해줘"
의도: news_sentiment
신뢰도: 0.90
이유: 뉴스 요청이 명시적이고 시점이 '오늘'로 한정됨.

예시 5:
질문: "안녕! 오늘 기분 어때?"
의도: casual_chat
신뢰도: 0.80
이유: 인사 및 감정 표현은 대화형 목적에 해당.

⚠️ **중요한 처리 규칙**:
1. **Intent 분류 후 해당하는 도구를 반드시 사용**
2. **도구 결과만을 사용하여 답변 구성** (추측 금지)
3. **항상 한국어로 답변**

📋 **Intent별 처리 방법**:

🔸 **news_sentiment** 분류 시:
- 'crypto_news_search' 도구를 반드시 사용하세요
- 도구가 반환한 결과를 절대 수정하거나 해석하지 마세요
- 도구 결과를 그대로 복사하여 답변으로 사용하세요
- ❌ 금지: 도구 결과를 요약하거나 재작성하는 것
- ✅ 필수: 도구 결과 텍스트를 그대로 출력

🔸 **price_lookup** 분류 시:
- 'crypto_price_checker' 또는 'multi_coin_price_checker' 도구 사용
- 실시간 가격 정보 제공

🔸 **historical_data** 분류 시:
- 'database_stats' 도구 사용하여 과거 데이터 조회

🔸 **technical_analysis** 분류 시:
- 관련 도구 조합하여 기술적 분석 제공

🔸 **casual_chat** 분류 시:
- 도구 없이 친근한 대화로 응답

✅ **성공적인 답변의 핵심**: Intent를 정확히 분류하고, 해당 도구의 결과를 충실히 반영하는 것입니다."""

            # Agent 초기화 (시스템 메시지 포함)
            self.agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.memory,
                verbose=True,  # 디버깅용 로그
                max_iterations=3,  # 무한 루프 방지
                handle_parsing_errors=True,  # 파싱 오류 처리
                agent_kwargs={
                    "system_message": system_message
                }
            )

            logger.info("✅ 에이전트 초기화 완료")

        except Exception as e:
            logger.error(f"❌ 에이전트 초기화 실패: {e}")
            raise

    async def process_message(self, message: str, session_id: str, use_rag: bool = True) -> Dict:
        """메시지 처리 메인 메서드"""
        try:
            logger.info(f"💬 메시지 처리 시작: {message[:50]}...")

            # 세션별 메모리 관리
            self._manage_session_memory(session_id)

            # RAG 사용 여부에 따른 처리
            if use_rag:
                response_text = await self._process_with_rag(message)
                data_sources = ["LangChain Agent", "Vector DB", "Real-time API"]
            else:
                response_text = await self._process_without_rag(message)
                data_sources = ["LLM Knowledge"]

            # 응답 후처리
            cleaned_response = self._clean_response(response_text)

            result = {
                'message': cleaned_response,
                'session_id': session_id,
                'data_sources': data_sources,
                'confidence_score': 0.85  # 기본 신뢰도
            }

            logger.info(f"✅ 메시지 처리 완료: {len(cleaned_response)}자 응답")
            return result

        except Exception as e:
            logger.error(f"💥 메시지 처리 중 오류: {e}")

            # 오류 응답 생성
            error_response = {
                'message': "죄송합니다. 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                'session_id': session_id,
                'data_sources': [],
                'error': str(e)
            }
            return error_response

    def _manage_session_memory(self, session_id: str):
        """세션별 메모리 관리"""
        if session_id not in self.session_memories:
            # 새로운 세션에 대한 메모리 생성
            self.session_memories[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            logger.debug(f"🆕 새로운 세션 메모리 생성: {session_id}")

        # 현재 세션의 메모리를 에이전트에 설정
        self.agent.memory = self.session_memories[session_id]

    async def _process_with_rag(self, message: str) -> str:
        """RAG를 사용한 메시지 처리"""
        try:
            logger.info(f"🔗 RAG 모드로 처리 중... 사용자 메시지: '{message[:100]}...'")
            logger.debug(f"도구 개수: {len(self.tools)}, 메모리 활성화: {self.agent.memory is not None}")

            # Intent-based 처리 지시사항
            korean_instruction = f"""다음 사용자 질문을 처리해주세요:

질문: {message}

🎯 **처리 단계**:
1. 먼저 질문의 의도를 5개 카테고리 중 하나로 분류하세요
2. Few-shot 예시를 참고하여 정확한 분류를 하세요
3. 분류된 Intent에 따라 적절한 도구를 사용하세요
4. 도구의 결과만을 사용하여 한국어로 답변하세요

⚠️ **극도로 중요한 규칙**: 
- Intent 분류는 반드시 수행하세요
- 해당 Intent에 맞는 도구를 사용하세요  
- 🚨 **절대적 금지**: 도구 결과를 수정, 요약, 해석, 번역하는 것
- 🚨 **절대적 필수**: 도구가 반환한 텍스트를 글자 그대로 복사하여 답변
- 모든 답변은 한국어로 작성하세요

🔥 **news_sentiment 분류 시 필수 행동**:
1. crypto_news_search 도구 호출
2. 도구 결과를 받음
3. 도구 결과 텍스트를 그대로 복사
4. 복사한 텍스트를 답변으로 출력 (수정 없이)
5. 절대로 "SEC가 승인했습니다" 같은 자체 해석 금지

📋 **예상 처리**:
- "비트코인 최신뉴스" → news_sentiment → crypto_news_search 사용
- "비트코인 가격" → price_lookup → crypto_price_checker 사용
- "안녕하세요" → casual_chat → 친근한 인사 응답"""

            logger.debug("LangChain Agent 실행 시작...")
            # LangChain Agent 실행
            result = self.agent.run(input=korean_instruction)
            logger.info(f"LangChain Agent 실행 완료: {len(result) if result else 0}자 응답")

            # LangChain의 이상한 마크다운 형태 정리
            result = result.replace('***', '')
            result = result.replace('```json', '')
            result = result.replace('```', '')

            # JSON 파싱 시도
            try:
                if '{' in result and '}' in result:
                    json_start = result.find('{')
                    json_end = result.rfind('}') + 1
                    json_str = result[json_start:json_end]

                    import json
                    parsed = json.loads(json_str)
                    if 'action_input' in parsed:
                        result = parsed['action_input']  # 실제 응답 메시지 추출
            except:
                pass  # JSON 파싱 실패 시 원본 사용

            return result

        except Exception as e:
            logger.error(f"❌ RAG 처리 실패: {e}")
            return f"죄송합니다. RAG 처리 중 오류가 발생했습니다: {str(e)}"

    async def _process_without_rag(self, message: str) -> str:
        """RAG 없이 메시지 처리"""
        try:
            logger.debug("🧠 LLM만으로 처리 중...")

            # 한국어 지시사항을 포함한 LLM 호출
            korean_prompt = f"""당신은 암호화폐 전문 AI 어시스턴트입니다. 
다음 질문에 대해 **반드시 한국어로** 친근하고 도움이 되는 방식으로 답변해주세요.

질문: {message}

답변 시 다음을 지켜주세요:
- 모든 답변은 한국어로 작성
- 친근하고 이해하기 쉽게 설명
- 이모지를 적절히 사용
- 암호화폐 관련 전문 지식 활용"""

            response = self.llm.predict(korean_prompt)

            return response

        except Exception as e:
            logger.error(f"❌ LLM 처리 실패: {e}")
            return "죄송합니다. 응답 생성 중 오류가 발생했습니다."

    def _clean_response(self, response: str) -> str:
        """응답 후처리 및 정리"""
        try:
            # 기본 정리
            cleaned = response.strip()

            # LangChain 메타데이터 제거
            patterns_to_remove = [
                '***',
                '```json',
                '```',
                'Action:',
                'Action Input:',
                'Observation:',
                'Thought:'
            ]

            for pattern in patterns_to_remove:
                cleaned = cleaned.replace(pattern, '')

            # 빈 줄 정리
            lines = cleaned.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned = '\n'.join(cleaned_lines)

            # 최소 길이 보장
            if len(cleaned) < 10:
                cleaned = "죄송합니다. 적절한 응답을 생성하지 못했습니다. 다시 시도해주세요."

            return cleaned

        except Exception as e:
            logger.error(f"❌ 응답 정리 실패: {e}")
            return response  # 원본 반환

    async def health_check(self) -> bool:
        """에이전트 상태 확인"""
        try:
            # LLM 연결 확인
            if not self.llm:
                return False

            # 에이전트 상태 확인
            if not self.agent:
                return False

            # 도구들 상태 확인
            if not self.tools:
                return False

            # 간단한 테스트 메시지 처리
            test_response = self.llm.predict("안녕하세요")
            if len(test_response) < 5:
                return False

            logger.debug("✅ 챗봇 에이전트 상태 정상")
            return True

        except Exception as e:
            logger.error(f"❌ 챗봇 에이전트 상태 확인 실패: {e}")
            return False
