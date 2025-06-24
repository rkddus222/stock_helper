import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scroll_down(driver, pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != last_height

def scrape_naver_stock_news_filtered(stock_code: str, keyword: str, max_count: int = 20) -> list[dict]:
    """
    Selenium을 사용해 네이버 모바일 주식 뉴스 페이지에서 뉴스 기사 중 keyword가 제목 또는 내용에 포함된 것만 최대 max_count개까지 수집 (무한 스크롤 지원)
    """
    url = f"https://m.stock.naver.com/domestic/stock/{stock_code}/news"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    all_articles = []
    seen = set()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.NewsList_inner__kSzOg'))
        )
        while len(all_articles) < max_count:
            news_items = driver.find_elements(By.CSS_SELECTOR, 'div.NewsList_inner__kSzOg')
            for item in news_items:
                try:
                    title = item.find_element(By.CSS_SELECTOR, 'p.NewsList_title__JKIWC').text.strip()
                    content = ""
                    try:
                        content_elem = item.find_element(By.CSS_SELECTOR, 'p.NewsList_text__iXNbt')
                        content = content_elem.text.strip()
                        if not content:
                            content = content_elem.get_attribute('innerText').strip()
                        if not content:
                            content = content_elem.get_attribute('textContent').strip()
                    except:
                        pass
                    # 중복 방지
                    unique_key = title + content
                    if unique_key in seen:
                        continue
                    seen.add(unique_key)
                    if keyword in title or keyword in content:
                        all_articles.append({'title': title, 'content': content})
                        if len(all_articles) >= max_count:
                            break
                except Exception as e:
                    continue
            if len(all_articles) >= max_count:
                break
            # 스크롤 다운
            changed = scroll_down(driver)
            if not changed:
                break
    finally:
        driver.quit()
    return all_articles

if __name__ == "__main__":
    # 주식 코드 예시 (삼성전자: 005930)
    stock_code = "005930"  # 삼성전자
    
    # 주식 뉴스 기사 수집
    print("=== 뉴스 수집 테스트 ===")
    news_titles = scrape_naver_stock_news_filtered(stock_code=stock_code, keyword="삼성")
    
    if news_titles:
        print(f"\n--- {stock_code} 주식 관련 수집된 기사 ---")
        for i, article in enumerate(news_titles, 1):
            print(f"{i}. 제목: {article['title']}")
            print(f"   내용: {article['content']}\n")
    else:
        print("수집된 기사가 없습니다.")