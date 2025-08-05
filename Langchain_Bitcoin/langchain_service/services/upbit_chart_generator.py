"""
Upbit API + Plotly 차트 생성기
실시간 데이터로 전문적인 기술 분석 차트 생성
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
import base64
import io
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time

logger = logging.getLogger(__name__)

class UpbitChartGenerator:
    def __init__(self):
        self.base_url = "https://api.upbit.com/v1"
        
    def get_candle_data(self, market: str = "KRW-BTC", count: int = 365, unit: str = "days") -> pd.DataFrame:
        """Upbit API에서 캔들 데이터 가져오기"""
        try:
            logger.info(f"📊 Upbit에서 {market} 데이터 수집 중... ({count}개)")
            
            if unit == "days":
                url = f"{self.base_url}/candles/days"
            elif unit == "minutes":
                url = f"{self.base_url}/candles/minutes/1"
            else:
                url = f"{self.base_url}/candles/days"
            
            params = {
                "market": market,
                "count": count
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.error("Upbit API에서 데이터를 받아오지 못했습니다.")
                return pd.DataFrame()
            
            # DataFrame 생성
            df = pd.DataFrame(data)
            df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
            df = df.sort_values('candle_date_time_kst').reset_index(drop=True)
            
            # 컬럼명 정리
            df = df.rename(columns={
                'candle_date_time_kst': 'datetime',
                'opening_price': 'open',
                'high_price': 'high',
                'low_price': 'low',
                'trade_price': 'close',
                'candle_acc_trade_volume': 'volume'
            })
            
            logger.info(f"✅ {len(df)}개 데이터 수집 완료")
            return df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"❌ Upbit 데이터 수집 실패: {e}")
            return pd.DataFrame()
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """이동평균선 계산 (5, 20, 60, 120일선)"""
        try:
            df = df.copy()
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma60'] = df['close'].rolling(window=60).mean()
            df['ma120'] = df['close'].rolling(window=120).mean()
            
            logger.info("✅ 이동평균선 계산 완료")
            return df
            
        except Exception as e:
            logger.error(f"❌ 이동평균선 계산 실패: {e}")
            return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """RSI 계산"""
        try:
            df = df.copy()
            delta = df['close'].diff()
            
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            logger.info("✅ RSI 계산 완료")
            return df
            
        except Exception as e:
            logger.error(f"❌ RSI 계산 실패: {e}")
            return df
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD 계산"""
        try:
            df = df.copy()
            
            # EMA 계산
            ema_fast = df['close'].ewm(span=fast).mean()
            ema_slow = df['close'].ewm(span=slow).mean()
            
            # MACD 라인
            df['macd'] = ema_fast - ema_slow
            
            # Signal 라인
            df['macd_signal'] = df['macd'].ewm(span=signal).mean()
            
            # Histogram
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            logger.info("✅ MACD 계산 완료")
            return df
            
        except Exception as e:
            logger.error(f"❌ MACD 계산 실패: {e}")
            return df
    
    def generate_comprehensive_chart(self, market: str = "KRW-BTC", days: int = 365) -> str:
        """종합 기술 분석 차트 생성"""
        try:
            logger.info(f"🚀 {market} 종합 차트 생성 시작 ({days}일)")
            
            # 데이터 수집
            df = self.get_candle_data(market, days)
            if df.empty:
                return "데이터를 가져올 수 없습니다."
            
            # 기술적 지표 계산
            df = self.calculate_moving_averages(df)
            df = self.calculate_rsi(df)
            df = self.calculate_macd(df)
            
            # 4개 서브플롯 생성 (가격, 거래량, RSI, MACD)
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(
                    f'{market} 가격 차트 & 이동평균선',
                    '거래량',
                    'RSI (14일)',
                    'MACD'
                ),
                row_heights=[0.5, 0.15, 0.15, 0.2]
            )
            
            # 1. 캔들스틱 차트
            fig.add_trace(
                go.Candlestick(
                    x=df['datetime'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='가격',
                    increasing_line_color='red',
                    decreasing_line_color='blue'
                ),
                row=1, col=1
            )
            
            # 2. 이동평균선들
            ma_colors = {
                'ma5': '#FF6B6B',    # 빨강
                'ma20': '#4ECDC4',   # 청록
                'ma60': '#45B7D1',   # 파랑
                'ma120': '#96CEB4'   # 초록
            }
            
            ma_names = {
                'ma5': '5일선',
                'ma20': '20일선', 
                'ma60': '60일선',
                'ma120': '120일선'
            }
            
            for ma_col, color in ma_colors.items():
                if ma_col in df.columns and not df[ma_col].isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df['datetime'],
                            y=df[ma_col],
                            mode='lines',
                            name=ma_names[ma_col],
                            line=dict(color=color, width=1.5)
                        ),
                        row=1, col=1
                    )
            
            # 3. 거래량
            colors = ['red' if close >= open else 'blue' 
                     for close, open in zip(df['close'], df['open'])]
            
            fig.add_trace(
                go.Bar(
                    x=df['datetime'],
                    y=df['volume'],
                    name='거래량',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # 4. RSI
            if 'rsi' in df.columns and not df['rsi'].isna().all():
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=df['rsi'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='purple', width=2)
                    ),
                    row=3, col=1
                )
                
                # RSI 과매수/과매도 선
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="blue", opacity=0.7, row=3, col=1)
                fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.5, row=3, col=1)
            
            # 5. MACD
            if 'macd' in df.columns and not df['macd'].isna().all():
                # MACD 라인
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=df['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ),
                    row=4, col=1
                )
                
                # Signal 라인
                fig.add_trace(
                    go.Scatter(
                        x=df['datetime'],
                        y=df['macd_signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color='red', width=2)
                    ),
                    row=4, col=1
                )
                
                # Histogram
                histogram_colors = ['green' if val >= 0 else 'red' for val in df['macd_histogram']]
                fig.add_trace(
                    go.Bar(
                        x=df['datetime'],
                        y=df['macd_histogram'],
                        name='Histogram',
                        marker_color=histogram_colors,
                        opacity=0.6
                    ),
                    row=4, col=1
                )
            
            # 레이아웃 설정
            fig.update_layout(
                title=f'{market} 종합 기술 분석 차트 ({days}일)',
                template='plotly_white',
                showlegend=True,
                height=1200,
                width=1400,
                font=dict(size=10)
            )
            
            # Y축 설정
            fig.update_yaxes(title_text="가격 (KRW)", row=1, col=1)
            fig.update_yaxes(title_text="거래량", row=2, col=1)
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
            fig.update_yaxes(title_text="MACD", row=4, col=1)
            
            # X축 설정 (맨 아래만)
            fig.update_xaxes(title_text="날짜", row=4, col=1)
            
            # 이미지로 변환
            img_bytes = fig.to_image(format="png", width=1400, height=1200)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            logger.info(f"✅ {market} 종합 차트 생성 완료")
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"❌ 종합 차트 생성 실패: {e}")
            return f"차트 생성 실패: {str(e)}"
    
    def generate_simple_price_chart(self, market: str = "KRW-BTC", days: int = 30) -> str:
        """간단한 가격 + 이동평균 차트"""
        try:
            logger.info(f"📈 {market} 간단 차트 생성 ({days}일)")
            
            # 데이터 수집
            df = self.get_candle_data(market, days)
            if df.empty:
                return "데이터를 가져올 수 없습니다."
            
            # 이동평균 계산
            df = self.calculate_moving_averages(df)
            
            # 차트 생성
            fig = go.Figure()
            
            # 캔들스틱
            fig.add_trace(
                go.Candlestick(
                    x=df['datetime'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='가격'
                )
            )
            
            # 이동평균선들
            ma_settings = [
                ('ma5', '5일선', '#FF6B6B'),
                ('ma20', '20일선', '#4ECDC4'),
                ('ma60', '60일선', '#45B7D1'),
                ('ma120', '120일선', '#96CEB4')
            ]
            
            for ma_col, name, color in ma_settings:
                if ma_col in df.columns and not df[ma_col].isna().all():
                    fig.add_trace(
                        go.Scatter(
                            x=df['datetime'],
                            y=df[ma_col],
                            mode='lines',
                            name=name,
                            line=dict(color=color, width=2)
                        )
                    )
            
            fig.update_layout(
                title=f'{market} 가격 차트 & 이동평균선 ({days}일)',
                xaxis_title='날짜',
                yaxis_title='가격 (KRW)',
                template='plotly_white',
                height=600,
                width=1000
            )
            
            # 이미지로 변환
            img_bytes = fig.to_image(format="png", width=1000, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            logger.info(f"✅ {market} 간단 차트 완료")
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"❌ 간단 차트 생성 실패: {e}")
            return f"차트 생성 실패: {str(e)}"
    
    def get_market_analysis(self, market: str = "KRW-BTC", days: int = 30) -> Dict[str, Any]:
        """시장 분석 데이터 생성"""
        try:
            df = self.get_candle_data(market, days)
            if df.empty:
                return {}
            
            df = self.calculate_moving_averages(df)
            df = self.calculate_rsi(df)
            df = self.calculate_macd(df)
            
            latest = df.iloc[-1]
            
            analysis = {
                'current_price': latest['close'],
                'price_change_24h': ((latest['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close']) * 100,
                'volume_24h': latest['volume'],
                'ma5': latest.get('ma5'),
                'ma20': latest.get('ma20'),
                'ma60': latest.get('ma60'),
                'ma120': latest.get('ma120'),
                'rsi': latest.get('rsi'),
                'macd': latest.get('macd'),
                'macd_signal': latest.get('macd_signal')
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"시장 분석 실패: {e}")
            return {}