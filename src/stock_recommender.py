"""
주식 종목 추천 모듈

퍼플렉시티 LLM API를 사용하여 주식 종목을 추천합니다.
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


class StockRecommender:
    """주식 종목 추천 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        StockRecommender 초기화
        
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
    
    def get_market_data(self) -> Dict:
        """
        시장 전반적인 데이터 수집
        
        Returns:
            시장 데이터 딕셔너리
        """
        # 주요 지수들
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
            '^VIX': 'VIX (변동성 지수)'
        }
        
        market_data = {}
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - prev_close
                    change_percent = (change / prev_close) * 100
                    
                    market_data[symbol] = {
                        'name': name,
                        'current': current,
                        'change': change,
                        'change_percent': change_percent
                    }
                    
            except Exception as e:
                logger.error(f"{symbol} 시장 데이터 수집 실패: {e}")
        
        return market_data
    
    def get_sector_performance(self) -> Dict:
        """
        섹터별 성과 데이터 수집
        
        Returns:
            섹터 성과 데이터
        """
        # 주요 섹터 ETF들
        sector_etfs = {
            'XLK': 'Technology',
            'XLF': 'Financial',
            'XLE': 'Energy',
            'XLV': 'Healthcare',
            'XLI': 'Industrial',
            'XLP': 'Consumer Staples',
            'XLY': 'Consumer Discretionary',
            'XLU': 'Utilities',
            'XLB': 'Materials',
            'XLRE': 'Real Estate'
        }
        
        sector_data = {}
        
        for symbol, sector in sector_etfs.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    month_ago = hist['Close'].iloc[0]
                    change_percent = ((current - month_ago) / month_ago) * 100
                    
                    sector_data[sector] = {
                        'symbol': symbol,
                        'change_percent': change_percent,
                        'current_price': current
                    }
                    
            except Exception as e:
                logger.error(f"{sector} 섹터 데이터 수집 실패: {e}")
        
        return sector_data
    
    def create_recommendation_prompt(self, market_data: Dict, sector_data: Dict, 
                                   user_preferences: Optional[str] = None) -> str:
        """
        추천을 위한 프롬프트 생성
        
        Args:
            market_data: 시장 데이터
            sector_data: 섹터 성과 데이터
            user_preferences: 사용자 선호사항
            
        Returns:
            프롬프트 문자열
        """
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        prompt = f"""
오늘({today})의 시장 상황을 분석하여 주식 종목을 추천해주세요.

=== 현재 시장 상황 ===
"""
        
        # 시장 지수 정보
        for symbol, data in market_data.items():
            prompt += f"""
{data['name']}: {data['current']:.2f} ({data['change']:+.2f}, {data['change_percent']:+.2f}%)
"""
        
        prompt += "\n=== 섹터별 성과 (최근 1개월) ===\n"
        
        # 섹터 성과 정보
        for sector, data in sector_data.items():
            prompt += f"""
{sector}: {data['change_percent']:+.2f}% (현재가: ${data['current_price']:.2f})
"""
        
        if user_preferences:
            prompt += f"\n=== 사용자 선호사항 ===\n{user_preferences}\n"
        
        prompt += """
위 정보를 바탕으로 다음을 분석하고 추천해주세요:

1. **현재 시장 동향 분석**
   - 전반적인 시장 분위기
   - 주요 지수들의 움직임

2. **섹터별 분석**
   - 강세/약세 섹터
   - 각 섹터의 전망

3. **주식 종목 추천 (5-10개)**
   - 추천 이유
   - 예상 수익률
   - 위험 요소
   - 투자 전략

4. **투자 조언**
   - 포트폴리오 구성 방향
   - 주의사항

한국어로 상세하고 실용적으로 작성해주세요. 각 추천 종목에 대해 구체적인 이유와 전망을 포함해주세요.
"""
        
        return prompt
    
    def get_stock_recommendations(self, user_preferences: Optional[str] = None) -> str:
        """
        주식 종목 추천 생성
        
        Args:
            user_preferences: 사용자 선호사항 (예: "안정적인 배당주", "성장주", "테크주" 등)
            
        Returns:
            추천 텍스트
        """
        logger.info("주식 종목 추천 시작")
        
        try:
            # 시장 데이터 수집
            market_data = self.get_market_data()
            logger.info("시장 데이터 수집 완료")
            
            # 섹터 성과 데이터 수집
            sector_data = self.get_sector_performance()
            logger.info("섹터 데이터 수집 완료")
            
            # 프롬프트 생성
            prompt = self.create_recommendation_prompt(market_data, sector_data, user_preferences)
            
            # Perplexity API로 추천 생성
            recommendation = self.get_recommendation_from_perplexity(prompt)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"주식 추천 생성 중 오류: {e}")
            return f"주식 추천 생성 중 오류가 발생했습니다: {e}"
    
    def get_recommendation_from_perplexity(self, prompt: str) -> str:
        """
        Perplexity API를 사용하여 추천 생성
        
        Args:
            prompt: 추천 요청 프롬프트
            
        Returns:
            추천 텍스트
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
                "max_tokens": 1500,
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
            return f"추천 생성 중 오류가 발생했습니다: {e}"


def main():
    """테스트용 메인 함수"""
    try:
        recommender = StockRecommender()
        
        print("=== 주식 종목 추천 시스템 ===")
        print("1. 일반 추천")
        print("2. 안정적인 배당주 추천")
        print("3. 성장주 추천")
        print("4. 테크주 추천")
        
        choice = input("\n원하는 추천 유형을 선택하세요 (1-4): ").strip()
        
        preferences = {
            "1": None,
            "2": "안정적인 배당주를 중심으로 추천해주세요. 배당 수익률이 높고 안정적인 기업들을 선호합니다.",
            "3": "고성장 기업들을 중심으로 추천해주세요. 매출과 이익이 빠르게 성장하는 기업들을 선호합니다.",
            "4": "기술주를 중심으로 추천해주세요. AI, 반도체, 소프트웨어 등 기술 관련 기업들을 선호합니다."
        }
        
        if choice in preferences:
            print("\n주식 종목을 분석하고 추천을 생성 중입니다...")
            recommendation = recommender.get_stock_recommendations(preferences[choice])
            print("\n" + "="*60)
            print("주식 종목 추천")
            print("="*60)
            print(recommendation)
            print("="*60)
        else:
            print("잘못된 선택입니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main() 