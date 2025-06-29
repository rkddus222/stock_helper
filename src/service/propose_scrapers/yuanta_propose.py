import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional

class YuantaProposeScraper:
    def __init__(self):
        self.base_url = "https://m.myasset.com/myasset/research/rs_list/RS_0702001_P1.cmd"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_recommended_stocks(self) -> List[Dict]:
        """
        유안타증권 추천 종목을 스크래핑합니다.
        
        Returns:
            List[Dict]: 추천 종목 리스트
        """
        try:
            # URL 파라미터 설정
            params = {
                'section': '01',
                'timestamp': '1750775382430'
            }
            
            print("🔍 유안타증권 추천 종목 스크래핑 시작...")
            
            # 웹페이지 요청
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 추천 종목 추출
            recommended_stocks = []
            
            # dl 태그들 찾기 (추천 종목 컨테이너)
            stock_containers = soup.find_all('dl')
            
            for container in stock_containers:
                stock_info = self._extract_stock_info(container)
                if stock_info:
                    recommended_stocks.append(stock_info)
            
            print(f"✅ {len(recommended_stocks)}개의 추천 종목을 스크래핑했습니다.")
            return recommended_stocks
            
        except requests.RequestException as e:
            print(f"❌ 웹페이지 요청 실패: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ 스크래핑 중 오류 발생: {str(e)}")
            return []
    
    def _extract_stock_info(self, container) -> Optional[Dict]:
        """
        개별 종목 정보를 추출합니다.
        
        Args:
            container: BeautifulSoup dl 태그 객체
            
        Returns:
            Dict: 종목 정보 딕셔너리
        """
        try:
            # 종목명과 종목코드 추출
            title_element = container.find('strong', class_='js-data js-title')
            if not title_element:
                return None
            
            title_text = title_element.get_text(strip=True)
            
            # 종목코드 추출 (data-jongcode 속성에서)
            stock_code = title_element.get('data-jongcode', '')
            
            # 종목명에서 코드 제거 (예: "BNK금융지주(138930)" -> "BNK금융지주")
            stock_name = re.sub(r'\([0-9]+\)', '', title_text).strip()
            
            # 가격 정보 추출
            price_info = {}
            item_wrap = container.find('div', class_='itemWrap')
            if item_wrap:
                ul = item_wrap.find('ul')
                if ul:
                    for li in ul.find_all('li'):
                        text = li.get_text(strip=True)
                        if '편입가' in text:
                            price_info['entry_price'] = text.replace('편입가 : ', '')
                        elif '현재가' in text:
                            price_info['current_price'] = text.replace('현재가 : ', '')
                        elif '수익률' in text:
                            # 수익률에서 + 기호와 % 제거하여 숫자만 추출
                            profit_rate = re.search(r'([+-]?\d+\.?\d*)%', text)
                            if profit_rate:
                                price_info['profit_rate'] = profit_rate.group(1) + '%'
            
            # 추천자 정보 추출
            recommender = ""
            dd_content = container.find('dd', class_='jsAccDetail')
            if dd_content:
                content_text = dd_content.get_text(strip=True)
                # 추천자 정보 추출 (첫 번째 줄에서)
                lines = content_text.split('\n')
                for line in lines:
                    if '추천자' in line:
                        recommender = line.replace('추천자 : ', '').strip()
                        break
            
            # 추천 이유 추출 (dd 태그의 전체 내용)
            recommendation_reason = ""
            if dd_content:
                recommendation_reason = dd_content.get_text(strip=True)
                # 추천자 정보 제거
                if '추천자 : ' in recommendation_reason:
                    recommendation_reason = recommendation_reason.split('추천자 : ')[1]
                    if '\n' in recommendation_reason:
                        recommendation_reason = recommendation_reason.split('\n', 1)[1]
            
            return {
                'stock_name': stock_name,
                'stock_code': stock_code,
                'entry_price': price_info.get('entry_price', ''),
                'current_price': price_info.get('current_price', ''),
                'profit_rate': price_info.get('profit_rate', ''),
                'recommender': recommender,
                'recommendation_reason': recommendation_reason
            }
            
        except Exception as e:
            print(f"❌ 종목 정보 추출 중 오류: {str(e)}")
            return None
    
    def format_recommendations(self, stocks: List[Dict]) -> str:
        """
        추천 종목 리스트를 포맷된 문자열로 변환합니다.
        
        Args:
            stocks: 추천 종목 리스트
            
        Returns:
            str: 포맷된 추천 종목 문자열
        """
        if not stocks:
            return "추천 종목이 없습니다."
        
        formatted_text = "📈 유안타증권 추천 종목\n"
        formatted_text += "=" * 50 + "\n\n"
        
        for i, stock in enumerate(stocks, 1):
            formatted_text += f"{i}. {stock['stock_name']} ({stock['stock_code']})\n"
            formatted_text += f"   편입가: {stock['entry_price']}\n"
            formatted_text += f"   현재가: {stock['current_price']}\n"
            formatted_text += f"   수익률: {stock['profit_rate']}\n"
            formatted_text += f"   추천자: {stock['recommender']}\n"
            formatted_text += f"   추천이유: {stock['recommendation_reason'][:100]}{'...' if len(stock['recommendation_reason']) > 100 else ''}\n"
            formatted_text += "\n"
        
        return formatted_text

# 전역 스크래퍼 인스턴스
yuanta_scraper = YuantaProposeScraper()

if __name__ == "__main__":
    scraper = YuantaProposeScraper()
    print(scraper.scrape_recommended_stocks())