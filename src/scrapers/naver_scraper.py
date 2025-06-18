import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from datetime import datetime

def scrape_naver_finance_news_titles(max_pages: int = 2) -> list[dict]:
    """
    네이버 금융 뉴스 메인 페이지에서 지정된 페이지 수만큼 기사 제목을 수집합니다.

    Args:
        max_pages (int): 수집할 최대 페이지 수.

    Returns:
        list[dict]: 각 기사의 제목과 URL을 포함하는 딕셔너리 리스트.
                    예: [{'title': '기사 제목', 'url': '기사 URL'}]
    """
    base_url = "https://finance.naver.com/news/mainnews.naver"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_articles = []
    
    print(f"네이버 금융 뉴스 기사 제목 수집 시작 (최대 {max_pages} 페이지)")

    for page_num in range(1, max_pages + 1):
        # 첫 페이지는 page 파라미터 없이
        if page_num == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page_num}"
            
        print(f"  페이지 {page_num} 수집 중: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 여러 가능한 선택자 시도
            selectors = [
                'div.mainNewsList li',
                'div.mainNewsList a',
                'ul.mainNewsList li',
                'ul.mainNewsList a',
                'div.newsList li',
                'div.newsList a',
                'table.newsList tr td a',
                'div.news_area li',
                'div.news_area a'
            ]
            
            news_items = []
            used_selector = None
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    news_items = items
                    used_selector = selector
                    print(f"    선택자 '{selector}'로 {len(items)}개 항목 발견")
                    break
            
            if not news_items:
                print(f"  페이지 {page_num}에서 뉴스를 찾을 수 없습니다.")
                # HTML 구조 확인을 위해 일부 내용 출력
                print(f"    페이지 제목: {soup.title.string if soup.title else '제목 없음'}")
                print(f"    mainNewsList div 개수: {len(soup.select('div.mainNewsList'))}")
                print(f"    모든 a 태그 개수: {len(soup.select('a'))}")
                break
            
            page_articles = 0
            for item in news_items:
                # articleSubject 클래스를 가진 dd 태그에서 a 태그 찾기
                article_subject = item.select_one('dd.articleSubject a')
                
                if article_subject and article_subject.get_text(strip=True):
                    title = article_subject.get_text(strip=True)
                    
                    # 제목이 너무 짧으면 건너뛰기
                    if len(title) < 5:
                        continue
                    
                    relative_url = article_subject.get('href')
                    if relative_url:
                        # 상대 URL을 절대 URL로 변환
                        full_url = urljoin("https://finance.naver.com/", relative_url)
                        
                        # 기사 제목과 URL 저장
                        all_articles.append({'title': title, 'url': full_url})
                        page_articles += 1
                        print(f"      수집: {title[:50]}...")
            
            print(f"    페이지 {page_num}에서 {page_articles}개 기사 수집")
            
            # 첫 페이지에서 디버깅 정보 출력
            if page_num == 1 and page_articles == 0:
                if news_items:
                    first_item = news_items[0]
                    print(f"    첫 번째 요소 태그: {first_item.name}")
                    print(f"    첫 번째 요소 내용: {first_item.get_text()[:100]}...")
                    a_tags = first_item.select('a')
                    print(f"    첫 번째 요소 내 a 태그 개수: {len(a_tags)}")
                    if a_tags:
                        print(f"    첫 번째 a 태그: {a_tags[0]}")
                        print(f"    첫 번째 a 태그 텍스트: {a_tags[0].get_text()}")
                        print(f"    첫 번째 a 태그 href: {a_tags[0].get('href')}")
                    
                    # articleSubject 확인
                    article_subject = first_item.select_one('dd.articleSubject a')
                    if article_subject:
                        print(f"    articleSubject a 태그: {article_subject}")
                        print(f"    articleSubject 텍스트: {article_subject.get_text()}")
                        print(f"    articleSubject href: {article_subject.get('href')}")
                    else:
                        print("    articleSubject를 찾을 수 없습니다.")
            
            # 다음 페이지로 넘어갈 때 서버에 부담을 주지 않기 위해 잠시 대기
            time.sleep(1) 

        except requests.exceptions.RequestException as e:
            print(f"  페이지 {page_num} 요청 중 오류 발생: {e}")
            break
        except Exception as e:
            print(f"  페이지 {page_num} 처리 중 예상치 못한 오류 발생: {e}")
            break

    print(f"총 {len(all_articles)}개의 기사 제목 수집 완료.")
    return all_articles

if __name__ == "__main__":
    # 5페이지까지의 기사 제목 수집
    news_titles = scrape_naver_finance_news_titles(max_pages=5)
    
    if news_titles:
        print("\n--- 수집된 기사 제목 ---")
        for i, article in enumerate(news_titles, 1):
            print(f"{i}. {article['title']}")
            # print(f"   URL: {article['url']}") # URL도 함께 보고 싶다면 주석 해제
    else:
        print("수집된 기사가 없습니다.")