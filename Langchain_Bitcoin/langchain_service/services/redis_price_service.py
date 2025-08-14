#!/usr/bin/env python3
"""
Redis 기반 암호화폐 가격 캐싱 서비스
Upbit API와 연동하여 실시간 가격 정보를 캐싱하고 제공
"""

import json
import logging
import redis
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class RedisPriceService:
    """Redis 기반 암호화폐 가격 캐싱 서비스"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, db: int = 0):
        """초기화"""
        self.redis_client = None
        self.upbit_base_url = "https://api.upbit.com/v1"
        
        # Redis 연결
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=db, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            logger.info("✅ Redis 연결 성공")
        except Exception as e:
            logger.error(f"❌ Redis 연결 실패: {e}")
            self.redis_client = None
        
        # 캐시 설정
        self.cache_ttl = 30  # 30초 캐시
        self.batch_update_interval = 20  # 20초마다 배치 업데이트
        
        # 지원 코인 목록
        self.supported_coins = [
            'BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'EOS', 'XLM', 'ADA', 
            'TRX', 'BNB', 'LINK', 'DOT', 'UNI', 'SOL', 'AVAX', 
            'MATIC', 'DOGE', 'SHIB', 'ATOM', 'NEAR', 'ALGO', 'VET', 
            'ICP', 'FIL', 'AAVE', 'GRT', 'SAND', 'MANA', 'CRV'
        ]
        
        # 한글명 매핑
        self.korean_names = {
            'BTC': '비트코인',
            'ETH': '이더리움', 
            'XRP': '리플',
            'LTC': '라이트코인',
            'BCH': '비트코인캐시',
            'EOS': '이오스',
            'XLM': '스텔라루멘',
            'ADA': '에이다',
            'TRX': '트론',
            'BNB': '바이낸스코인',
            'LINK': '체인링크',
            'DOT': '폴카닷',
            'UNI': '유니스왑',
            'SOL': '솔라나',
            'AVAX': '아발란체',
            'MATIC': '폴리곤',
            'DOGE': '도지코인',
            'SHIB': '시바이누'
        }
    
    def get_cache_key(self, symbol: str, data_type: str = "price") -> str:
        """캐시 키 생성"""
        return f"crypto:{data_type}:{symbol.upper()}"
    
    def get_batch_cache_key(self) -> str:
        """배치 데이터 캐시 키"""
        return "crypto:batch:all_prices"
    
    def get_last_update_key(self) -> str:
        """마지막 업데이트 시간 키"""
        return "crypto:meta:last_batch_update"
    
    def normalize_symbol(self, coin_input: str) -> Optional[str]:
        """코인 입력을 표준 심볼로 변환"""
        coin_input = coin_input.upper().strip()
        
        # 한글명 → 심볼 매핑
        korean_to_symbol = {v: k for k, v in self.korean_names.items()}
        
        if coin_input in korean_to_symbol:
            return korean_to_symbol[coin_input]
        
        if coin_input in self.supported_coins:
            return coin_input
        
        return None
    
    def fetch_upbit_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """업비트에서 여러 코인 가격 조회"""
        try:
            markets = [f"KRW-{symbol}" for symbol in symbols]
            url = f"{self.upbit_base_url}/ticker"
            params = {"markets": ",".join(markets)}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 심볼별로 데이터 정리
            result = {}
            for item in data:
                market = item.get('market', '')
                if market.startswith('KRW-'):
                    symbol = market.replace('KRW-', '')
                    result[symbol] = {
                        'symbol': symbol,
                        'korean_name': self.korean_names.get(symbol, symbol),
                        'current_price': item.get('trade_price', 0),
                        'change_rate': item.get('change_rate', 0) * 100,
                        'change': item.get('change', 'EVEN'),
                        'high_price': item.get('high_price', 0),
                        'low_price': item.get('low_price', 0),
                        'volume_24h': item.get('acc_trade_volume_24h', 0),
                        'trade_volume_24h': item.get('acc_trade_price_24h', 0),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'upbit'
                    }
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 업비트 API 호출 실패: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ 가격 데이터 처리 실패: {e}")
            return {}
    
    def cache_price_data(self, symbol: str, price_data: Dict) -> bool:
        """개별 코인 가격 데이터 캐싱"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self.get_cache_key(symbol)
            self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(price_data, ensure_ascii=False)
            )
            return True
        except Exception as e:
            logger.error(f"❌ 캐시 저장 실패 ({symbol}): {e}")
            return False
    
    def cache_batch_data(self, batch_data: Dict[str, Dict]) -> bool:
        """배치 데이터 캐싱"""
        if not self.redis_client:
            return False
        
        try:
            # 배치 데이터 저장
            batch_key = self.get_batch_cache_key()
            self.redis_client.setex(
                batch_key,
                self.cache_ttl + 10,  # 조금 더 긴 TTL
                json.dumps(batch_data, ensure_ascii=False)
            )
            
            # 개별 코인별로도 저장
            for symbol, data in batch_data.items():
                self.cache_price_data(symbol, data)
            
            # 마지막 업데이트 시간 저장
            update_key = self.get_last_update_key()
            self.redis_client.setex(
                update_key,
                3600,  # 1시간
                datetime.now().isoformat()
            )
            
            logger.info(f"✅ 배치 데이터 캐싱 완료: {len(batch_data)}개 코인")
            return True
            
        except Exception as e:
            logger.error(f"❌ 배치 캐시 저장 실패: {e}")
            return False
    
    def get_cached_price(self, symbol: str) -> Optional[Dict]:
        """캐시에서 가격 데이터 조회"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self.get_cache_key(symbol)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
                
        except Exception as e:
            logger.error(f"❌ 캐시 조회 실패 ({symbol}): {e}")
        
        return None
    
    def get_cached_batch_data(self) -> Optional[Dict[str, Dict]]:
        """캐시에서 배치 데이터 조회"""
        if not self.redis_client:
            return None
        
        try:
            batch_key = self.get_batch_cache_key()
            cached_data = self.redis_client.get(batch_key)
            
            if cached_data:
                return json.loads(cached_data)
                
        except Exception as e:
            logger.error(f"❌ 배치 캐시 조회 실패: {e}")
        
        return None
    
    def get_price(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """가격 정보 조회 (캐시 우선, 필요시 API 호출)"""
        try:
            normalized_symbol = self.normalize_symbol(symbol)
            if not normalized_symbol:
                logger.warning(f"❌ 지원하지 않는 코인: {symbol}")
                return None
            
            # 강제 새로고침이 아닌 경우 캐시 확인
            if not force_refresh:
                cached_data = self.get_cached_price(normalized_symbol)
                if cached_data:
                    logger.debug(f"📋 캐시에서 조회: {normalized_symbol}")
                    return cached_data
            
            # 캐시 미스 또는 강제 새로고침 시 API 호출
            logger.info(f"🔄 API 호출: {normalized_symbol}")
            fresh_data = self.fetch_upbit_prices([normalized_symbol])
            
            if normalized_symbol in fresh_data:
                price_data = fresh_data[normalized_symbol]
                self.cache_price_data(normalized_symbol, price_data)
                return price_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 가격 조회 실패 ({symbol}): {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str], force_refresh: bool = False) -> Dict[str, Dict]:
        """여러 코인 가격 일괄 조회"""
        try:
            normalized_symbols = []
            for symbol in symbols:
                norm_symbol = self.normalize_symbol(symbol)
                if norm_symbol:
                    normalized_symbols.append(norm_symbol)
            
            if not normalized_symbols:
                return {}
            
            result = {}
            symbols_to_fetch = []
            
            # 캐시 확인 (강제 새로고침이 아닌 경우)
            if not force_refresh:
                for symbol in normalized_symbols:
                    cached_data = self.get_cached_price(symbol)
                    if cached_data:
                        result[symbol] = cached_data
                    else:
                        symbols_to_fetch.append(symbol)
            else:
                symbols_to_fetch = normalized_symbols
            
            # API 호출이 필요한 코인들
            if symbols_to_fetch:
                logger.info(f"🔄 API 호출: {symbols_to_fetch}")
                fresh_data = self.fetch_upbit_prices(symbols_to_fetch)
                
                for symbol, data in fresh_data.items():
                    result[symbol] = data
                    self.cache_price_data(symbol, data)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 다중 가격 조회 실패: {e}")
            return {}
    
    def update_all_prices(self) -> bool:
        """모든 지원 코인의 가격 정보 업데이트"""
        try:
            logger.info("🔄 전체 가격 정보 업데이트 시작")
            
            # 배치로 모든 코인 가격 조회
            batch_data = self.fetch_upbit_prices(self.supported_coins)
            
            if batch_data:
                # 캐시에 저장
                success = self.cache_batch_data(batch_data)
                if success:
                    logger.info(f"✅ 전체 가격 업데이트 완료: {len(batch_data)}개 코인")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 전체 가격 업데이트 실패: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """캐시 정보 조회"""
        if not self.redis_client:
            return {"redis_connected": False}
        
        try:
            # 마지막 배치 업데이트 시간
            last_update_key = self.get_last_update_key()
            last_update = self.redis_client.get(last_update_key)
            
            # 캐시된 코인 수 확인
            pattern = "crypto:price:*"
            cached_keys = self.redis_client.keys(pattern)
            
            # 배치 데이터 확인
            batch_key = self.get_batch_cache_key()
            batch_exists = self.redis_client.exists(batch_key)
            
            return {
                "redis_connected": True,
                "last_batch_update": last_update,
                "cached_coins_count": len(cached_keys),
                "batch_cache_exists": bool(batch_exists),
                "cache_ttl_seconds": self.cache_ttl,
                "supported_coins_count": len(self.supported_coins)
            }
            
        except Exception as e:
            logger.error(f"❌ 캐시 정보 조회 실패: {e}")
            return {"redis_connected": False, "error": str(e)}
    
    def clear_cache(self, pattern: str = "crypto:*") -> bool:
        """캐시 삭제"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"🗑️ 캐시 삭제 완료: {deleted}개 키")
                return True
            return True
            
        except Exception as e:
            logger.error(f"❌ 캐시 삭제 실패: {e}")
            return False
    
    def start_background_updater(self, interval: int = None):
        """백그라운드 가격 업데이트 시작"""
        if interval:
            self.batch_update_interval = interval
        
        def update_loop():
            while True:
                try:
                    self.update_all_prices()
                    time.sleep(self.batch_update_interval)
                except Exception as e:
                    logger.error(f"❌ 백그라운드 업데이트 오류: {e}")
                    time.sleep(5)  # 오류 시 5초 대기
        
        # 별도 스레드에서 실행
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(update_loop)
        
        logger.info(f"🔄 백그라운드 가격 업데이트 시작 (간격: {self.batch_update_interval}초)")

# 사용 예시
if __name__ == "__main__":
    import time
    
    # 서비스 초기화
    price_service = RedisPriceService()
    
    # 캐시 정보 확인
    cache_info = price_service.get_cache_info()
    print("캐시 정보:", json.dumps(cache_info, indent=2, ensure_ascii=False))
    
    # 전체 가격 업데이트
    print("\n전체 가격 업데이트...")
    price_service.update_all_prices()
    
    # 개별 코인 조회 테스트
    print("\n=== 개별 코인 조회 테스트 ===")
    btc_price = price_service.get_price("BTC")
    if btc_price:
        print(f"BTC 가격: {btc_price['current_price']:,}원")
        print(f"변동률: {btc_price['change_rate']:.2f}%")
    
    # 다중 코인 조회 테스트
    print("\n=== 다중 코인 조회 테스트 ===")
    prices = price_service.get_multiple_prices(["BTC", "ETH", "XRP"])
    for symbol, data in prices.items():
        print(f"{data['korean_name']} ({symbol}): {data['current_price']:,}원")
    
    print("\n✅ 테스트 완료")