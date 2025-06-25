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

def scrape_stock_news(
    stock_info: dict,
    keyword: str = "",
    max_count_per_stock: int = 10
) -> dict:
    """
    주식 리스트의 각 종목에 대해 뉴스를 수집

    Args:
        stock_info (dict): _load_stock_list() 함수로부터 로드된 주식 정보 딕셔너리
        keyword (str): 검색할 키워드 (기본값: 빈 문자열 - 모든 뉴스 수집)
        max_count_per_stock (int): 종목당 최대 수집할 뉴스 개수

    Returns:
        dict: {종목코드(종목명): 뉴스리스트} 형태의 결과
    """
    if not stock_info:
        print("주식 리스트가 비어있습니다.")
        return {}

    results = {}

    print(f"\n=== 주식 뉴스 수집 시작 ===")
    print(f"수집 대상: {len(stock_info)}개 종목")
    print(f"키워드: '{keyword}' (비어있으면 모든 뉴스)")
    print(f"종목당 최대 수집 개수: {max_count_per_stock}개")
    print("=" * 50)


    for i, (stock_code, stock_name) in enumerate(stock_info.items(), 1):
        print(f"\n[{i}/{len(stock_info)}] {stock_code}({stock_name}) 뉴스 수집 중...")

        try:
            # 네이버 주식 뉴스 수집
            news_list = scrape_naver_stock_news_filtered(
                stock_code=stock_code,
                keyword=keyword,
                max_count=max_count_per_stock
            )

            # 종목코드(종목명) 형태로 키 생성 - UTF-8 인코딩 보장
            key = f"{stock_code}({stock_name})"
            # 디버깅을 위한 출력
            print(f"생성된 키: {repr(key)}")
            results[key] = news_list
            print(f"  ✓ {len(news_list)}개 뉴스 수집 완료")

            # 수집된 뉴스 미리보기
            if news_list:
                print(f"  최근 뉴스 제목: {news_list[0]['title'][:50]}...")

        except Exception as e:
            print(f"  ✗ {stock_code}({stock_name}) 뉴스 수집 실패: {str(e)}")
            key = f"{stock_code}({stock_name})"
            results[key] = []

    return results