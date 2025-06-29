from typing import List, Dict, Optional

# 셀레니움 관련 import 추가
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_MANAGER = True
except ImportError:
    USE_MANAGER = False

class ThinkpoolProposeScraper:
    def __init__(self):
        self.base_url = "https://m.thinkpool.com"
        self.target_url = "https://m.thinkpool.com/advisor/todays"
        # headers는 셀레니움에서는 사용하지 않음

    def scrape_recommended_stocks(self) -> List[Dict]:
        """
        셀레니움으로 씽크풀 AI 종목 추천을 스크래핑합니다.
        Returns:
            List[Dict]: 추천 종목 리스트
        """
        print("🔍 셀레니움으로 씽크풀 AI 종목 추천 스크래핑 시작...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--lang=ko_KR')
        
        if USE_MANAGER:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        stocks = []
        try:
            driver.get(self.target_url)
            time.sleep(3)  # JS 렌더링 대기
            
            # itemView 클래스만 추출
            divs = driver.find_elements(By.CLASS_NAME, 'itemView')
            for div in divs:
                try:
                    # 종목명, 코드
                    name_div = div.find_element(By.CLASS_NAME, 'name')
                    stock_name = name_div.find_element(By.TAG_NAME, 'strong').text.strip()
                    stock_code = name_div.find_element(By.TAG_NAME, 'span').text.strip()
                    
                    # 빈 데이터 필터링
                    if not stock_name or not stock_code:
                        continue
                        
                    # 기업 정보
                    company_info = div.find_element(By.CLASS_NAME, 'info').text.strip()
                    # 태그
                    tag_div = div.find_element(By.CLASS_NAME, 'tag')
                    tags = [span.text.strip() for span in tag_div.find_elements(By.TAG_NAME, 'span') if span.text.strip()]
                    # 투자포인트
                    con_div = div.find_element(By.CLASS_NAME, 'con')
                    investment_point = con_div.text.replace('[투자포인트]', '').strip()
                    
                    stocks.append({
                        'stock_name': stock_name,
                        'stock_code': stock_code,
                        'company_info': company_info,
                        'tags': tags,
                        'investment_point': investment_point
                    })
                except Exception as e:
                    continue  # 오류 발생 시 해당 항목만 스킵
            print(f"✅ {len(stocks)}개의 씽크풀 AI 추천 종목을 스크래핑했습니다.")
            return stocks
        except Exception as e:
            print(f"❌ 셀레니움 스크래핑 오류: {str(e)}")
            return []
        finally:
            driver.quit()
    
    def format_recommendations(self, stocks: List[Dict]) -> str:
        """
        추천 종목 리스트를 포맷된 문자열로 변환합니다.
        
        Args:
            stocks: 추천 종목 리스트
            
        Returns:
            str: 포맷된 추천 종목 문자열
        """
        if not stocks:
            return "씽크풀 AI 추천 종목이 없습니다."
        
        formatted_text = "🤖 씽크풀 AI 종목 추천\n"
        formatted_text += "=" * 50 + "\n\n"
        
        for i, stock in enumerate(stocks, 1):
            formatted_text += f"{i}. {stock['stock_name']} ({stock['stock_code']})\n"
            
            if stock.get('company_info'):
                formatted_text += f"   기업정보: {stock['company_info']}\n"
            
            if stock.get('tags'):
                formatted_text += f"   태그: {', '.join(stock['tags'])}\n"
            
            if stock.get('investment_point'):
                # 투자 포인트가 길면 줄여서 표시
                investment_text = stock['investment_point']
                if len(investment_text) > 200:
                    investment_text = investment_text[:200] + "..."
                formatted_text += f"   투자포인트: {investment_text}\n"
            
            formatted_text += "\n"
        
        return formatted_text

# 전역 스크래퍼 인스턴스
thinkpool_scraper = ThinkpoolProposeScraper()