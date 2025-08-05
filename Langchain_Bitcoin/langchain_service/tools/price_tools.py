"""
암호화폐 가격 조회 Tool
Redis 캐싱을 활용한 실시간 가격 정보 제공
"""

import logging
import requests
from typing import Any, Dict, List
from langchain.tools import BaseTool
from pydantic import Field
from datetime import datetime
import sys
import os

# Redis 가격 서비스 import
try:
    from services.redis_price_service import RedisPriceService
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis 가격 서비스를 사용할 수 없습니다. 기본 API 모드로 실행됩니다.")

logger = logging.getLogger(__name__)

class CryptoPriceChecker(BaseTool):
    """암호화폐 실시간 가격 조회 도구"""
    
    name: str = "crypto_price_checker"
    description: str = """
    업비트 거래소에서 암호화폐의 실시간 가격 정보를 조회합니다.
    
    사용 예시:
    - "BTC" 또는 "비트코인"
    - "ETH" 또는 "이더리움"
    - "XRP" 또는 "리플"
    
    입력: 암호화폐 심볼 또는 이름
    출력: 현재 가격, 변동률, 거래량 등 상세 정보
    """
    
    def _run(self, coin_symbol: str) -> str:
        """가격 정보 조회 실행 (Redis 캐싱 우선)"""
        try:
            logger.info(f"💰 가격 조회 실행: {coin_symbol}")
            
            # Redis 서비스를 사용할 수 있는 경우
            if REDIS_AVAILABLE:
                return self._get_price_with_redis(coin_symbol)
            else:
                return self._get_price_direct_api(coin_symbol)

        except Exception as e:
            logger.error(f"❌ 가격 조회 실패: {e}")
            return f"가격 조회 중 오류가 발생했습니다: {str(e)}"

    def _get_price_with_redis(self, coin_symbol: str) -> str:
        """Redis 캐싱을 사용한 가격 조회"""
        try:
            logger.info(f"🔄 Redis 캐싱을 통한 가격 조회: {coin_symbol}")

            # Redis 서비스 초기화
            redis_service = RedisPriceService()

            # 가격 정보 조회 (캐시 우선)
            price_data = redis_service.get_price(coin_symbol)

            if not price_data:
                return f"{coin_symbol}의 가격 정보를 찾을 수 없습니다. 지원하지 않는 암호화폐이거나 API 연결에 문제가 있을 수 있습니다."

            # Redis 서비스의 데이터 형식으로 포맷팅
            formatted_info = self._format_redis_price_info(price_data, coin_symbol)

            logger.info(f"✅ Redis 캐싱 가격 조회 완료: {coin_symbol}")
            return formatted_info

        except Exception as e:
            logger.error(f"❌ Redis 가격 조회 실패: {e}")
            # Redis 실패 시 직접 API 호출로 폴백
            return self._get_price_direct_api(coin_symbol)

    def _get_price_direct_api(self, coin_symbol: str) -> str:
        """직접 API 호출을 통한 가격 조회 (폴백)"""
        try:
            logger.info(f"📡 직접 API 호출: {coin_symbol}")

            # 코인 심볼 정규화
            normalized_symbol = self._normalize_coin_symbol(coin_symbol)
            if not normalized_symbol:
                return f"지원하지 않는 암호화폐입니다: {coin_symbol}"
            
            # 업비트 API 호출
            market = f"KRW-{normalized_symbol}"
            price_data = self._fetch_upbit_price([market])
            
            if not price_data:
                return f"{coin_symbol}의 가격 정보를 찾을 수 없습니다."
            
            # 가격 정보 포맷팅
            formatted_info = self._format_price_info(price_data[0], coin_symbol)
            
            logger.info(f"✅ 직접 API 가격 조회 완료: {coin_symbol}")
            return formatted_info
            
        except Exception as e:
            logger.error(f"❌ 직접 API 가격 조회 실패: {e}")
            return f"가격 조회 중 오류가 발생했습니다: {str(e)}"
    
    def _normalize_coin_symbol(self, coin_input: str) -> str:
        """코인 입력을 표준 심볼로 변환"""
        coin_input = coin_input.upper().strip()
        
        # 한글명 → 심볼 매핑
        korean_to_symbol = {
            '비트코인': 'BTC',
            '이더리움': 'ETH',
            '리플': 'XRP',
            '라이트코인': 'LTC',
            '비트코인캐시': 'BCH',
            '이오스': 'EOS',
            '스텔라루멘': 'XLM',
            '에이다': 'ADA',
            '트론': 'TRX',
            '바이낸스코인': 'BNB',
            '체인링크': 'LINK',
            '폴카닷': 'DOT',
            '유니스왑': 'UNI',
            '솔라나': 'SOL',
            '아발란체': 'AVAX',
            '카르다노': 'ADA',
            '폴리곤': 'MATIC',
            '도지코인': 'DOGE',
            '시바이누': 'SHIB'
        }
        
        # 한글명 확인
        if coin_input in korean_to_symbol:
            return korean_to_symbol[coin_input]
        
        # 이미 심볼 형태인 경우
        valid_symbols = [
            'BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'EOS', 'XLM', 'ADA', 
            'TRX', 'BNB', 'LINK', 'DOT', 'UNI', 'SOL', 'AVAX', 
            'MATIC', 'DOGE', 'SHIB', 'ATOM', 'NEAR', 'ALGO', 'VET', 
            'ICP', 'FIL', 'AAVE', 'GRT', 'SAND', 'MANA', 'CRV'
        ]
        
        if coin_input in valid_symbols:
            return coin_input
        
        # 알 수 없는 입력
        return None
    
    def _fetch_upbit_price(self, markets: List[str]) -> List[Dict]:
        """업비트 API에서 가격 정보 조회"""
        try:
            url = "https://api.upbit.com/v1/ticker"
            params = {"markets": ",".join(markets)}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 업비트 API 호출 실패: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ 가격 데이터 처리 실패: {e}")
            return []
    
    def _format_redis_price_info(self, price_data: Dict, coin_name: str) -> str:
        """
Redis 서비스에서 가져온 가격 데이터 포맷팅"""
        try:
            # Redis 서비스 데이터 구조에 맞게 추출
            symbol = price_data.get('symbol', coin_name)
            korean_name = price_data.get('korean_name', coin_name)
            current_price = price_data.get('current_price', 0)
            change_rate = price_data.get('change_rate', 0)  # 이미 퍼센트 단위
            change = price_data.get('change', 'EVEN')
            high_price = price_data.get('high_price', 0)
            low_price = price_data.get('low_price', 0)
            volume_24h = price_data.get('volume_24h', 0)
            timestamp = price_data.get('timestamp', '')

            # 변동 방향 및 기호
            if change == 'RISE':
                change_symbol = "+"
                change_direction = "상승"
                change_emoji = "📈"
            elif change == 'FALL':
                change_symbol = "-"
                change_direction = "하락"
                change_emoji = "📉"
            else:
                change_symbol = ""
                change_direction = "보합"
                change_emoji = "➡️"

            # 시간 정보 포맷팅
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y년 %m월 %d일 %H시 %M분")
                except:
                    formatted_time = timestamp
            else:
                formatted_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")

            # 포맷된 정보 생성
            formatted_info = f"""💰 {korean_name} ({symbol}) 가격 정보

🏷️ **현재 가격**: {current_price:,}원
{change_emoji} **변동률**: {change_symbol}{change_rate:.2f}% {change_direction}
📊 **24시간 최고가**: {high_price:,}원
📊 **24시간 최저가**: {low_price:,}원
💹 **24시간 거래량**: {volume_24h:.2f} {symbol}
📅 **조회 시간**: {formatted_time}

📦 데이터 소스: Redis 캐시 (업비트 API 기반)
💡 실시간 캐싱된 데이터 제공"""

            return formatted_info

        except Exception as e:
            logger.error(f"❌ Redis 가격 정보 포맷팅 실패: {e}")
            return f"{coin_name}의 가격 정보를 표시하는 중 오류가 발생했습니다."

    def _format_price_info(self, price_data: Dict, coin_name: str) -> str:
        """기존 API 가격 데이터를 사용자 친화적 형태로 포맷팅"""
        try:
            # 기본 정보 추출
            current_price = price_data.get('trade_price', 0)
            change_rate = price_data.get('change_rate', 0) * 100
            change = price_data.get('change', 'EVEN')
            high_price = price_data.get('high_price', 0)
            low_price = price_data.get('low_price', 0)
            volume = price_data.get('acc_trade_volume_24h', 0)
            
            # 변동 방향 및 기호
            if change == 'RISE':
                change_symbol = "+"
                change_direction = "상승"
                change_emoji = "📈"
            elif change == 'FALL':
                change_symbol = "-"
                change_direction = "하락"
                change_emoji = "📉"
            else:
                change_symbol = ""
                change_direction = "보합"
                change_emoji = "➡️"
            
            # 시간 정보
            timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
            
            # 포맷된 정보 생성
            formatted_info = f"""💰 {coin_name} 가격 정보

🏷️ **현재 가격**: {current_price:,}원
{change_emoji} **변동률**: {change_symbol}{change_rate:.2f}% {change_direction}
📊 **24시간 최고가**: {high_price:,}원
📊 **24시간 최저가**: {low_price:,}원
💹 **24시간 거래량**: {volume:.2f} {coin_name}
📅 **조회 시간**: {timestamp}

💡 업비트 거래소 기준 실시간 데이터"""
            
            return formatted_info
            
        except Exception as e:
            logger.error(f"❌ 가격 정보 포맷팅 실패: {e}")
            return f"{coin_name}의 가격 정보를 표시하는 중 오류가 발생했습니다."
    
    async def _arun(self, coin_symbol: str) -> str:
        """비동기 가격 조회 실행"""
        return self._run(coin_symbol)


class MultiCoinPriceChecker(BaseTool):
    """여러 암호화폐 가격 동시 조회 도구"""
    
    name: str = "multi_coin_price_checker"
    description: str = """
    여러 암호화폐의 가격을 동시에 조회합니다.
    
    사용 예시:
    - "top 5 코인"
    - "주요 암호화폐"
    - "비트코인 이더리움 리플"
    
    입력: "top" 또는 여러 코인명
    출력: 여러 암호화폐의 가격 정보 요약
    """
    
    def _run(self, query: str) -> str:
        """여러 코인 가격 조회 실행 (Redis 캐싱 우선)"""
        try:
            logger.info(f"💰 다중 가격 조회 실행: {query}")
            
            # 쿼리 분석하여 코인 목록 결정
            if "top" in query.lower() or "주요" in query:
                # TOP 5 암호화폐
                coin_symbols = ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']
            else:
                # 쿼리에서 코인 추출
                coin_symbols = self._extract_coins_from_query(query)
                if not coin_symbols:
                    return "조회할 암호화폐를 찾을 수 없습니다. 'BTC', '이더리움' 등으로 입력해주세요."
            
            # Redis 서비스를 사용할 수 있는 경우
            if REDIS_AVAILABLE:
                return self._get_multiple_prices_with_redis(coin_symbols, query)
            else:
                return self._get_multiple_prices_direct_api(coin_symbols, query)

        except Exception as e:
            logger.error(f"❌ 다중 가격 조회 실패: {e}")
            return f"다중 가격 조회 중 오류가 발생했습니다: {str(e)}"

    def _get_multiple_prices_with_redis(self, coin_symbols: List[str], query: str) -> str:
        """Redis 캐싱을 사용한 다중 코인 가격 조회"""
        try:
            logger.info(f"🔄 Redis 캐싱을 통한 다중 가격 조회: {coin_symbols}")

            # Redis 서비스 초기화
            redis_service = RedisPriceService()

            # 다중 가격 정보 조회
            prices_data = redis_service.get_multiple_prices(coin_symbols)

            if not prices_data:
                return "가격 정보를 조회할 수 없습니다."

            # Redis 데이터 형식으로 포맷팅
            formatted_result = self._format_redis_multi_price_info(prices_data, query)

            logger.info(f"✅ Redis 캐싱 다중 가격 조회 완료: {len(prices_data)}개 코인")
            return formatted_result

        except Exception as e:
            logger.error(f"❌ Redis 다중 가격 조회 실패: {e}")
            # Redis 실패 시 직접 API 호출로 폴백
            return self._get_multiple_prices_direct_api(coin_symbols, query)

    def _get_multiple_prices_direct_api(self, coin_symbols: List[str], query: str) -> str:
        """직접 API 호출을 통한 다중 코인 가격 조회"""
        try:
            logger.info(f"📡 직접 API 호출: {coin_symbols}")

            # 업비트 마켓 형태로 변환
            markets = [f"KRW-{symbol}" for symbol in coin_symbols]
            
            # 가격 정보 조회
            price_data_list = self._fetch_upbit_price(markets)
            
            if not price_data_list:
                return "가격 정보를 조회할 수 없습니다."
            
            # 결과 포맷팅
            formatted_result = self._format_multi_price_info(price_data_list)
            
            logger.info(f"✅ 직접 API 다중 가격 조회 완료: {len(price_data_list)}개 코인")
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ 직접 API 다중 가격 조회 실패: {e}")
            return f"다중 가격 조회 중 오류가 발생했습니다: {str(e)}"
    
    def _extract_coins_from_query(self, query: str) -> List[str]:
        """쿼리에서 암호화폐 심볼 추출"""
        query_upper = query.upper()
        
        # 가능한 코인 목록
        possible_coins = {
            'BTC': ['BTC', '비트코인'],
            'ETH': ['ETH', '이더리움'],
            'XRP': ['XRP', '리플'],
            'ADA': ['ADA', '에이다', '카르다노'],
            'SOL': ['SOL', '솔라나'],
            'DOT': ['DOT', '폴카닷'],
            'LINK': ['LINK', '체인링크'],
            'LTC': ['LTC', '라이트코인'],
            'BCH': ['BCH', '비트코인캐시'],
            'UNI': ['UNI', '유니스왑']
        }
        
        found_coins = []
        for symbol, names in possible_coins.items():
            for name in names:
                if name in query_upper or name in query:
                    if symbol not in found_coins:
                        found_coins.append(symbol)
                    break
        
        return found_coins[:5]  # 최대 5개까지만
    
    def _fetch_upbit_price(self, markets: List[str]) -> List[Dict]:
        """업비트 API에서 여러 코인 가격 정보 조회"""
        try:
            url = "https://api.upbit.com/v1/ticker"
            params = {"markets": ",".join(markets)}
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 업비트 API 호출 실패: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ 가격 데이터 처리 실패: {e}")
            return []
    
    def _format_redis_multi_price_info(self, prices_data: Dict[str, Dict], query: str) -> str:
        """
Redis 서비스에서 가져온 다중 코인 가격 데이터 포맷팅"""
        try:
            timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")

            formatted_result = f"💰 암호화폐 가격 현황 ({timestamp})\n\n"

            # 가격순으로 정렬
            sorted_items = sorted(prices_data.items(), key=lambda x: x[1].get('current_price', 0), reverse=True)

            for i, (symbol, price_data) in enumerate(sorted_items, 1):
                korean_name = price_data.get('korean_name', symbol)
                current_price = price_data.get('current_price', 0)
                change_rate = price_data.get('change_rate', 0)  # 이미 퍼센트 단위
                change = price_data.get('change', 'EVEN')

                # 변동 방향 이모지
                if change == 'RISE':
                    change_emoji = "🔴"
                    change_symbol = "+"
                elif change == 'FALL':
                    change_emoji = "🔵"
                    change_symbol = "-"
                else:
                    change_emoji = "⚫"
                    change_symbol = ""

                formatted_result += f"{i}. **{korean_name} ({symbol})** {change_emoji}\n"
                formatted_result += f"   💵 {current_price:,}원\n"
                formatted_result += f"   📊 {change_symbol}{change_rate:.2f}%\n\n"

            formatted_result += f"📦 데이터 소스: Redis 캐시 (업비트 API 기반)\n"
            formatted_result += f"💡 실시간 캐싱된 데이터 제공"

            return formatted_result

        except Exception as e:
            logger.error(f"❌ Redis 다중 가격 정보 포맷팅 실패: {e}")
            return "가격 정보를 표시하는 중 오류가 발생했습니다."

    def _format_multi_price_info(self, price_data_list: List[Dict]) -> str:
        """기존 API 여러 코인의 가격 데이터를 포맷팅"""
        try:
            timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
            
            formatted_result = f"💰 암호화폐 가격 현황 ({timestamp})\n\n"
            
            for i, price_data in enumerate(price_data_list, 1):
                market = price_data.get('market', '')
                coin_symbol = market.replace('KRW-', '') if market else 'Unknown'
                
                current_price = price_data.get('trade_price', 0)
                change_rate = price_data.get('change_rate', 0) * 100
                change = price_data.get('change', 'EVEN')
                
                # 변동 방향 이모지
                if change == 'RISE':
                    change_emoji = "🔴"
                    change_symbol = "+"
                elif change == 'FALL':
                    change_emoji = "🔵"
                    change_symbol = "-"
                else:
                    change_emoji = "⚫"
                    change_symbol = ""
                
                formatted_result += f"{i}. **{coin_symbol}** {change_emoji}\n"
                formatted_result += f"   💵 {current_price:,}원\n"
                formatted_result += f"   📊 {change_symbol}{change_rate:.2f}%\n\n"
            
            formatted_result += "💡 업비트 거래소 기준 실시간 데이터"
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ 다중 가격 정보 포맷팅 실패: {e}")
            return "가격 정보를 표시하는 중 오류가 발생했습니다."
    
    async def _arun(self, query: str) -> str:
        """비동기 다중 가격 조회 실행"""
        return self._run(query)


class CoinMarketCapTool(BaseTool):
    """시가총액 기반 암호화폐 순위 조회 도구"""
    
    name: str = "coin_market_cap"
    description: str = """
    암호화폐 시가총액 순위를 조회합니다.
    
    사용 예시:
    - "시가총액 순위"
    - "암호화폐 랭킹"
    - "마켓캡 top 10"
    
    입력: "시가총액" 또는 "ranking" 관련 키워드
    출력: 주요 암호화폐들의 시가총액 기반 순위
    """
    
    def _run(self, query: str = "시가총액") -> str:
        """시가총액 순위 조회 실행 (Redis 캐싱 우선)"""
        try:
            logger.info(f"📊 시가총액 순위 조회 실행: {query}")
            
            # 주요 암호화폐들의 시가총액 순위 (고정 데이터)
            top_coins = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT', 'MATIC', 'AVAX']
            
            # Redis 서비스를 사용할 수 있는 경우
            if REDIS_AVAILABLE:
                return self._get_market_cap_with_redis(top_coins, query)
            else:
                return self._get_market_cap_direct_api(top_coins, query)

        except Exception as e:
            logger.error(f"❌ 시가총액 순위 조회 실패: {e}")
            return f"시가총액 순위 조회 중 오류가 발생했습니다: {str(e)}"

    def _get_market_cap_with_redis(self, top_coins: List[str], query: str) -> str:
        """Redis 캐싱을 사용한 시가총액 순위 조회"""
        try:
            logger.info(f"🔄 Redis 캐싱을 통한 시가총액 조회: {top_coins}")

            # Redis 서비스 초기화
            redis_service = RedisPriceService()

            # 다중 가격 정보 조회
            prices_data = redis_service.get_multiple_prices(top_coins)

            if not prices_data:
                return "시가총액 정보를 조회할 수 없습니다."

            # Redis 데이터 형식으로 포맷팅
            formatted_result = self._format_redis_market_cap_info(prices_data)

            logger.info(f"✅ Redis 캐싱 시가총액 조회 완료")
            return formatted_result

        except Exception as e:
            logger.error(f"❌ Redis 시가총액 조회 실패: {e}")
            # Redis 실패 시 직접 API 호출로 폴백
            return self._get_market_cap_direct_api(top_coins, query)

    def _get_market_cap_direct_api(self, top_coins: List[str], query: str) -> str:
        """직접 API 호출을 통한 시가총액 순위 조회"""
        try:
            logger.info(f"📡 직접 API 호출: {top_coins}")

            # 업비트에서 가격 정보 조회
            markets = [f"KRW-{symbol}" for symbol in top_coins]
            price_data_list = self._fetch_upbit_price(markets)
            
            if not price_data_list:
                return "시가총액 정보를 조회할 수 없습니다."
            
            # 결과 포맷팅
            formatted_result = self._format_market_cap_info(price_data_list)
            
            logger.info(f"✅ 직접 API 시가총액 조회 완료")
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ 직접 API 시가총액 조회 실패: {e}")
            return f"시가총액 순위 조회 중 오류가 발생했습니다: {str(e)}"
    
    def _fetch_upbit_price(self, markets: List[str]) -> List[Dict]:
        """업비트 API에서 여러 코인 가격 정보 조회"""
        try:
            url = "https://api.upbit.com/v1/ticker"
            params = {"markets": ",".join(markets)}
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 업비트 API 호출 실패: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ 가격 데이터 처리 실패: {e}")
            return []
    
    def _format_redis_market_cap_info(self, prices_data: Dict[str, Dict]) -> str:
        """
Redis 서비스에서 가져온 시가총액 순위 정보 포맷팅"""
        try:
            timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")

            formatted_result = f"📊 암호화폐 시가총액 순위 ({timestamp})\n\n"

            # 가격 기준으로 정렬 (시가총액 대신 가격으로 대체)
            sorted_items = sorted(prices_data.items(), key=lambda x: x[1].get('current_price', 0), reverse=True)

            for i, (symbol, price_data) in enumerate(sorted_items[:10], 1):
                korean_name = price_data.get('korean_name', symbol)
                current_price = price_data.get('current_price', 0)
                change_rate = price_data.get('change_rate', 0)  # 이미 퍼센트 단위
                change = price_data.get('change', 'EVEN')
                volume_24h = price_data.get('volume_24h', 0)

                # 등수에 따른 메달 이모지
                if i == 1:
                    rank_emoji = "🥇"
                elif i == 2:
                    rank_emoji = "🥈"
                elif i == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = f"{i}."

                # 변동 방향 이모지
                if change == 'RISE':
                    change_emoji = "📈"
                    change_symbol = "+"
                elif change == 'FALL':
                    change_emoji = "📉"
                    change_symbol = "-"
                else:
                    change_emoji = "➡️"
                    change_symbol = ""

                formatted_result += f"{rank_emoji} **{korean_name} ({symbol})** {change_emoji}\n"
                formatted_result += f"   💰 {current_price:,}원\n"
                formatted_result += f"   📊 {change_symbol}{change_rate:.2f}%\n"
                formatted_result += f"   📈 거래량: {volume_24h:.2f}\n\n"

            formatted_result += f"📦 데이터 소스: Redis 캐시 (업비트 API 기반)\n"
            formatted_result += f"💡 가격순 정렬, 실시간 캐싱된 데이터"

            return formatted_result

        except Exception as e:
            logger.error(f"❌ Redis 시가총액 정보 포맷팅 실패: {e}")
            return "시가총액 정보를 표시하는 중 오류가 발생했습니다."

    def _format_market_cap_info(self, price_data_list: List[Dict]) -> str:
        """기존 API 시가총액 순위 정보 포맷팅"""
        try:
            timestamp = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
            
            formatted_result = f"📊 암호화폐 시가총액 순위 ({timestamp})\n\n"
            
            # 가격 기준으로 정렬 (시가총액 대신 가격으로 대체)
            sorted_data = sorted(price_data_list, key=lambda x: x.get('trade_price', 0), reverse=True)
            
            for i, price_data in enumerate(sorted_data[:10], 1):
                market = price_data.get('market', '')
                coin_symbol = market.replace('KRW-', '') if market else 'Unknown'
                
                current_price = price_data.get('trade_price', 0)
                change_rate = price_data.get('change_rate', 0) * 100
                change = price_data.get('change', 'EVEN')
                volume = price_data.get('acc_trade_volume_24h', 0)
                
                # 등수에 따른 메달 이모지
                if i == 1:
                    rank_emoji = "🥇"
                elif i == 2:
                    rank_emoji = "🥈"
                elif i == 3:
                    rank_emoji = "🥉"
                else:
                    rank_emoji = f"{i}."
                
                # 변동 방향 이모지
                if change == 'RISE':
                    change_emoji = "📈"
                    change_symbol = "+"
                elif change == 'FALL':
                    change_emoji = "📉"
                    change_symbol = "-"
                else:
                    change_emoji = "➡️"
                    change_symbol = ""
                
                formatted_result += f"{rank_emoji} **{coin_symbol}** {change_emoji}\n"
                formatted_result += f"   💰 {current_price:,}원\n"
                formatted_result += f"   📊 {change_symbol}{change_rate:.2f}%\n"
                formatted_result += f"   📈 거래량: {volume:.2f}\n\n"
            
            formatted_result += "💡 업비트 거래소 기준, 가격순 정렬"
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ 시가총액 정보 포맷팅 실패: {e}")
            return "시가총액 정보를 표시하는 중 오류가 발생했습니다."
    
    async def _arun(self, query: str = "시가총액") -> str:
        """비동기 시가총액 순위 조회 실행"""
        return self._run(query)
