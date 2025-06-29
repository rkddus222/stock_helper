from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import os

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_MANAGER = True
except ImportError:
    USE_MANAGER = False

class SamsungProposeScraper:
    def __init__(self):
        self.base_url = "https://www.samsungpop.com"
        self.target_url = "https://www.samsungpop.com/?MENU_CODE=M1444009177194"
    
    def scrape_recommended_stocks(self) -> List[Dict]:
        """
        삼성증권 SAMSUNGPOP 해외주식추천종목을 스크래핑합니다.
        
        Returns:
            List[Dict]: 추천 종목 리스트
        """
        print("🔍 삼성증권 해외주식 추천 종목 스크래핑 시작...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--log-level=3')
        
        if USE_MANAGER:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        stock_data = []
        
        try:
            print(f"메인 웹 페이지 로드 중: {self.target_url}")
            driver.get(self.target_url)
            
            # 메인 페이지 로딩 대기 (프레임셋이 로드될 때까지)
            time.sleep(3)
            
            # 'frmContent' frame으로 전환
            print("iframe/frame 'frmContent'로 전환 시도 중...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, 'frmContent'))
                )
                print("성공적으로 'frmContent' frame으로 전환되었습니다.")
            except Exception as e:
                print(f"❌ 'frmContent' frame 전환 실패: {e}")
                return []
            
            # frame 내부의 HTML 소스 가져오기
            frame_page_source = driver.page_source
            
            soup = BeautifulSoup(frame_page_source, 'html.parser')
            
            # 'table.guideTb1' 내부의 'tbody' 태그를 찾음
            table = soup.find('table', class_='guideTb1')
            if not table:
                print("❌ 'table.guideTb1' 태그를 찾을 수 없습니다.")
                return []
            
            tbody = table.find('tbody')
            if not tbody:
                print("❌ 'tbody' 태그를 찾을 수 없습니다.")
                return []
            
            # 'tbody' 내부에서 'onclick' 속성을 가진 모든 <tr> 태그를 찾음
            rows = tbody.find_all('tr', onclick=True)
            print(f"발견된 유효한 'tr' 태그 개수: {len(rows)}")
            
            if not rows:
                print("❌ 'onclick' 속성을 가진 'tr' 태그를 찾을 수 없습니다.")
                return []
            
            # 각 종목은 2개의 tr로 구성되므로 2개씩 건너뛰며 처리
            for i in range(0, len(rows), 2):
                first_row = rows[i]
                
                try:
                    cols_first = first_row.find_all('td')
                    
                    # 컬럼 개수 유효성 검사
                    if len(cols_first) < 6:
                        continue
                    
                    # 데이터 추출 및 정리
                    category = cols_first[0].text.strip()
                    name = cols_first[1].text.strip()
                    exchange = cols_first[2].text.strip()
                    current_price = cols_first[3].text.strip()
                    change_rate = cols_first[4].text.strip()
                    reason = cols_first[5].text.strip().replace('\n', ' ').replace('<br/>', ' ')
                    
                    stock_data.append({
                        'category': category,
                        'stock_name': name,
                        'exchange': exchange,
                        'current_price': current_price,
                        'change_rate': change_rate,
                        'reason': reason
                    })
                    
                except Exception as e:
                    print(f"❌ 개별 'tr' 처리 중 오류: {e}")
                    continue
            
            print(f"✅ {len(stock_data)}개의 삼성증권 해외주식 추천 종목을 스크래핑했습니다.")
            return stock_data
            
        except Exception as e:
            print(f"❌ 스크래핑 중 오류 발생: {str(e)}")
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
            return "삼성증권 해외주식 추천 종목이 없습니다."
        
        formatted_text = "🏦 삼성증권 해외주식 추천 종목\n"
        formatted_text += "=" * 50 + "\n\n"
        
        for i, stock in enumerate(stocks, 1):
            formatted_text += f"{i}. {stock['stock_name']} ({stock['exchange']})\n"
            formatted_text += f"   구분: {stock['category']}\n"
            formatted_text += f"   현재가: {stock['current_price']}\n"
            formatted_text += f"   등락률: {stock['change_rate']}\n"
            
            if stock.get('reason'):
                reason_text = stock['reason']
                if len(reason_text) > 200:
                    reason_text = reason_text[:200] + "..."
                formatted_text += f"   추천사유: {reason_text}\n"
            
            formatted_text += "\n"
        
        return formatted_text

# 전역 스크래퍼 인스턴스
samsung_scraper = SamsungProposeScraper()

if __name__ == "__main__":
    scraper = SamsungProposeScraper()
    stocks = scraper.scrape_recommended_stocks()
    print("스크래핑 결과:")
    for stock in stocks:
        print(stock)
    print("\n포맷된 결과:")
    print(scraper.format_recommendations(stocks))