"""
주식 정보 요약 모듈

퍼플렉시티 LLM API를 사용하여 오늘의 주식 정보를 요약합니다.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import yfinance as yf
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)


class StockSummarizer:
    """주식 정보 요약 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        StockSummarizer 초기화
        
        Args:
            api_key: Perplexity API 키 (None인 경우 환경 변수에서 로드)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("Perplexity API 키가 필요합니다. .env 파일에 PERPLEXITY_API_KEY를 설정하세요.")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_stock_data(self, symbols: List[str]) -> Dict:
        """
        주식 데이터 수집
        
        Args:
            symbols: 주식 심볼 리스트
            
        Returns:
            주식 데이터 딕셔너리
        """
        stock_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 오늘의 주가 정보
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    change = hist['Close'].iloc[-1] - hist['Open'].iloc[0]
                    change_percent = (change / hist['Open'].iloc[0]) * 100
                else:
                    current_price = info.get('currentPrice', 0)
                    change = 0
                    change_percent = 0
                
                stock_data[symbol] = {
                    'name': info.get('longName', symbol),
                    'current_price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': info.get('volume', 0),
                    'market_cap': info.get('marketCap', 0),
                    'sector': info.get('sector', 'Unknown')
                }
                
                logger.info(f"{symbol} 데이터 수집 완료")
                
            except Exception as e:
                logger.error(f"{symbol} 데이터 수집 실패: {e}")
                stock_data[symbol] = None
        
        return stock_data
    
    def create_summary_prompt(self, stock_data: Dict) -> str:
        """
        요약을 위한 프롬프트 생성
        
        Args:
            stock_data: 주식 데이터
            
        Returns:
            프롬프트 문자열
        """
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        prompt = f"""
오늘({today})의 주요 주식 정보를 분석하고 요약해주세요.

다음은 주요 주식들의 현재 정보입니다:

"""
        
        for symbol, data in stock_data.items():
            if data:
                prompt += f"""
{symbol} ({data['name']}):
- 현재가: ${data['current_price']:.2f}
- 변동: ${data['change']:.2f} ({data['change_percent']:.2f}%)
- 거래량: {data['volume']:,}
- 섹터: {data['sector']}

"""
        
        prompt += """
위 정보를 바탕으로 다음을 요약해주세요:
1. 오늘의 전반적인 시장 동향
2. 주요 주식들의 성과 분석
3. 주목할 만한 변동 사항
4. 투자자들에게 도움이 될 수 있는 인사이트

한국어로 간결하고 이해하기 쉽게 작성해주세요.
"""
        
        return prompt
    
    def get_summary_from_perplexity(self, prompt: str) -> str:
        """
        Perplexity API를 사용하여 요약 생성
        
        Args:
            prompt: 요약 요청 프롬프트
            
        Returns:
            요약 텍스트
        """
        try:
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API 요청 실패: {response.status_code} - {response.text}")
                return "API 요청 중 오류가 발생했습니다."
                
        except Exception as e:
            logger.error(f"Perplexity API 호출 중 오류: {e}")
            return f"요약 생성 중 오류가 발생했습니다: {e}"
    
    def get_daily_stock_summary(self, symbols: Optional[List[str]] = None) -> str:
        """
        오늘의 주식 정보 요약 생성
        
        Args:
            symbols: 분석할 주식 심볼 리스트 (None인 경우 기본값 사용)
            
        Returns:
            요약 텍스트
        """
        if symbols is None:
            default_symbols = os.getenv('DEFAULT_STOCK_SYMBOLS', 'AAPL,MSFT,GOOGL,TSLA,AMZN')
            symbols = [s.strip() for s in default_symbols.split(',')]
        
        logger.info(f"주식 정보 요약 시작: {symbols}")
        
        # 주식 데이터 수집
        stock_data = self.get_stock_data(symbols)
        
        # 프롬프트 생성
        prompt = self.create_summary_prompt(stock_data)
        
        # Perplexity API로 요약 생성
        summary = self.get_summary_from_perplexity(prompt)
        
        return summary


def main():
    """테스트용 메인 함수"""
    try:
        summarizer = StockSummarizer()
        summary = summarizer.get_daily_stock_summary()
        print("=== 오늘의 주식 정보 요약 ===")
        print(summary)
        
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main() 