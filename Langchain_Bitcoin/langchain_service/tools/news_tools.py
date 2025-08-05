"""
크립토 뉴스 검색 Tool
기존 벡터 검색 기능을 LangChain Tool로 래핑
"""

import logging
import asyncio
from typing import Any, Dict
from langchain.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)

class CryptoNewsSearchTool(BaseTool):
    """크립토 뉴스 벡터 검색 도구"""
    
    name: str = "crypto_news_search"
    description: str = """
    암호화폐 관련 뉴스를 벡터 유사도 기반으로 검색합니다.
    
    사용 예시:
    - "비트코인 최근 뉴스"
    - "이더리움 가격 상승 소식"
    - "암호화폐 규제 뉴스"
    
    입력: 검색하고 싶은 키워드나 질문
    출력: 관련 뉴스 목록과 요약
    """
    
    vector_service: Any = Field(description="벡터 서비스 인스턴스")
    
    def _run(self, query: str) -> str:
        """뉴스 검색 실행 - 개선된 버전"""
        try:
            logger.info(f"📰 뉴스 검색 실행: '{query}'")
            
            # 사용자 요청량 파악
            requested_count = 3  # 기본값
            if '다' in query or '모든' in query or '전체' in query or '모두' in query:
                requested_count = 10  # 더 많이 요청한 경우
            elif any(num in query for num in ['5개', '다섯', '5']):
                requested_count = 5
            
            logger.debug(f"검색 파라미터 - 요청량: {requested_count}개")
            
            # 직접 DB 검색으로 단순화 (벡터 검색 문제 우회)
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                
                conn = psycopg2.connect(
                    host='localhost',
                    port=5435,
                    database='mydb',
                    user='myuser',
                    password='mypassword'
                )
                
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    logger.debug(f"직접 DB 검색 실행 - 키워드: '{query}'")
                    
                    # 키워드 기반 검색 + 최신순 정렬
                    search_conditions = []
                    search_params = []
                    
                    # 기본 키워드 검색
                    basic_keywords = ['비트코인', 'bitcoin', 'btc', '암호화폐', 'crypto', 'ethereum', 'eth']
                    
                    # 사용자 쿼리에서 키워드 추출
                    query_lower = query.lower()
                    found_keywords = []
                    
                    for keyword in basic_keywords:
                        if keyword in query_lower:
                            found_keywords.append(keyword)
                    
                    # 구체적인 키워드가 있으면 해당 키워드로 검색
                    if found_keywords:
                        keyword_conditions = []
                        for keyword in found_keywords:
                            keyword_conditions.append('(title ILIKE %s OR summary ILIKE %s)')
                            search_params.extend([f'%{keyword}%', f'%{keyword}%'])
                        
                        search_query = f'''
                            SELECT id, title, summary, url, source, published_date,
                                   CASE 
                                       WHEN title ILIKE %s THEN 0.9
                                       WHEN summary ILIKE %s THEN 0.7
                                       ELSE 0.5
                                   END as relevance_score
                            FROM crypto_news 
                            WHERE ({' OR '.join(keyword_conditions)})
                            ORDER BY relevance_score DESC, published_date DESC 
                            LIMIT %s
                        '''
                        search_params = [f'%{found_keywords[0]}%', f'%{found_keywords[0]}%'] + search_params + [requested_count]
                        
                    else:
                        # 키워드가 없으면 최신 뉴스 제공
                        search_query = '''
                            SELECT id, title, summary, url, source, published_date,
                                   0.8 as relevance_score
                            FROM crypto_news 
                            ORDER BY published_date DESC 
                            LIMIT %s
                        '''
                        search_params = [requested_count]
                    
                    cur.execute(search_query, search_params)
                    results = cur.fetchall()
                    
                    logger.info(f"직접 DB 검색 완료: {len(results)}개 결과")
                    
                    if results:
                        # 결과 포맷팅
                        formatted_results = f"📰 '{query}' 검색 결과 ({len(results)}개):\n\n"
                        
                        for i, result in enumerate(results, 1):
                            title = result['title']
                            if len(title) > 80:
                                title = title[:80] + "..."
                            
                            summary = result.get('summary', '')  
                            if summary and len(summary) > 150:
                                summary = summary[:150] + "..."
                            elif not summary:
                                summary = '요약 정보가 없습니다.'
                            
                            # 관련도를 별점으로 표시
                            relevance = result.get('relevance_score', 0.5)
                            star_rating = "⭐" * min(max(int(relevance * 5), 1), 5)
                            
                            # 날짜 포맷팅
                            pub_date = result.get('published_date', '')
                            if isinstance(pub_date, str) and 'T' in pub_date:
                                pub_date = pub_date.split('T')[0]
                            
                            formatted_results += f"{i}. **{title}**\n"
                            formatted_results += f"   {star_rating} 관련도: {relevance:.2f}\n"
                            if pub_date:
                                formatted_results += f"   📅 {pub_date}\n"
                            formatted_results += f"   📖 {summary}\n"
                            formatted_results += f"   🔗 출처: {result.get('source', '출처 미상')}\n\n"
                        
                        formatted_results += f"💡 총 {len(results)}개의 뉴스를 찾았습니다."
                        
                        if len(results) < requested_count:
                            formatted_results += f"\n\n🔄 더 많은 뉴스를 원하시면 뉴스 파이프라인을 실행하여 최신 뉴스를 수집해보세요."
                        
                        conn.close()
                        logger.info("뉴스 검색 성공, 결과 반환")
                        return formatted_results
                    
                    else:
                        # 결과가 없는 경우 최신 뉴스라도 제공
                        cur.execute('''
                            SELECT id, title, summary, url, source, published_date
                            FROM crypto_news 
                            ORDER BY published_date DESC 
                            LIMIT 3
                        ''')
                        
                        latest_results = cur.fetchall()
                        conn.close()
                        
                        if latest_results:
                            formatted_results = f"'{query}'와 직접 관련된 뉴스를 찾지 못해서 최신 암호화폐 뉴스를 제공합니다:\n\n"
                            
                            for i, result in enumerate(latest_results, 1):
                                title = result['title']
                                if len(title) > 70:
                                    title = title[:70] + "..."
                                
                                summary = result.get('summary', '')
                                if summary and len(summary) > 120:
                                    summary = summary[:120] + "..."
                                
                                formatted_results += f"{i}. **{title}**\n"
                                formatted_results += f"   📖 {summary}\n"
                                formatted_results += f"   📅 {result.get('published_date', '')}\n"
                                formatted_results += f"   🔗 출처: {result.get('source', '')}\n\n"
                            
                            formatted_results += "🔄 더 관련성 높은 뉴스를 위해 뉴스 파이프라인을 실행해보세요."
                            return formatted_results
                
                conn.close()
                
            except Exception as db_error:
                logger.error(f"❌ 직접 DB 검색 실패: {db_error}")
                results = []
            
            if not results:
                logger.warning("모든 벡터 검색 방법 실패, 기존 테이블에서 직접 검색 시도")
                # 기존 테이블에서 검색 시도 (백업) - OPENAI_API_KEY 없이 직접 DB 연결
                try:
                    logger.debug("기존 테이블 직접 검색 시도 (직접 DB 연결)...")
                    import psycopg2
                    from psycopg2.extras import RealDictCursor
                    
                    # PgVector DB에 직접 연결
                    conn = psycopg2.connect(
                        host='localhost',
                        port=5435,
                        database='mydb',
                        user='myuser',
                        password='mypassword'
                    )
                    
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        logger.debug(f"SQL 직접 검색 실행 - 키워드: '{query}'")
                        
                        # 확장된 키워드 검색
                        search_terms = [query]
                        
                        # 특정 키워드에 대한 확장 검색어 추가
                        if '트럼프' in query.lower():
                            search_terms.extend(['trump', 'donald', '도널드', '대통령', 'president'])
                        elif '백악관' in query.lower():
                            search_terms.extend(['white house', 'whitehouse', '미국', 'usa', '정부', 'government'])
                        elif '정책' in query.lower():
                            search_terms.extend(['policy', 'regulation', '규제', 'sec', '정부'])
                        elif 'etf' in query.lower():
                            search_terms.extend(['bitcoin etf', 'spot etf', '상장지수펀드'])
                        
                        # 각 검색어로 검색
                        all_results = []
                        for term in search_terms:
                            cur.execute("""
                                SELECT id, title, summary, url, source, published_date 
                                FROM crypto_news 
                                WHERE title ILIKE %s OR summary ILIKE %s 
                                ORDER BY published_date DESC 
                                LIMIT 5
                            """, (f'%{term}%', f'%{term}%'))
                            
                            term_results = cur.fetchall()
                            all_results.extend(term_results)
                        
                        # 중복 제거 (id 기준)
                        seen_ids = set()
                        unique_results = []
                        for result in all_results:
                            if result['id'] not in seen_ids:
                                seen_ids.add(result['id'])
                                unique_results.append(result)
                        
                        fallback_results = unique_results[:3]  # 최대 3개
                        logger.info(f"확장 키워드 검색 완료: {len(fallback_results)}개 결과")
                        
                        if fallback_results:
                            logger.debug("확장 검색에서 결과 찾음, 포맷팅 시작")
                            formatted_results = f"📰 '{query}' 관련 뉴스 검색 결과:\n\n"
                            for i, result in enumerate(fallback_results, 1):
                                title = result['title'][:80] + "..." if len(result['title']) > 80 else result['title']
                                summary = result.get('summary', '')[:150] + "..." if result.get('summary') and len(result.get('summary', '')) > 150 else result.get('summary', '내용 없음')
                                
                                formatted_results += f"{i}. **{title}**\n"
                                formatted_results += f"   📖 {summary}\n"
                                formatted_results += f"   📅 {result.get('published_date', '날짜 미상')}\n"
                                formatted_results += f"   🔗 출처: {result.get('source', '출처 미상')}\n\n"
                            
                            formatted_results += f"💡 총 {len(fallback_results)}개의 관련 뉴스를 찾았습니다."
                            logger.info("확장 검색 성공, 결과 반환")
                            conn.close()
                            return formatted_results
                        else:
                            # 검색 결과가 없으면 최신 뉴스 제공
                            logger.info("검색 결과 없음, 최신 뉴스 제공")
                            cur.execute("""
                                SELECT id, title, summary, url, source, published_date 
                                FROM crypto_news 
                                ORDER BY published_date DESC 
                                LIMIT 3
                            """)
                            
                            latest_news = cur.fetchall()
                            
                            if latest_news:
                                formatted_results = f"'{query}'와 직접적으로 관련된 뉴스를 찾을 수 없어서, 대신 최신 암호화폐 뉴스를 제공합니다:\n\n"
                                
                                for i, result in enumerate(latest_news, 1):
                                    title = result['title'][:80] + "..." if len(result['title']) > 80 else result['title']
                                    summary = result.get('summary', '')[:120] + "..." if result.get('summary') and len(result.get('summary', '')) > 120 else result.get('summary', '내용 없음')
                                    
                                    formatted_results += f"{i}. **{title}**\n"
                                    formatted_results += f"   📖 {summary}\n"
                                    formatted_results += f"   📅 {result.get('published_date', '날짜 미상')}\n"
                                    formatted_results += f"   🔗 출처: {result.get('source', '출처 미상')}\n\n"
                                
                                formatted_results += f"🔄 더 구체적인 키워드로 검색하시거나, 뉴스 파이프라인을 실행하여 최신 뉴스를 수집해보세요."
                                conn.close()
                                return formatted_results
                            
                    conn.close()
                        
                except Exception as e:
                    logger.error(f"❌ 기존 테이블 검색 실패: {e}")
                    logger.debug(f"기존 테이블 검색 상세 오류: {str(e)}")
                    if 'conn' in locals():
                        conn.close()
                
                logger.warning(f"모든 검색 방법 실패: '{query}' 키워드로 뉴스를 찾을 수 없음")
                return f"'{query}'와 관련된 뉴스를 현재 데이터베이스에서 찾을 수 없습니다.\n\n🔄 **해결 방법:**\n• 다른 키워드로 검색해보세요 (예: 'ETF', '규제', '비트코인')\n• 뉴스 파이프라인을 실행하여 최신 뉴스를 수집해보세요\n• 좀 더 일반적인 용어로 검색해보세요"
            
            # 결과 포맷팅
            formatted_results = "📰 관련 뉴스 검색 결과:\n\n"
            
            for i, result in enumerate(results, 1):
                # PgVector 서비스의 결과 형식에 맞춤
                similarity_score = result.get('similarity', 0)
                title = result.get('title', '제목 없음')
                summary = result.get('summary') or result.get('content', '')
                source = result.get('source', '출처 미상')
                published_date = result.get('published_date', '')
                
                # 제목 정리
                if len(title) > 80:
                    title = title[:80] + "..."
                
                # 요약 내용 정리
                if summary:
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                else:
                    summary = "내용을 확인할 수 없습니다."
                
                # 유사도를 별점으로 표현
                star_rating = "⭐" * min(max(int(similarity_score * 5), 1), 5)
                
                # 날짜 포맷팅
                if published_date and isinstance(published_date, str):
                    try:
                        # ISO 형식 날짜를 간단하게 변환
                        if 'T' in published_date:
                            date_part = published_date.split('T')[0]
                            published_date = date_part
                    except:
                        pass
                
                formatted_results += f"{i}. **{title}**\n"
                formatted_results += f"   {star_rating} 관련도: {similarity_score:.2f}\n"
                if published_date:
                    formatted_results += f"   📅 {published_date}\n"
                formatted_results += f"   📖 {summary}\n"
                formatted_results += f"   🔗 출처: {source}\n\n"
            
            formatted_results += f"💡 총 {len(results)}개의 관련 뉴스를 찾았습니다."
            
            logger.info(f"✅ 뉴스 검색 완료: {len(results)}개 결과")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 뉴스 검색 실패: {e}")
            return f"뉴스 검색 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """비동기 뉴스 검색 실행"""
        return self._run(query)


class LatestNewsLookupTool(BaseTool):
    """최신 뉴스 조회 도구"""
    
    name: str = "latest_news_lookup"
    description: str = """
    암호화폐 관련 최신 뉴스를 시간순으로 조회합니다.
    
    사용 예시:
    - "최신 뉴스"
    - "오늘 암호화폐 소식"
    - "최근 업데이트"
    
    입력: "최신" 또는 "recent" 등의 키워드
    출력: 시간순으로 정렬된 최신 뉴스 목록
    """
    
    vector_service: Any = Field(description="벡터 서비스 인스턴스")
    
    def _run(self, query: str = "최신") -> str:
        """최신 뉴스 조회 실행"""
        try:
            logger.info(f"📅 최신 뉴스 조회 실행: {query}")
            
            # DualDatabaseService를 통한 최신 뉴스 조회
            try:
                from services.dual_db_service import DualDatabaseService
                dual_db_service = DualDatabaseService()
                results = dual_db_service.get_recent_articles(hours=24, limit=5)
            except Exception as import_error:
                logger.error(f"DualDatabaseService import 실패: {import_error}")
                # PgVector 서비스 백업
                try:
                    from services.pgvector_service import PgVectorService
                    pgvector_service = PgVectorService()
                    results = pgvector_service.get_recent_articles(hours=24, limit=5)
                except Exception as backup_error:
                    logger.error(f"백업 서비스 실패: {backup_error}")
                    # 기존 벡터 서비스 사용 (최종 백업)
                    if hasattr(self.vector_service, 'get_latest_news'):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            results = loop.run_until_complete(
                                self.vector_service.get_latest_news(limit=5)
                            )
                        finally:
                            loop.close()
                    else:
                        results = []
            
            if not results:
                return "최신 뉴스를 찾을 수 없습니다. 데이터베이스에 뉴스가 없거나 연결에 문제가 있을 수 있습니다."
            
            # 결과 포맷팅
            formatted_results = "📅 최신 암호화폐 뉴스 (최근 24시간):\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', '제목 없음')
                summary = result.get('summary') or result.get('content', '')
                source = result.get('source', '출처 미상')
                published_date = result.get('published_date', '')
                
                # 제목 정리
                if len(title) > 70:
                    title = title[:70] + "..."
                
                # 요약 내용 정리
                if summary:
                    if len(summary) > 120:
                        summary = summary[:120] + "..."
                else:
                    summary = "내용을 확인할 수 없습니다."
                
                # 날짜 포맷팅
                if published_date and isinstance(published_date, str):
                    try:
                        if 'T' in published_date:
                            date_part = published_date.split('T')[0]
                            published_date = date_part
                    except:
                        pass
                
                formatted_results += f"{i}. **{title}**\n"
                if published_date:
                    formatted_results += f"   📅 {published_date}\n"
                formatted_results += f"   📖 {summary}\n"
                formatted_results += f"   🔗 출처: {source}\n\n"
            
            formatted_results += f"💡 총 {len(results)}개의 최신 뉴스를 찾았습니다."
            
            logger.info(f"✅ 최신 뉴스 조회 완료: {len(results)}개 결과")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 최신 뉴스 조회 실패: {e}")
            return f"최신 뉴스 조회 중 오류가 발생했습니다: {str(e)}. 데이터베이스에 뉴스 데이터가 있는지 확인해주세요."
    
    async def _arun(self, query: str = "최신") -> str:
        """비동기 최신 뉴스 조회 실행"""
        return self._run(query)


class DatabaseStatsTool(BaseTool):
    """데이터베이스 통계 조회 도구"""
    
    name: str = "database_stats"
    description: str = """
    현재 데이터베이스의 뉴스 통계 정보를 조회합니다.
    
    사용 예시:
    - "데이터베이스 상태"
    - "뉴스 개수"
    - "통계 정보"
    
    입력: "stats" 또는 "통계" 등의 키워드
    출력: 전체 뉴스 개수, 임베딩 처리 현황 등의 통계
    """
    
    vector_service: Any = Field(description="벡터 서비스 인스턴스")
    
    def _run(self, query: str = "통계") -> str:
        """데이터베이스 통계 조회 실행"""
        try:
            logger.info(f"📊 데이터베이스 통계 조회 실행: {query}")
            
            # 직접 DB 연결로 통계 조회 (비동기 루프 충돌 방지)
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                
                # PgVector DB에 직접 연결
                conn = psycopg2.connect(
                    host='localhost',
                    port=5435,
                    database='mydb',
                    user='myuser',
                    password='mypassword'
                )
                
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 통계 정보 조회
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total_news,
                            COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as news_with_embedding,
                            COUNT(CASE WHEN embedding IS NULL THEN 1 END) as news_without_embedding
                        FROM crypto_news
                    """)
                    
                    result = cur.fetchone()
                    
                    total_news = result['total_news']
                    news_with_embedding = result['news_with_embedding'] 
                    news_without_embedding = result['news_without_embedding']
                    
                    if total_news > 0:
                        embedding_coverage = (news_with_embedding / total_news) * 100
                    else:
                        embedding_coverage = 0
                    
                    stats = {
                        'total_news': total_news,
                        'news_with_embedding': news_with_embedding,
                        'news_without_embedding': news_without_embedding,
                        'embedding_coverage': embedding_coverage
                    }
                
                conn.close()
                
            except Exception as direct_db_error:
                logger.error(f"직접 DB 통계 조회 실패: {direct_db_error}")
                
                # 기존 벡터 서비스 사용 (백업)
                try:
                    # 현재 실행 중인 이벤트 루프가 있는지 확인
                    try:
                        current_loop = asyncio.get_running_loop()
                        # 이미 실행 중인 루프가 있으면 새 스레드에서 실행
                        import concurrent.futures
                        import threading
                        
                        def get_stats():
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                return new_loop.run_until_complete(
                                    self.vector_service.get_database_stats()
                                )
                            finally:
                                new_loop.close()
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(get_stats)
                            stats = future.result(timeout=10)
                            
                    except RuntimeError:
                        # 실행 중인 루프가 없으면 새 루프 생성
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            stats = loop.run_until_complete(
                                self.vector_service.get_database_stats()
                            )
                        finally:
                            loop.close()
                            
                except Exception as backup_error:
                    logger.error(f"백업 통계 조회도 실패: {backup_error}")
                    stats = None
            
            if not stats:
                return "데이터베이스 통계 정보를 조회할 수 없습니다."
            
            # 결과 포맷팅
            total_news = stats.get('total_news', 0)
            news_with_embedding = stats.get('news_with_embedding', 0)
            news_without_embedding = stats.get('news_without_embedding', 0)
            embedding_coverage = stats.get('embedding_coverage', 0)
            
            formatted_stats = "📊 데이터베이스 통계 정보:\n\n"
            formatted_stats += f"📰 **전체 뉴스 개수**: {total_news:,}개\n"
            formatted_stats += f"✅ **임베딩 처리 완료**: {news_with_embedding:,}개\n"
            formatted_stats += f"⏳ **임베딩 처리 대기**: {news_without_embedding:,}개\n"
            formatted_stats += f"📈 **처리 완료율**: {embedding_coverage:.1f}%\n\n"
            
            # 상태 평가
            if embedding_coverage >= 90:
                status = "🟢 우수한 상태입니다!"
            elif embedding_coverage >= 70:
                status = "🟡 양호한 상태입니다."
            else:
                status = "🔴 임베딩 처리가 더 필요합니다."
            
            formatted_stats += f"💡 **상태 평가**: {status}\n"
            
            logger.info(f"✅ 데이터베이스 통계 조회 완료")
            return formatted_stats
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 통계 조회 실패: {e}")
            return f"데이터베이스 통계 조회 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, query: str = "통계") -> str:
        """비동기 데이터베이스 통계 조회 실행"""
        return self._run(query)
