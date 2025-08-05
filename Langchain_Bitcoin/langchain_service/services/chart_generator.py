"""
가격 차트 생성기 - Plotly 기반
candle_data와 technical_indicators 데이터를 활용한 차트 생성
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import base64
import io
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5435,
            'database': 'mydb',
            'user': 'myuser',
            'password': 'mypassword'
        }
    
    def get_connection(self):
        """데이터베이스 연결"""
        return psycopg2.connect(**self.db_config)
    
    def generate_price_chart(self, symbol: str = "BTC", days: int = 30) -> str:
        """가격 차트 생성 후 base64 이미지 반환"""
        try:
            logger.info(f"📊 {symbol} 가격 차트 생성 시작 ({days}일)")
            
            # 캔들 데이터 조회
            candle_data = self._get_candle_data(symbol, days)
            if not candle_data:
                return "차트 데이터가 없습니다."
            
            # 기술적 지표 데이터 조회
            tech_data = self._get_technical_indicators(symbol, days)
            
            # 차트 생성
            fig = self._create_candlestick_chart(candle_data, tech_data, symbol)
            
            # 이미지로 변환
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            logger.info(f"✅ {symbol} 차트 생성 완료")
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"❌ 차트 생성 실패: {e}")
            return f"차트 생성 중 오류 발생: {str(e)}"
    
    def _get_candle_data(self, symbol: str, days: int) -> pd.DataFrame:
        """캔들 데이터 조회"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    since_date = datetime.now() - timedelta(days=days)
                    
                    query = """
                        SELECT timestamp, open_price, high_price, low_price, close_price, volume
                        FROM candle_data 
                        WHERE symbol = %s AND timestamp >= %s
                        ORDER BY timestamp ASC
                        LIMIT 1000
                    """
                    
                    cur.execute(query, (symbol, since_date))
                    rows = cur.fetchall()
                    
                    if rows:
                        df = pd.DataFrame(rows)
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        return df
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"캔들 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def _get_technical_indicators(self, symbol: str, days: int) -> pd.DataFrame:
        """기술적 지표 데이터 조회"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    since_date = datetime.now() - timedelta(days=days)
                    
                    query = """
                        SELECT timestamp, rsi, macd, signal_line, sma_20, sma_50, bollinger_upper, bollinger_lower
                        FROM technical_indicators 
                        WHERE symbol = %s AND timestamp >= %s
                        ORDER BY timestamp ASC
                        LIMIT 1000
                    """
                    
                    cur.execute(query, (symbol, since_date))
                    rows = cur.fetchall()
                    
                    if rows:
                        df = pd.DataFrame(rows)
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        return df
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"기술적 지표 조회 실패: {e}")
            return pd.DataFrame()
    
    def _create_candlestick_chart(self, candle_df: pd.DataFrame, tech_df: pd.DataFrame, symbol: str) -> go.Figure:
        """캔들스틱 차트 생성"""
        # 서브플롯 생성 (가격 차트 + RSI)
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'{symbol} 가격 차트', 'RSI'),
            row_width=[0.7, 0.3]
        )
        
        # 캔들스틱 차트
        if not candle_df.empty:
            fig.add_trace(
                go.Candlestick(
                    x=candle_df['timestamp'],
                    open=candle_df['open_price'],
                    high=candle_df['high_price'],
                    low=candle_df['low_price'],
                    close=candle_df['close_price'],
                    name=f'{symbol} 가격'
                ),
                row=1, col=1
            )
        
        # 기술적 지표 추가
        if not tech_df.empty:
            # 이동평균선
            if 'sma_20' in tech_df.columns and tech_df['sma_20'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=tech_df['timestamp'],
                        y=tech_df['sma_20'],
                        mode='lines',
                        name='20일 이평선',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'sma_50' in tech_df.columns and tech_df['sma_50'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=tech_df['timestamp'],
                        y=tech_df['sma_50'],
                        mode='lines',
                        name='50일 이평선',
                        line=dict(color='purple', width=1)
                    ),
                    row=1, col=1
                )
            
            # 볼린저 밴드
            if 'bollinger_upper' in tech_df.columns and tech_df['bollinger_upper'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=tech_df['timestamp'],
                        y=tech_df['bollinger_upper'],
                        mode='lines',
                        name='볼린저 상단',
                        line=dict(color='red', width=1, dash='dash')
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=tech_df['timestamp'],
                        y=tech_df['bollinger_lower'],
                        mode='lines',
                        name='볼린저 하단',
                        line=dict(color='blue', width=1, dash='dash')
                    ),
                    row=1, col=1
                )
            
            # RSI
            if 'rsi' in tech_df.columns and tech_df['rsi'].notna().any():
                fig.add_trace(
                    go.Scatter(
                        x=tech_df['timestamp'],
                        y=tech_df['rsi'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='green', width=2)
                    ),
                    row=2, col=1
                )
                
                # RSI 과매수/과매도 선
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="blue", opacity=0.5, row=2, col=1)
        
        # 차트 레이아웃 설정
        fig.update_layout(
            title=f'{symbol} 기술적 분석 차트',
            yaxis_title='가격 (USD)',
            xaxis_title='날짜',
            template='plotly_white',
            showlegend=True,
            height=800,
            width=1200
        )
        
        # RSI 차트 Y축 범위 설정
        fig.update_yaxes(range=[0, 100], row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        
        return fig
    
    def generate_simple_price_chart(self, symbol: str = "BTC", days: int = 7) -> str:
        """간단한 가격 차트 (빠른 생성용)"""
        try:
            logger.info(f"📈 {symbol} 간단 차트 생성 ({days}일)")
            
            candle_data = self._get_candle_data(symbol, days)
            if candle_data.empty:
                return "차트 데이터가 없습니다."
            
            # 간단한 라인 차트
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=candle_data['timestamp'],
                    y=candle_data['close_price'],
                    mode='lines+markers',
                    name=f'{symbol} 가격',
                    line=dict(color='blue', width=3)
                )
            )
            
            fig.update_layout(
                title=f'{symbol} 가격 차트 (최근 {days}일)',
                xaxis_title='날짜',
                yaxis_title='가격 (USD)',
                template='plotly_white',
                height=500,
                width=800
            )
            
            # 이미지로 변환
            img_bytes = fig.to_image(format="png", width=800, height=500)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            logger.info(f"✅ {symbol} 간단 차트 완료")
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"❌ 간단 차트 생성 실패: {e}")
            return f"차트 생성 실패: {str(e)}"