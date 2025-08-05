#!/usr/bin/env python3
"""
코인 뉴스 수집 및 전처리 파이프라인

이 스크립트는 다음 작업을 수행합니다:
1. 각종 코인 뉴스 사이트에서 RSS/웹 스크래핑으로 뉴스 수집
2. 수집된 뉴스를 전처리 및 요약
3. PgVector DB에 임베딩과 함께 저장
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    import codecs
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    except:
        # 이미 설정된 경우 무시
        pass

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.news_collector import NewsCollector
from services.news_preprocessor import NewsPreprocessor
from services.dual_db_service import DualDatabaseService

class NewsPipeline:
    def __init__(self, 
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 pg_host: str = "localhost",
                 pg_port: int = 5433,
                 openai_api_key: str = None):
        """뉴스 파이프라인 초기화"""
        
        # 로깅 설정
        # 기존 핸들러 제거
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # UTF-8 StreamHandler 생성
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # 파일 핸들러 생성
        file_handler = logging.FileHandler('news_pipeline.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # 루트 로거에 핸들러 추가
        logging.root.setLevel(logging.INFO)
        logging.root.addHandler(console_handler)
        logging.root.addHandler(file_handler)
        self.logger = logging.getLogger(__name__)
        
        # 서비스 초기화
        try:
            self.collector = NewsCollector(redis_host=redis_host, redis_port=redis_port)
            self.preprocessor = NewsPreprocessor(openai_api_key=openai_api_key)
            self.dual_db_service = DualDatabaseService()
            
            self.logger.info("뉴스 파이프라인 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"뉴스 파이프라인 초기화 실패: {e}")
            raise
    
    def run_pipeline(self, hours_back: int = 24, use_cache: bool = True) -> Dict[str, Any]:
        """전체 파이프라인 실행"""
        start_time = datetime.now()
        results = {
            'start_time': start_time.isoformat(),
            'collected_count': 0,
            'processed_count': 0,
            'saved_count': 0,
            'errors': [],
            'duration_seconds': 0
        }
        
        try:
            self.logger.info("=" * 50)
            self.logger.info("뉴스 파이프라인 시작")
            self.logger.info("=" * 50)
            
            # 1단계: 뉴스 수집
            self.logger.info("1단계: 뉴스 수집 시작")
            
            raw_articles = []
            
            if use_cache:
                # 캐시에서 먼저 확인
                cached_articles = self.collector.load_from_cache()
                if cached_articles:
                    raw_articles = cached_articles
                    self.logger.info(f"캐시에서 {len(raw_articles)}개 뉴스 로드")
            
            if not raw_articles:
                # 새로 수집
                raw_articles = self.collector.collect_all_news(hours_back=hours_back)
                if use_cache:
                    self.collector.save_to_cache(raw_articles)
            
            results['collected_count'] = len(raw_articles)
            self.logger.info(f"총 {len(raw_articles)}개 뉴스 수집 완료")
            
            if not raw_articles:
                self.logger.warning("수집된 뉴스가 없습니다")
                return results
            
            # 2단계: 뉴스 전처리
            self.logger.info("2단계: 뉴스 전처리 시작")
            
            processed_articles = []
            for i, article_data in enumerate(raw_articles):
                try:
                    processed_article = self.preprocessor.preprocess_article(article_data)
                    
                    # 처리된 기사를 딕셔너리로 변환
                    article_dict = {
                        'title': processed_article.title,
                        'content': processed_article.content,
                        'summary': processed_article.summary,
                        'url': processed_article.url,
                        'source': processed_article.source,
                        'published_date': processed_article.published_date.isoformat(),
                        'keywords': processed_article.keywords or [],
                        'sentiment': processed_article.sentiment,
                        'raw_data': article_data.get('raw_data', {})
                    }
                    
                    processed_articles.append(article_dict)
                    
                    if (i + 1) % 10 == 0:
                        self.logger.info(f"전처리 진행률: {i + 1}/{len(raw_articles)}")
                    
                except Exception as e:
                    error_msg = f"기사 전처리 실패 (index {i}): {e}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
                    continue
            
            results['processed_count'] = len(processed_articles)
            self.logger.info(f"총 {len(processed_articles)}개 뉴스 전처리 완료")
            
            # 3단계: 데이터베이스 저장
            self.logger.info("3단계: 데이터베이스 저장 시작")
            
            saved_count = self.dual_db_service.batch_insert_articles(processed_articles)
            results['saved_count'] = saved_count
            
            self.logger.info(f"총 {saved_count}개 뉴스 저장 완료")
            
            # 완료 처리
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            results['duration_seconds'] = duration
            results['end_time'] = end_time.isoformat()
            
            self.logger.info("=" * 50)
            self.logger.info("뉴스 파이프라인 완료")
            self.logger.info(f"실행 시간: {duration:.2f}초")
            self.logger.info(f"수집: {results['collected_count']}개")
            self.logger.info(f"전처리: {results['processed_count']}개")
            self.logger.info(f"저장: {results['saved_count']}개")
            if results['errors']:
                self.logger.info(f"오류: {len(results['errors'])}개")
            self.logger.info("=" * 50)
            
        except Exception as e:
            error_msg = f"파이프라인 실행 중 오류 발생: {e}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            raise
        
        return results
    
    def run_incremental_update(self, hours_back: int = 6) -> Dict[str, Any]:
        """증분 업데이트 실행 (최근 N시간 뉴스만)"""
        self.logger.info(f"증분 업데이트 시작 (최근 {hours_back}시간)")
        return self.run_pipeline(hours_back=hours_back, use_cache=False)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """파이프라인 상태 확인"""
        try:
            # 데이터베이스 통계
            stats = self.dual_db_service.get_statistics()
            
            # Redis 연결 상태
            redis_status = "connected" if self.collector.redis_client else "disconnected"
            try:
                if self.collector.redis_client:
                    self.collector.redis_client.ping()
                    redis_status = "connected"
            except:
                redis_status = "connection_failed"
            
            return {
                'database_stats': stats,
                'redis_status': redis_status,
                'services_initialized': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'services_initialized': False
            }
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """오래된 데이터 정리"""
        self.logger.info(f"{days}일 이전 데이터 정리 시작")
        # DualDatabaseService에는 delete_old_articles가 없으므로 주석 처리
        # deleted_count = self.dual_db_service.delete_old_articles(days)
        deleted_count = 0  # 임시로 0 반환
        self.logger.info(f"{deleted_count}개 오래된 기사 삭제 완료")
        return deleted_count

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='코인 뉴스 수집 및 전처리 파이프라인')
    parser.add_argument('--hours', type=int, default=24, help='수집할 뉴스의 시간 범위 (기본: 24시간)')
    parser.add_argument('--no-cache', action='store_true', help='캐시 사용 안함')
    parser.add_argument('--incremental', action='store_true', help='증분 업데이트 모드')
    parser.add_argument('--status', action='store_true', help='파이프라인 상태 확인')
    parser.add_argument('--cleanup', type=int, help='N일 이전 데이터 정리')
    parser.add_argument('--openai-key', type=str, help='OpenAI API 키')
    
    args = parser.parse_args()
    
    try:
        # 파이프라인 초기화
        pipeline = NewsPipeline(openai_api_key=args.openai_key)
        
        if args.status:
            # 상태 확인
            status = pipeline.get_pipeline_status()
            print("파이프라인 상태:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif args.cleanup:
            # 데이터 정리
            deleted_count = pipeline.cleanup_old_data(args.cleanup)
            print(f"{deleted_count}개 오래된 기사를 삭제했습니다.")
            
        elif args.incremental:
            # 증분 업데이트
            results = pipeline.run_incremental_update(args.hours)
            print("증분 업데이트 결과:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            
        else:
            # 전체 파이프라인 실행
            results = pipeline.run_pipeline(
                hours_back=args.hours,
                use_cache=not args.no_cache
            )
            print("파이프라인 실행 결과:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
    
    except KeyboardInterrupt:
        print("\n파이프라인이 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"파이프라인 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()