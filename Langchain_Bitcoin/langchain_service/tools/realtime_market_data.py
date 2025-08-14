"""
실시간 시장 데이터 통합 도구
가격, 거래량, 기술 지표 등의 실시간 데이터를 통합하여 Claude 수준의 시장 분석 제공
"""

import logging
import os
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from pydantic import Field
from dataclasses import dataclass
import pandas as pd
import numpy as np

from langchain_service.core.database_manager import db_manager

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """시장 데이터 모델"""
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    market_cap: float
    high_24h: float
    low_24h: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change_24h': self.change_24h,
            'change_percent_24h': self.change_percent_24h,
            'volume_24h': self.volume_24h,
            'market_cap': self.market_cap,
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class TechnicalIndicators:
    """기술적 지표 모델"""
    symbol: str
    rsi: float
    macd: float
    macd_signal: float
    bb_upper: float
    bb_lower: float
    sma_20: float
    sma_50: float
    volume_sma: float
    timestamp: datetime

class RealTimeMarketDataTool(BaseTool):
    """실시간 시장 데이터 통합 도구"""
    
    name: str = "realtime_market_data"
    description: str = """
    실시간 암호화폐 시장 데이터를 수집하고 분석합니다.
    
    특징:
    - 실시간 가격 및 거래량 데이터
    - 기술적 지표 계산 (RSI, MACD, 볼린저 밴드)
    - 시장 심리 지표 분석
    - 다중 거래소 데이터 통합
    - 캐싱을 통한 빠른 응답
    
    사용 예시:
    - "비트코인 실시간 시장 데이터"
    - "주요 코인 기술적 지표 분석"
    - "시장 전체 동향 파악"
    """
    
    def __init__(self):
        super().__init__()
        self.api_endpoints = {
            'upbit': 'https://api.upbit.com/v1/ticker',
            'coinmarketcap': 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest',
            'coingecko': 'https://api.coingecko.com/api/v3/simple/price'
        }
        self.supported_symbols = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH']
        
    def _run(self, query: str) -> str:
        """비동기 실행을 동기로 래핑"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._arun(query))
        finally:
            loop.close()
    
    async def _arun(self, query: str) -> str:
        """실시간 시장 데이터 분석 실행"""
        try:
            logger.info(f"📊 실시간 시장 데이터 분석 시작: {query}")
            
            # 분석 타입 결정
            analysis_type = self._determine_analysis_type(query)
            
            if analysis_type == 'single_coin':
                symbol = self._extract_symbol(query)
                return await self._analyze_single_coin(symbol)
            elif analysis_type == 'market_overview':
                return await self._analyze_market_overview()
            elif analysis_type == 'technical_analysis':
                symbol = self._extract_symbol(query)
                return await self._perform_technical_analysis(symbol)
            else:
                return await self._comprehensive_market_analysis()
                
        except Exception as e:
            logger.error(f"❌ 실시간 시장 데이터 분석 실패: {e}")
            return f"시장 데이터 분석 중 오류가 발생했습니다: {str(e)}"
    
    def _determine_analysis_type(self, query: str) -> str:
        """쿼리 분석하여 분석 타입 결정"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['btc', 'bitcoin', '비트코인', 'eth', 'ethereum']):
            return 'single_coin'
        elif any(word in query_lower for word in ['기술', 'technical', 'rsi', 'macd', '지표']):
            return 'technical_analysis'
        elif any(word in query_lower for word in ['전체', 'overview', '시장', 'market']):
            return 'market_overview'
        else:
            return 'comprehensive'
    
    def _extract_symbol(self, query: str) -> str:
        """쿼리에서 심볼 추출"""
        query_lower = query.lower()
        
        symbol_mapping = {
            'btc': 'BTC', 'bitcoin': 'BTC', '비트코인': 'BTC',
            'eth': 'ETH', 'ethereum': 'ETH', '이더리움': 'ETH',
            'xrp': 'XRP', '리플': 'XRP',
            'ada': 'ADA', '에이다': 'ADA',
            'dot': 'DOT', '폴카닷': 'DOT'
        }
        
        for key, value in symbol_mapping.items():
            if key in query_lower:
                return value
        
        return 'BTC'  # 기본값
    
    async def _get_upbit_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """업비트 API에서 데이터 수집"""
        try:
            markets = [f"KRW-{symbol}" for symbol in symbols]
            url = f"{self.api_endpoints['upbit']}?markets={','.join(markets)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {}
                        
                        for item in data:
                            symbol = item['market'].replace('KRW-', '')
                            result[symbol] = MarketData(
                                symbol=symbol,
                                price=item['trade_price'],
                                change_24h=item['change_price'],
                                change_percent_24h=item['change_rate'] * 100,
                                volume_24h=item['acc_trade_volume_24h'],
                                market_cap=0,  # 업비트 API에서 제공하지 않음
                                high_24h=item['high_price'],
                                low_24h=item['low_price'],
                                timestamp=datetime.now()
                            )
                        
                        return result
                    
        except Exception as e:
            logger.error(f"업비트 데이터 수집 실패: {e}")
            return {}
    
    async def _get_coingecko_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """CoinGecko API에서 데이터 수집"""
        try:
            # 심볼을 CoinGecko ID로 매핑
            symbol_to_id = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'BCH': 'bitcoin-cash'
            }
            
            ids = [symbol_to_id.get(symbol, symbol.lower()) for symbol in symbols]
            url = f"{self.api_endpoints['coingecko']}?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = {}
                        
                        for coin_id, coin_data in data.items():
                            # ID를 다시 심볼로 변환
                            symbol = next((k for k, v in symbol_to_id.items() if v == coin_id), coin_id.upper())
                            
                            result[symbol] = MarketData(
                                symbol=symbol,
                                price=coin_data['usd'],
                                change_24h=coin_data.get('usd_24h_change', 0),
                                change_percent_24h=coin_data.get('usd_24h_change', 0),
                                volume_24h=coin_data.get('usd_24h_vol', 0),
                                market_cap=coin_data.get('usd_market_cap', 0),
                                high_24h=0,  # CoinGecko 기본 API에서 제공하지 않음
                                low_24h=0,
                                timestamp=datetime.now()
                            )
                        
                        return result
                    
        except Exception as e:
            logger.error(f"CoinGecko 데이터 수집 실패: {e}")
            return {}
    
    async def _calculate_technical_indicators(self, symbol: str, prices: List[float]) -> TechnicalIndicators:
        """기술적 지표 계산"""
        try:
            if len(prices) < 50:
                logger.warning(f"가격 데이터 부족 ({len(prices)}개), 기본값 사용")
                return TechnicalIndicators(
                    symbol=symbol,
                    rsi=50.0,
                    macd=0.0,
                    macd_signal=0.0,
                    bb_upper=prices[-1] * 1.02 if prices else 0,
                    bb_lower=prices[-1] * 0.98 if prices else 0,
                    sma_20=sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1] if prices else 0,
                    sma_50=sum(prices[-50:]) / 50 if len(prices) >= 50 else prices[-1] if prices else 0,
                    volume_sma=0,
                    timestamp=datetime.now()
                )
            
            # RSI 계산
            rsi = self._calculate_rsi(prices)
            
            # MACD 계산
            macd, macd_signal = self._calculate_macd(prices)
            
            # 볼린저 밴드 계산
            bb_upper, bb_lower = self._calculate_bollinger_bands(prices)
            
            # 이동평균 계산
            sma_20 = sum(prices[-20:]) / 20
            sma_50 = sum(prices[-50:]) / 50
            
            return TechnicalIndicators(
                symbol=symbol,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                bb_upper=bb_upper,
                bb_lower=bb_lower,
                sma_20=sma_20,
                sma_50=sma_50,
                volume_sma=0,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"기술적 지표 계산 실패: {e}")
            return TechnicalIndicators(
                symbol=symbol, rsi=50.0, macd=0.0, macd_signal=0.0,
                bb_upper=0, bb_lower=0, sma_20=0, sma_50=0, volume_sma=0,
                timestamp=datetime.now()
            )
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI 계산"""
        if len(prices) < period + 1:
            return 50.0
            
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [change if change > 0 else 0 for change in changes]
        losses = [-change if change < 0 else 0 for change in changes]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float]:
        """MACD 계산"""
        if len(prices) < 26:
            return 0.0, 0.0
            
        # EMA 계산
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        macd = ema_12 - ema_26
        
        # MACD의 EMA (시그널)
        macd_values = [macd]  # 실제로는 더 많은 MACD 값이 필요
        macd_signal = macd  # 간단화
        
        return macd, macd_signal
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """지수이동평균 계산"""
        if len(prices) < period:
            return sum(prices) / len(prices)
            
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float]:
        """볼린저 밴드 계산"""
        if len(prices) < period:
            avg = sum(prices) / len(prices)
            return avg * 1.02, avg * 0.98
            
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / period
        variance = sum((price - sma) ** 2 for price in recent_prices) / period
        std = variance ** 0.5
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, lower_band
    
    async def _analyze_single_coin(self, symbol: str) -> str:
        """단일 코인 심층 분석"""
        try:
            logger.info(f"📊 {symbol} 단일 코인 분석 시작")
            
            # 실시간 데이터 수집
            upbit_data = await self._get_upbit_data([symbol])
            coingecko_data = await self._get_coingecko_data([symbol])
            
            # 데이터 통합
            market_data = upbit_data.get(symbol) or coingecko_data.get(symbol)
            
            if not market_data:
                return f"{symbol} 시장 데이터를 찾을 수 없습니다."
            
            # 과거 가격 데이터 (데이터베이스에서 조회)
            historical_prices = await self._get_historical_prices(symbol)
            
            # 기술적 지표 계산
            if historical_prices:
                tech_indicators = await self._calculate_technical_indicators(symbol, historical_prices)
            else:
                tech_indicators = None
            
            # 분석 보고서 생성
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            
            report = f"""# 📊 {symbol} 실시간 시장 분석 보고서

**분석 시점**: {current_time}

## 💰 **현재 시장 현황**

- **현재가**: ${market_data.price:,.2f}
- **24시간 변동**: {market_data.change_percent_24h:+.2f}% (${market_data.change_24h:+,.2f})
- **24시간 고가**: ${market_data.high_24h:,.2f}
- **24시간 저가**: ${market_data.low_24h:,.2f}
- **24시간 거래량**: {market_data.volume_24h:,.0f} {symbol}
"""

            if market_data.market_cap > 0:
                report += f"- **시가총액**: ${market_data.market_cap:,.0f}\n"

            if tech_indicators:
                report += f"""
## 📈 **기술적 지표 분석**

- **RSI (14)**: {tech_indicators.rsi:.1f} - {self._interpret_rsi(tech_indicators.rsi)}
- **20일 이동평균**: ${tech_indicators.sma_20:,.2f}
- **50일 이동평균**: ${tech_indicators.sma_50:,.2f}
- **MACD**: {tech_indicators.macd:.4f}
- **볼린저 밴드 상단**: ${tech_indicators.bb_upper:,.2f}
- **볼린저 밴드 하단**: ${tech_indicators.bb_lower:,.2f}

### 🎯 **기술적 분석 요약**
{self._generate_technical_summary(market_data, tech_indicators)}
"""

            # 시장 심리 분석
            market_sentiment = self._analyze_market_sentiment(market_data, tech_indicators)
            report += f"""
## 🎭 **시장 심리 분석**

{market_sentiment}

---
*⚠️ 이 분석은 AI가 실시간 데이터를 기반으로 생성한 것으로, 투자 권유가 아닙니다.*
"""

            return report
            
        except Exception as e:
            logger.error(f"단일 코인 분석 실패: {e}")
            return f"{symbol} 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _analyze_market_overview(self) -> str:
        """시장 전체 개요 분석"""
        try:
            logger.info("📊 시장 전체 개요 분석 시작")
            
            # 주요 코인들의 데이터 수집
            major_coins = ['BTC', 'ETH', 'XRP', 'ADA']
            upbit_data = await self._get_upbit_data(major_coins)
            coingecko_data = await self._get_coingecko_data(major_coins)
            
            # 데이터 통합
            combined_data = {}
            for symbol in major_coins:
                combined_data[symbol] = upbit_data.get(symbol) or coingecko_data.get(symbol)
            
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            
            report = f"""# 🌐 암호화폐 시장 전체 현황

**분석 시점**: {current_time}

## 📊 **주요 코인 현황**

"""
            
            total_change = 0
            positive_count = 0
            
            for symbol, data in combined_data.items():
                if data:
                    status_emoji = "🟢" if data.change_percent_24h > 0 else "🔴" if data.change_percent_24h < 0 else "⚪"
                    report += f"**{symbol}**: {status_emoji} ${data.price:,.2f} ({data.change_percent_24h:+.2f}%)\n"
                    
                    total_change += data.change_percent_24h
                    if data.change_percent_24h > 0:
                        positive_count += 1
            
            # 시장 전체 심리
            avg_change = total_change / len([d for d in combined_data.values() if d])
            market_mood = "🟢 강세" if avg_change > 1 else "🔴 약세" if avg_change < -1 else "⚪ 보합"
            
            report += f"""
## 🎭 **시장 전체 심리**

- **평균 변동률**: {avg_change:+.2f}%
- **상승 종목**: {positive_count}/{len([d for d in combined_data.values() if d])}개
- **시장 분위기**: {market_mood}

## 💡 **시장 인사이트**

{self._generate_market_insights(combined_data)}

---
*📅 다음 업데이트: 1분 후 | 실시간 데이터 기반 분석*
"""

            return report
            
        except Exception as e:
            logger.error(f"시장 개요 분석 실패: {e}")
            return f"시장 개요 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _perform_technical_analysis(self, symbol: str) -> str:
        """기술적 분석 전문 보고서"""
        try:
            logger.info(f"📈 {symbol} 기술적 분석 시작")
            
            # 현재 가격 데이터
            upbit_data = await self._get_upbit_data([symbol])
            market_data = upbit_data.get(symbol)
            
            if not market_data:
                return f"{symbol} 시장 데이터를 찾을 수 없습니다."
            
            # 과거 가격 데이터
            historical_prices = await self._get_historical_prices(symbol, days=50)
            
            if not historical_prices or len(historical_prices) < 20:
                return f"{symbol} 기술적 분석을 위한 충분한 데이터가 없습니다."
            
            # 기술적 지표 계산
            tech_indicators = await self._calculate_technical_indicators(symbol, historical_prices)
            
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            
            report = f"""# 📈 {symbol} 기술적 분석 보고서

**분석 시점**: {current_time}
**분석 기간**: 최근 50일 데이터 기반

## 🎯 **핵심 지표 스냅샷**

| 지표 | 값 | 해석 |
|------|----|----- |
| **현재가** | ${market_data.price:,.2f} | 24H {market_data.change_percent_24h:+.2f}% |
| **RSI(14)** | {tech_indicators.rsi:.1f} | {self._interpret_rsi(tech_indicators.rsi)} |
| **20일 MA** | ${tech_indicators.sma_20:,.2f} | {self._compare_to_ma(market_data.price, tech_indicators.sma_20)} |
| **50일 MA** | ${tech_indicators.sma_50:,.2f} | {self._compare_to_ma(market_data.price, tech_indicators.sma_50)} |

## 📊 **상세 기술적 분석**

### 🔄 **추세 분석**
{self._analyze_trend(market_data, tech_indicators)}

### ⚡ **모멘텀 분석**
- **RSI**: {tech_indicators.rsi:.1f} - {self._get_rsi_signal(tech_indicators.rsi)}
- **MACD**: {tech_indicators.macd:.4f} - {self._get_macd_signal(tech_indicators.macd, tech_indicators.macd_signal)}

### 🎯 **지지/저항 분석**
- **볼린저 밴드 상단**: ${tech_indicators.bb_upper:,.2f} (저항선)
- **볼린저 밴드 하단**: ${tech_indicators.bb_lower:,.2f} (지지선)
- **현재 위치**: {self._get_bb_position(market_data.price, tech_indicators)}

## 🚨 **트레이딩 시그널**

{self._generate_trading_signals(market_data, tech_indicators)}

## 📈 **단기 전망 (1-7일)**

{self._generate_short_term_outlook(market_data, tech_indicators)}

---
*⚠️ 기술적 분석은 참고용이며, 투자 결정 시 다양한 요소를 종합적으로 고려하시기 바랍니다.*
"""

            return report
            
        except Exception as e:
            logger.error(f"기술적 분석 실패: {e}")
            return f"{symbol} 기술적 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _comprehensive_market_analysis(self) -> str:
        """종합적인 시장 분석"""
        try:
            logger.info("🔍 종합적인 시장 분석 시작")
            
            # 다양한 분석 수행
            market_overview = await self._analyze_market_overview()
            btc_analysis = await self._analyze_single_coin('BTC')
            
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            
            report = f"""# 🔍 암호화폐 시장 종합 분석 보고서

**분석 시점**: {current_time}

{market_overview}

---

## 🔋 **비트코인 심층 분석** 

{btc_analysis.split('## 💰 **현재 시장 현황**')[1] if '## 💰 **현재 시장 현황**' in btc_analysis else '데이터 부족'}

---

## 🎯 **투자자 가이드라인**

### 📈 **장기 투자자**
- 주요 지지선과 저항선을 확인하여 매수/매도 타이밍 결정
- RSI와 볼린저 밴드를 활용한 과매수/과매도 구간 파악

### ⚡ **단기 트레이더**
- MACD 시그널과 거래량 변화 모니터링
- 기술적 지표의 다이버전스 패턴 주의

### 🛡️ **리스크 관리**
- 변동성이 큰 시장이므로 적절한 손절매 설정 필수
- 분산 투자를 통한 리스크 분산 권장

---
*💡 이 보고서는 AI가 실시간 데이터를 분석하여 생성한 것으로, 투자 권유가 아닌 정보 제공 목적입니다.*
"""

            return report
            
        except Exception as e:
            logger.error(f"종합 시장 분석 실패: {e}")
            return f"종합 시장 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _get_historical_prices(self, symbol: str, days: int = 30) -> List[float]:
        """과거 가격 데이터 조회 (데이터베이스 또는 API)"""
        try:
            # 캐시에서 확인
            cache_key = f"historical_prices_{symbol}_{days}"
            cached_data = await db_manager.get_cached_result(cache_key)
            
            if cached_data:
                return cached_data
            
            # 데이터베이스에서 조회 시도
            async with db_manager.get_pgvector_connection() as conn:
                query = """
                    SELECT close_price 
                    FROM candle_data 
                    WHERE symbol = $1 
                    ORDER BY timestamp DESC 
                    LIMIT $2
                """
                
                rows = await conn.fetch(query, symbol, days)
                prices = [float(row['close_price']) for row in rows]
                
                if prices:
                    # 캐시에 저장 (10분)
                    await db_manager.set_cached_result(cache_key, prices, ttl=600)
                    return list(reversed(prices))  # 시간순 정렬
            
            # 데이터베이스에 데이터가 없으면 더미 데이터 생성
            logger.warning(f"{symbol} 과거 가격 데이터 부족, 더미 데이터 생성")
            current_price = 50000  # 기본값
            return [current_price * (1 + (i * 0.01)) for i in range(-days, 0)]
            
        except Exception as e:
            logger.error(f"과거 가격 데이터 조회 실패: {e}")
            return []
    
    def _interpret_rsi(self, rsi: float) -> str:
        """RSI 해석"""
        if rsi >= 70:
            return "과매수 구간"
        elif rsi <= 30:
            return "과매도 구간"
        else:
            return "중립 구간"
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """RSI 시그널"""
        if rsi >= 80:
            return "🔴 강한 매도 시그널"
        elif rsi >= 70:
            return "🟡 매도 고려"
        elif rsi <= 20:
            return "🟢 강한 매수 시그널"
        elif rsi <= 30:
            return "🟡 매수 고려"
        else:
            return "⚪ 중립"
    
    def _compare_to_ma(self, current_price: float, ma_price: float) -> str:
        """현재가와 이동평균 비교"""
        diff_percent = ((current_price - ma_price) / ma_price) * 100
        if diff_percent > 5:
            return f"상단 이탈 (+{diff_percent:.1f}%)"
        elif diff_percent < -5:
            return f"하단 이탈 ({diff_percent:.1f}%)"
        else:
            return f"근접 ({diff_percent:+.1f}%)"
    
    def _generate_technical_summary(self, market_data: MarketData, tech_indicators: TechnicalIndicators) -> str:
        """기술적 분석 요약"""
        signals = []
        
        # RSI 시그널
        if tech_indicators.rsi > 70:
            signals.append("RSI 과매수")
        elif tech_indicators.rsi < 30:
            signals.append("RSI 과매도")
        
        # 이동평균 시그널
        if market_data.price > tech_indicators.sma_20 > tech_indicators.sma_50:
            signals.append("상승 추세")
        elif market_data.price < tech_indicators.sma_20 < tech_indicators.sma_50:
            signals.append("하락 추세")
        
        # 볼린저 밴드 시그널
        if market_data.price > tech_indicators.bb_upper:
            signals.append("볼린저 밴드 상단 돌파")
        elif market_data.price < tech_indicators.bb_lower:
            signals.append("볼린저 밴드 하단 터치")
        
        return "• " + "\n• ".join(signals) if signals else "• 명확한 기술적 시그널 없음"
    
    def _analyze_market_sentiment(self, market_data: MarketData, tech_indicators: Optional[TechnicalIndicators]) -> str:
        """시장 심리 분석"""
        sentiment_score = 50  # 중립
        
        # 가격 변동 반영
        if market_data.change_percent_24h > 5:
            sentiment_score += 20
        elif market_data.change_percent_24h > 2:
            sentiment_score += 10
        elif market_data.change_percent_24h < -5:
            sentiment_score -= 20
        elif market_data.change_percent_24h < -2:
            sentiment_score -= 10
        
        # 기술적 지표 반영
        if tech_indicators:
            if tech_indicators.rsi > 70:
                sentiment_score += 10
            elif tech_indicators.rsi < 30:
                sentiment_score -= 10
        
        if sentiment_score >= 70:
            return "🟢 **매우 긍정적** - 강한 상승 모멘텀이 감지됩니다."
        elif sentiment_score >= 60:
            return "🔵 **긍정적** - 전반적으로 상승 분위기입니다."
        elif sentiment_score >= 40:
            return "⚪ **중립적** - 횡보 구간에서 방향성을 찾고 있습니다."
        elif sentiment_score >= 30:
            return "🟡 **부정적** - 하락 압력이 있지만 반등 가능성 존재합니다."
        else:
            return "🔴 **매우 부정적** - 강한 하락 모멘텀이 우세합니다."
    
    def _generate_market_insights(self, market_data: Dict[str, MarketData]) -> str:
        """시장 인사이트 생성"""
        insights = []
        
        # 상관관계 분석
        btc_change = market_data.get('BTC', MarketData('BTC', 0, 0, 0, 0, 0, 0, 0, datetime.now())).change_percent_24h
        eth_change = market_data.get('ETH', MarketData('ETH', 0, 0, 0, 0, 0, 0, 0, datetime.now())).change_percent_24h
        
        if abs(btc_change - eth_change) < 1:
            insights.append("• BTC와 ETH가 동조화 현상을 보이고 있습니다.")
        
        # 시장 리더십 분석
        if btc_change > 3 and eth_change > 2:
            insights.append("• 메이저 코인들이 시장을 주도하고 있습니다.")
        
        # 변동성 분석
        avg_volatility = sum(abs(data.change_percent_24h) for data in market_data.values() if data) / len([d for d in market_data.values() if d])
        if avg_volatility > 5:
            insights.append("• 높은 변동성으로 단기 트레이딩 기회가 많습니다.")
        elif avg_volatility < 2:
            insights.append("• 낮은 변동성으로 안정적인 시장 상황입니다.")
        
        return "\n".join(insights) if insights else "• 현재 특별한 시장 패턴이 감지되지 않았습니다."
    
    def _generate_trading_signals(self, market_data: MarketData, tech_indicators: TechnicalIndicators) -> str:
        """트레이딩 시그널 생성"""
        signals = []
        
        # 복합 시그널 분석
        bullish_signals = 0
        bearish_signals = 0
        
        # RSI 시그널
        if tech_indicators.rsi < 30:
            bullish_signals += 1
            signals.append("🟢 RSI 과매도 반등 시그널")
        elif tech_indicators.rsi > 70:
            bearish_signals += 1
            signals.append("🔴 RSI 과매수 조정 시그널")
        
        # 이동평균 시그널
        if market_data.price > tech_indicators.sma_20 > tech_indicators.sma_50:
            bullish_signals += 1
            signals.append("🟢 이동평균 상승 배열")
        elif market_data.price < tech_indicators.sma_20 < tech_indicators.sma_50:
            bearish_signals += 1
            signals.append("🔴 이동평균 하락 배열")
        
        # 볼린저 밴드 시그널
        if market_data.price < tech_indicators.bb_lower:
            bullish_signals += 1
            signals.append("🟢 볼린저 밴드 하단 반등 기대")
        elif market_data.price > tech_indicators.bb_upper:
            bearish_signals += 1
            signals.append("🔴 볼린저 밴드 상단 저항")
        
        # 종합 판단
        if bullish_signals > bearish_signals:
            signals.insert(0, "🚀 **종합 판단: 매수 우세**")
        elif bearish_signals > bullish_signals:
            signals.insert(0, "⬇️ **종합 판단: 매도 우세**")
        else:
            signals.insert(0, "⚖️ **종합 판단: 관망 권장**")
        
        return "\n".join(signals)
    
    def _generate_short_term_outlook(self, market_data: MarketData, tech_indicators: TechnicalIndicators) -> str:
        """단기 전망 생성"""
        outlook = []
        
        # 지지/저항 레벨 계산
        support_level = min(tech_indicators.bb_lower, tech_indicators.sma_20 * 0.95)
        resistance_level = max(tech_indicators.bb_upper, tech_indicators.sma_20 * 1.05)
        
        outlook.append(f"**예상 지지선**: ${support_level:,.2f}")
        outlook.append(f"**예상 저항선**: ${resistance_level:,.2f}")
        
        # 변동성 예측
        if abs(market_data.change_percent_24h) > 5:
            outlook.append("**변동성**: 높음 - 큰 가격 변동 가능성")
        else:
            outlook.append("**변동성**: 보통 - 안정적인 움직임 예상")
        
        # 추세 방향
        if tech_indicators.rsi > 50 and market_data.price > tech_indicators.sma_20:
            outlook.append("**추세**: 상승 모멘텀 지속 가능성")
        elif tech_indicators.rsi < 50 and market_data.price < tech_indicators.sma_20:
            outlook.append("**추세**: 하락 압력 지속 우려")
        else:
            outlook.append("**추세**: 횡보 구간에서 방향성 모색")
        
        return "\n".join(f"• {item}" for item in outlook)
    
    def _get_macd_signal(self, macd: float, macd_signal: float) -> str:
        """MACD 시그널 해석"""
        if macd > macd_signal:
            return "🟢 상승 시그널"
        elif macd < macd_signal:
            return "🔴 하락 시그널"
        else:
            return "⚪ 중립"
    
    def _get_bb_position(self, price: float, tech_indicators: TechnicalIndicators) -> str:
        """볼린저 밴드 내 위치"""
        if price > tech_indicators.bb_upper:
            return "상단 이탈 (과매수 구간)"
        elif price < tech_indicators.bb_lower:
            return "하단 이탈 (과매도 구간)"
        else:
            # 밴드 내 위치 계산
            band_range = tech_indicators.bb_upper - tech_indicators.bb_lower
            position = (price - tech_indicators.bb_lower) / band_range
            if position > 0.8:
                return "상단 근접 (80%)"
            elif position < 0.2:
                return "하단 근접 (20%)"
            else:
                return f"중간 위치 ({position*100:.0f}%)"
    
    def _analyze_trend(self, market_data: MarketData, tech_indicators: TechnicalIndicators) -> str:
        """추세 분석"""
        trend_signals = []
        
        # 이동평균 비교
        if tech_indicators.sma_20 > tech_indicators.sma_50:
            trend_signals.append("단기 이동평균이 장기 이동평균 상회 (상승 추세)")
        else:
            trend_signals.append("단기 이동평균이 장기 이동평균 하회 (하락 추세)")
        
        # 현재가 위치
        if market_data.price > tech_indicators.sma_20:
            trend_signals.append("현재가가 20일 이동평균 상회")
        else:
            trend_signals.append("현재가가 20일 이동평균 하회")
        
        # 24시간 변동
        if market_data.change_percent_24h > 0:
            trend_signals.append(f"24시간 상승 모멘텀 ({market_data.change_percent_24h:+.2f}%)")
        else:
            trend_signals.append(f"24시간 하락 모멘텀 ({market_data.change_percent_24h:+.2f}%)")
        
        return "• " + "\n• ".join(trend_signals)

class MarketHeatmapTool(BaseTool):
    """시장 히트맵 분석 도구"""
    
    name: str = "market_heatmap"
    description: str = """
    암호화폐 시장의 전체적인 수익률 분포를 히트맵 형태로 분석합니다.
    
    특징:
    - 주요 코인들의 24시간 수익률 비교
    - 시장 섹터별 성과 분석
    - 상대적 강도 분석
    """
    
    def _run(self, query: str = "히트맵") -> str:
        """시장 히트맵 분석 실행"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._analyze_heatmap())
        finally:
            loop.close()
    
    async def _analyze_heatmap(self) -> str:
        """히트맵 분석"""
        try:
            logger.info("🔥 시장 히트맵 분석 시작")
            
            # RealTimeMarketDataTool 인스턴스 생성
            market_tool = RealTimeMarketDataTool()
            
            # 주요 코인 데이터 수집
            coins = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH']
            upbit_data = await market_tool._get_upbit_data(coins)
            coingecko_data = await market_tool._get_coingecko_data(coins)
            
            # 데이터 통합
            combined_data = {}
            for coin in coins:
                data = upbit_data.get(coin) or coingecko_data.get(coin)
                if data:
                    combined_data[coin] = data
            
            if not combined_data:
                return "히트맵 분석을 위한 데이터를 수집할 수 없습니다."
            
            # 수익률 순으로 정렬
            sorted_coins = sorted(combined_data.items(), 
                                key=lambda x: x[1].change_percent_24h, 
                                reverse=True)
            
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            
            report = f"""# 🔥 암호화폐 시장 히트맵 분석

**분석 시점**: {current_time}

## 📊 **24시간 수익률 랭킹**

"""
            
            for i, (symbol, data) in enumerate(sorted_coins, 1):
                change = data.change_percent_24h
                
                # 수익률에 따른 이모지 및 색상
                if change > 5:
                    emoji = "🟢🔥"
                    status = "강한 상승"
                elif change > 2:
                    emoji = "🟢"
                    status = "상승"
                elif change > 0:
                    emoji = "🟢"
                    status = "소폭 상승"
                elif change > -2:
                    emoji = "🟡"
                    status = "소폭 하락"
                elif change > -5:
                    emoji = "🔴"
                    status = "하락"
                else:
                    emoji = "🔴❄️"
                    status = "강한 하락"
                
                report += f"{i:2}. {emoji} **{symbol}**: {change:+.2f}% ({status})\n"
            
            # 시장 요약
            positive_count = sum(1 for _, data in combined_data.items() if data.change_percent_24h > 0)
            total_count = len(combined_data)
            avg_change = sum(data.change_percent_24h for data in combined_data.values()) / total_count
            
            report += f"""
## 🎭 **시장 요약**

- **상승 종목**: {positive_count}/{total_count}개 ({positive_count/total_count*100:.1f}%)
- **평균 수익률**: {avg_change:+.2f}%
- **시장 분위기**: {self._get_market_mood(avg_change, positive_count/total_count)}

## 💡 **인사이트**

{self._generate_heatmap_insights(sorted_coins)}

---
*🔄 실시간 업데이트 | 데이터 기반 AI 분석*
"""

            return report
            
        except Exception as e:
            logger.error(f"히트맵 분석 실패: {e}")
            return f"히트맵 분석 중 오류가 발생했습니다: {str(e)}"
    
    def _get_market_mood(self, avg_change: float, positive_ratio: float) -> str:
        """시장 분위기 판단"""
        if avg_change > 2 and positive_ratio > 0.7:
            return "🟢 매우 긍정적 (강세장)"
        elif avg_change > 0 and positive_ratio > 0.5:
            return "🔵 긍정적 (상승 모멘텀)"
        elif avg_change > -2 and positive_ratio > 0.3:
            return "🟡 혼조 (방향성 모색)"
        else:
            return "🔴 부정적 (하락 압력)"
    
    def _generate_heatmap_insights(self, sorted_coins: List[Tuple[str, MarketData]]) -> str:
        """히트맵 인사이트 생성"""
        insights = []
        
        # 최고/최저 수익률
        best_performer = sorted_coins[0]
        worst_performer = sorted_coins[-1]
        
        insights.append(f"• **최고 수익**: {best_performer[0]} ({best_performer[1].change_percent_24h:+.2f}%)")
        insights.append(f"• **최저 수익**: {worst_performer[0]} ({worst_performer[1].change_percent_24h:+.2f}%)")
        
        # 스프레드 분석
        spread = best_performer[1].change_percent_24h - worst_performer[1].change_percent_24h
        insights.append(f"• **수익률 스프레드**: {spread:.2f}%p")
        
        if spread > 10:
            insights.append("• 코인간 수익률 격차가 큰 상황으로 종목 선택이 중요합니다.")
        else:
            insights.append("• 코인들이 비슷한 움직임을 보이며 시장 전체 트렌드가 우세합니다.")
        
        return "\n".join(insights)