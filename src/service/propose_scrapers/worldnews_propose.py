from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import List, Dict, Optional
import time

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_MANAGER = True
except ImportError:
    USE_MANAGER = False

class WorldnewsProposeScraper:
    def __init__(self):
        self.base_url = "https://stockanalysis.com"
        self.target_url = "https://stockanalysis.com/news/all-stocks/"
        self.max_articles = 20
    
    def scrape_recommended_stocks(self) -> List[Dict]:
        """
        StockAnalysis.com 뉴스 페이지에서 기사 정보를 스크래핑합니다.
        
        Returns:
            List[Dict]: 뉴스 기사 리스트
        """
        print("🔍 StockAnalysis.com 뉴스 스크래핑 시작...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        
        if USE_MANAGER:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        articles_data = []
        
        try:
            driver.get(self.target_url)
            time.sleep(5)  # 페이지 로딩 및 동적 콘텐츠 대기
            
            # 각 뉴스 기사를 감싸는 div 요소 찾기
            articles = driver.find_elements(By.CSS_SELECTOR, 'div.gap-4.border-gray-300.bg-default.p-4.shadow.sm\\:grid.sm\\:grid-cols-news')
            
            for article in articles[:self.max_articles]:
                try:
                    # 제목과 링크
                    title_elem = article.find_element(By.CSS_SELECTOR, 'h3.text-xl.font-bold a')
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute('href')
                    
                    # 날짜
                    date_elem = article.find_element(By.CSS_SELECTOR, 'div.mt-1.text-sm.text-faded')
                    date = date_elem.get_attribute('title').strip() if date_elem.get_attribute('title') else date_elem.text.strip()
                    
                    # 요약
                    summary_elem = article.find_element(By.CSS_SELECTOR, 'p.overflow-auto.text-\\[0\\.95rem\\].text-light')
                    summary = summary_elem.text.strip()
                    
                    articles_data.append({
                        'title': title,
                        'link': link,
                        'date': date,
                        'summary': summary
                    })
                except Exception as e:
                    print(f"❌ 개별 기사 파싱 중 오류: {e}")
                    continue
            
            print(f"✅ {len(articles_data)}개의 뉴스 기사를 스크래핑했습니다.")
            return articles_data
            
        except Exception as e:
            print(f"❌ 뉴스 스크래핑 중 오류 발생: {str(e)}")
            return []
        finally:
            driver.quit()
    
    def format_recommendations(self, articles: List[Dict]) -> str:
        """
        뉴스 기사 리스트를 포맷된 문자열로 변환합니다.
        
        Args:
            articles: 뉴스 기사 리스트
            
        Returns:
            str: 포맷된 뉴스 문자열
        """
        if not articles:
            return "StockAnalysis.com 뉴스가 없습니다."
        
        formatted_text = "📰 StockAnalysis.com 최신 뉴스\n"
        formatted_text += "=" * 50 + "\n\n"
        
        for i, article in enumerate(articles, 1):
            formatted_text += f"{i}. {article['title']}\n"
            formatted_text += f"   날짜: {article['date']}\n"
            formatted_text += f"   링크: {article['link']}\n"
            
            if article.get('summary'):
                summary_text = article['summary']
                if len(summary_text) > 200:
                    summary_text = summary_text[:200] + "..."
                formatted_text += f"   요약: {summary_text}\n"
            
            formatted_text += "\n"
        
        return formatted_text

# 전역 스크래퍼 인스턴스
worldnews_scraper = WorldnewsProposeScraper()