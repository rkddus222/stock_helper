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
import os
import sys

def create_driver():
    """
    안정적인 Chrome WebDriver를 생성하는 함수
    """
    options = Options()
    
    # 기본 설정
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # 자동화 감지 방지
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 추가 안정성 설정
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")  # 필요한 경우 제거
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    # User-Agent 설정
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # ChromeDriverManager를 사용하여 드라이버 설치
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 자동화 감지 방지 스크립트 실행
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"Chrome 드라이버 생성 실패: {e}")
        return None

def scroll_down(driver, pause_time=2):
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        return new_height != last_height
    except Exception as e:
        print(f"스크롤 중 오류: {e}")
        return False

def scrape_yahoo_stock_news_filtered(stock_name: str, keyword: str, max_count: int = 20) -> list[dict]:
    """
    Selenium을 사용해 Yahoo Finance 주식 뉴스 페이지에서 뉴스 기사 중 keyword가 제목 또는 내용에 포함된 것만 최대 max_count개까지 수집 (무한 스크롤 지원)
    
    Args:
        stock_name: 주식 심볼 (예: "AAPL", "MSFT", "GOOGL")
        keyword: 검색할 키워드
        max_count: 최대 수집할 뉴스 개수
    
    Returns:
        뉴스 기사 리스트
    """
    url = f"https://finance.yahoo.com/quote/{stock_name}/news/"
    
    driver = create_driver()
    if driver is None:
        print("WebDriver 생성에 실패했습니다.")
        return []
    
    all_articles = []
    seen = set()
    
    try:
        print(f"  페이지 로딩 중: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기 (더 긴 시간)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="news-item"], .news-item, article'))
            )
        except:
            print("  뉴스 아이템을 찾을 수 없습니다. 다른 선택자 시도...")
            # 대체 선택자들 시도
            selectors = ['div[data-test-id="news-item"]', '.news-item', 'article', '.news-list-item', '[data-test-id="news-list"]']
            found = False
            for selector in selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    found = True
                    break
                except:
                    continue
            
            if not found:
                print("  뉴스 컨텐츠를 찾을 수 없습니다.")
                return []
        
        # 쿠키 수락 버튼이 있으면 클릭
        try:
            cookie_selectors = [
                'button[data-test-id="accept-cookies"]',
                'button[data-test-id="cookie-accept"]',
                '.cookie-accept',
                '[data-test-id="cookie-banner"] button'
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_button.click()
                    print("  쿠키 수락 버튼 클릭됨")
                    time.sleep(2)
                    break
                except:
                    continue
        except:
            pass
        
        # 페이지 소스 확인 (디버깅용)
        page_source = driver.page_source
        if "news" not in page_source.lower() and "article" not in page_source.lower():
            print("  뉴스 페이지가 아닌 것 같습니다.")
            return []
        
        while len(all_articles) < max_count:
            # Yahoo Finance 뉴스 페이지의 실제 구조에 맞는 선택자들
            news_selectors = [
                'a[data-ylk*="elm:hdln"]',  # Yahoo Finance 뉴스 링크
                'a.subtle-link.fin-size-small.titles',  # 뉴스 링크 클래스
                'div[data-test-id="news-item"]',
                '.news-item',
                'article',
                '.news-list-item',
                '[data-test-id="news-list"] > div',
                '.news-card',
                '.article-item'
            ]
            
            news_items = []
            for selector in news_selectors:
                try:
                    items = driver.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        news_items = items
                        print(f"  뉴스 아이템 {len(items)}개 발견 (선택자: {selector})")
                        break
                except:
                    continue
            
            if not news_items:
                print("  뉴스 아이템을 찾을 수 없습니다.")
                break
            
            for item in news_items:
                try:
                    # 제목 추출 - Yahoo Finance 구조에 맞게 개선
                    title_selectors = [
                        'h3.clamp',  # Yahoo Finance 제목 클래스
                        'h3.yf-10mgn4g',  # Yahoo Finance 제목 클래스
                        'h3',
                        'h4', 
                        '.news-title', 
                        '[data-test-id="news-title"]', 
                        '.title', 
                        '.headline'
                    ]
                    title = ""
                    for selector in title_selectors:
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, selector)
                            title = title_elem.text.strip()
                            if title:
                                break
                        except:
                            continue
                    
                    if not title:
                        continue
                    
                    # 내용 추출 - Yahoo Finance 구조에 맞게 개선
                    content_selectors = [
                        'p.clamp',  # Yahoo Finance 내용 클래스
                        'p.yf-10mgn4g',  # Yahoo Finance 내용 클래스
                        'p',
                        '.news-summary', 
                        '[data-test-id="news-summary"]', 
                        '.summary', 
                        '.description'
                    ]
                    content = ""
                    for selector in content_selectors:
                        try:
                            content_elem = item.find_element(By.CSS_SELECTOR, selector)
                            content = content_elem.text.strip()
                            if content:
                                break
                        except:
                            continue
                    
                    # 링크 추출
                    link = ""
                    try:
                        # 현재 아이템이 링크인 경우
                        if item.tag_name == 'a':
                            link = item.get_attribute('href')
                        else:
                            # 링크 요소 찾기
                            link_elem = item.find_element(By.CSS_SELECTOR, 'a')
                            link = link_elem.get_attribute('href')
                    except:
                        pass
                    
                    # 중복 방지
                    unique_key = title + content
                    if unique_key in seen:
                        continue
                    seen.add(unique_key)
                    
                    # 키워드 필터링
                    if not keyword or keyword.lower() in title.lower() or keyword.lower() in content.lower():
                        article = {
                            'title': title,
                            'content': content,
                            'link': link,
                            'source': 'Yahoo Finance'
                        }
                        all_articles.append(article)
                        print(f"    뉴스 추가: {title[:50]}...")
                        
                        if len(all_articles) >= max_count:
                            break
                            
                except Exception as e:
                    continue
            
            if len(all_articles) >= max_count:
                break
                
            # 스크롤 다운
            changed = scroll_down(driver)
            if not changed:
                print("  더 이상 스크롤할 내용이 없습니다.")
                break
                
            # 추가 로딩 대기
            time.sleep(3)
            
    except Exception as e:
        print(f"  Yahoo Finance 스크래핑 중 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass
        
    return all_articles

def scrape_stock_worldwide_news(
    stock_info: dict,
    keyword: str = "",
    max_count_per_stock: int = 10
) -> dict:
    """
    주식 리스트의 각 종목에 대해 Yahoo Finance 뉴스를 수집

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

    print(f"\n=== Yahoo Finance 주식 뉴스 수집 시작 ===")
    print(f"수집 대상: {len(stock_info)}개 종목")
    print(f"키워드: '{keyword}' (비어있으면 모든 뉴스)")
    print(f"종목당 최대 수집 개수: {max_count_per_stock}개")
    print("=" * 50)

    for i, (stock_code, stock_name) in enumerate(stock_info.items(), 1):
        print(f"\n[{i}/{len(stock_info)}] {stock_code}({stock_name}) Yahoo Finance 뉴스 수집 중...")

        try:
            news_list = scrape_yahoo_stock_news_filtered(
                stock_name=stock_name,
                keyword=keyword,
                max_count=max_count_per_stock
            )

            # 종목코드(종목명) 형태로 키 생성
            key = f"{stock_code}({stock_name})"
            results[key] = news_list
            print(f"  ✓ {len(news_list)}개 뉴스 수집 완료")

            # 수집된 뉴스 미리보기
            if news_list:
                print(f"  최근 뉴스 제목: {news_list[0]['title'][:50]}...")

        except Exception as e:
            print(f"  ✗ {stock_code}({stock_name}) Yahoo Finance 뉴스 수집 실패: {str(e)}")
            key = f"{stock_code}({stock_name})"
            results[key] = []

    return results

if __name__ == "__main__":
    print("=== Yahoo Finance 뉴스 스크래퍼 테스트 ===\n")
    
    # 테스트용 주식 정보
    test_stock_info = {
        "005930": "NVDA",
        "000660": "TSLA"
    }
    
    # 뉴스 수집 테스트
    results = scrape_stock_news(
        stock_info=test_stock_info,
        keyword="",
        max_count_per_stock=5
    )
    
    print(f"\n=== 수집 결과 ===")
    for key, news_list in results.items():
        print(f"{key}: {len(news_list)}개 뉴스")
        if news_list:
            print(f"  첫 번째 뉴스: {news_list[0]['title']}")
