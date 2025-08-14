#!/usr/bin/env python3
"""
Redis 암호화폐 가격 백그라운드 업데이터 서비스
주기적으로 Upbit API에서 가격 정보를 가져와 Redis에 캐싱
"""

import time
import logging
import signal
import sys
from datetime import datetime
from redis_price_service import RedisPriceService

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('price_updater.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class PriceUpdaterService:
    """백그라운드 가격 업데이트 서비스"""
    
    def __init__(self, update_interval: int = 20):
        """
        초기화
        Args:
            update_interval: 업데이트 간격 (초)
        """
        self.update_interval = update_interval
        self.redis_service = None
        self.is_running = False
        
        # 종료 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """종료 시그널 핸들러"""
        logger.info(f"🛑 종료 시그널 수신: {signum}")
        self.stop()
    
    def start(self):
        """서비스 시작"""
        try:
            logger.info("🚀 Redis 암호화폐 가격 업데이터 서비스 시작")
            
            # Redis 서비스 초기화
            self.redis_service = RedisPriceService()
            
            # Redis 연결 확인
            cache_info = self.redis_service.get_cache_info()
            if not cache_info.get('redis_connected', False):
                raise Exception("Redis 연결 실패")
            
            logger.info(f"✅ Redis 연결 성공: {cache_info}")
            
            # 초기 가격 업데이트
            logger.info("🔄 초기 가격 데이터 업데이트 중...")
            success = self.redis_service.update_all_prices()
            if success:
                logger.info("✅ 초기 가격 데이터 업데이트 완료")
            else:
                logger.warning("⚠️ 초기 가격 데이터 업데이트 실패")
            
            # 백그라운드 업데이트 루프 시작
            self.is_running = True
            self._update_loop()
            
        except Exception as e:
            logger.error(f"❌ 서비스 시작 실패: {e}")
            sys.exit(1)
    
    def stop(self):
        """서비스 중지"""
        logger.info("🛑 서비스 중지 중...")
        self.is_running = False
    
    def _update_loop(self):
        """백그라운드 업데이트 루프"""
        logger.info(f"🔄 백그라운드 업데이트 루프 시작 (간격: {self.update_interval}초)")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # 가격 정보 업데이트
                success = self.redis_service.update_all_prices()
                
                end_time = time.time()
                duration = end_time - start_time
                
                if success:
                    logger.info(f"✅ 가격 업데이트 완료 (소요시간: {duration:.2f}초)")
                    
                    # 캐시 통계 정보 출력
                    cache_info = self.redis_service.get_cache_info()
                    cached_count = cache_info.get('cached_coins_count', 0)
                    supported_count = cache_info.get('supported_coins_count', 0)
                    logger.info(f"📊 캐시 상태: {cached_count}/{supported_count}개 코인 캐싱됨")
                else:
                    logger.warning(f"⚠️ 가격 업데이트 실패 (소요시간: {duration:.2f}초)")
                
                # 다음 업데이트까지 대기
                if self.is_running:
                    logger.debug(f"⏰ {self.update_interval}초 대기 중...")
                    time.sleep(self.update_interval)
                    
            except Exception as e:
                logger.error(f"❌ 업데이트 루프 오류: {e}")
                if self.is_running:
                    logger.info("🔄 5초 후 재시도...")
                    time.sleep(5)
        
        logger.info("🏁 백그라운드 업데이트 루프 종료")
    
    def get_status(self) -> dict:
        """서비스 상태 조회"""
        if not self.redis_service:
            return {"status": "not_initialized"}
        
        cache_info = self.redis_service.get_cache_info()
        
        return {
            "status": "running" if self.is_running else "stopped",
            "update_interval": self.update_interval,
            "redis_connected": cache_info.get('redis_connected', False),
            "cached_coins_count": cache_info.get('cached_coins_count', 0),
            "supported_coins_count": cache_info.get('supported_coins_count', 0),
            "last_batch_update": cache_info.get('last_batch_update', None)
        }


def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("🚀 Redis 암호화폐 가격 업데이터 서비스")
    logger.info("=" * 60)
    
    # 업데이트 간격 설정 (기본 20초)
    update_interval = 20
    
    try:
        # 환경변수나 설정에서 간격 조회 가능
        import os
        if os.getenv('PRICE_UPDATE_INTERVAL'):
            update_interval = int(os.getenv('PRICE_UPDATE_INTERVAL'))
    except:
        pass
    
    # 서비스 시작
    service = PriceUpdaterService(update_interval=update_interval)
    service.start()


if __name__ == "__main__":
    main()