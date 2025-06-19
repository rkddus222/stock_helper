import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
from typing import List, Dict, Optional
import logging
import re

class InvestingScraper:
    """
    Investing.com에서 주식 시장 뉴스를 스크래핑하는 클래스
    """
    
    def __init__(self):
        self.base_url = "https://www.investing.com"
        self.news_url = "https://www.investing.com/news/stock-market-news"
        
        # 더 강력한 헤더 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.investing.com/',
        }
        
        # 세션 설정
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 쿠키 설정
        self.session.cookies.set('language', 'ko', domain='.investing.com')
        self.session.cookies.set('timezone', 'Asia/Seoul', domain='.investing.com')
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_news_list(self, max_pages: int = 3) -> List[Dict]:
        """
        주식 시장 뉴스 목록을 가져옵니다.
        
        Args:
            max_pages (int): 스크래핑할 최대 페이지 수
            
        Returns:
            List[Dict]: 뉴스 목록
        """
        all_news = []
        
        for page in range(1, max_pages + 1):
            try:
                self.logger.info(f"페이지 {page} 스크래핑 중...")
                
                if page == 1:
                    url = self.news_url
                else:
                    url = f"{self.news_url}/{page}"
                
                # 더 긴 타임아웃과 재시도 로직
                for attempt in range(3):
                    try:
                        response = self.session.get(url, timeout=20)
                        response.raise_for_status()
                        break
                    except requests.exceptions.RequestException as e:
                        if attempt == 2:  # 마지막 시도
                            raise e
                        self.logger.warning(f"페이지 {page} 시도 {attempt + 1} 실패, 재시도 중...")
                        time.sleep(random.uniform(3, 6))
                
                soup = BeautifulSoup(response.content, 'html.parser')
                news_items = self._parse_news_list(soup)
                
                all_news.extend(news_items)
                self.logger.info(f"페이지 {page}에서 {len(news_items)}개의 뉴스를 찾았습니다.")
                
                # 요청 간 딜레이 증가
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                self.logger.error(f"페이지 {page} 스크래핑 중 오류 발생: {str(e)}")
                continue
        
        return all_news
    
    def _parse_news_list(self, soup: BeautifulSoup) -> List[Dict]:
        """
        뉴스 목록 페이지를 파싱합니다.
        
        Args:
            soup (BeautifulSoup): 파싱할 BeautifulSoup 객체
            
        Returns:
            List[Dict]: 파싱된 뉴스 목록
        """
        news_items = []
        
        # Investing.com의 다양한 뉴스 컨테이너 선택자들
        news_selectors = [
            'article.articleItem',
            '.articleItem',
            '.js-article-item',
            '.article-item',
            '.largeTitle',
            '.articleList article',
            '.newsList article',
            '.contentSection article',
            'div[data-test="article-item"]',
            '.articleList .articleItem',
            '.newsList .articleItem',
            '.js-content-wrapper article',
            '.content-wrapper article'
        ]
        
        news_elements = []
        for selector in news_selectors:
            news_elements = soup.select(selector)
            if news_elements:
                self.logger.info(f"선택자 '{selector}'로 {len(news_elements)}개의 뉴스 요소를 찾았습니다.")
                break
        
        # 대안: 뉴스 링크를 직접 찾기
        if not news_elements:
            news_links = soup.find_all('a', href=re.compile(r'/news/.*'))
            self.logger.info(f"뉴스 링크를 통해 {len(news_links)}개의 링크를 찾았습니다.")
            
            # 링크의 부모 요소를 뉴스 아이템으로 사용
            for link in news_links:
                parent = link.find_parent(['article', 'div'])
                if parent and parent not in news_elements:
                    news_elements.append(parent)
        
        # 대안: 특정 클래스가 포함된 div들 찾기
        if not news_elements:
            divs_with_article = soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['article', 'news', 'item']))
            news_elements = divs_with_article
            self.logger.info(f"키워드 기반으로 {len(news_elements)}개의 요소를 찾았습니다.")
        
        for element in news_elements:
            try:
                news_item = self._extract_news_item(element)
                if news_item and news_item.get('title') and news_item.get('link'):
                    news_items.append(news_item)
            except Exception as e:
                self.logger.warning(f"뉴스 아이템 파싱 중 오류: {str(e)}")
                continue
        
        return news_items
    
    def _extract_news_item(self, element) -> Optional[Dict]:
        """
        개별 뉴스 아이템에서 정보를 추출합니다.
        
        Args:
            element: 뉴스 아이템 HTML 요소
            
        Returns:
            Optional[Dict]: 추출된 뉴스 정보
        """
        try:
            # 제목과 링크 추출
            title_element = None
            link = ""
            
            # 다양한 제목 선택자들
            title_selectors = [
                'a[class*="title"]',
                'a[class*="headline"]',
                'h2 a',
                'h3 a',
                'h4 a',
                'a[href*="/news/"]',
                'a'
            ]
            
            for selector in title_selectors:
                title_element = element.select_one(selector)
                if title_element and title_element.get('href'):
                    break
            
            if not title_element:
                return None
            
            title = title_element.get_text(strip=True)
            link = title_element.get('href', '')
            
            if not title or not link:
                return None
            
            # 상대 URL을 절대 URL로 변환
            if link.startswith('/'):
                link = self.base_url + link
            elif not link.startswith('http'):
                link = self.base_url + '/' + link
            
            # 시간 추출
            time_element = None
            time_selectors = [
                'span[class*="time"]',
                'span[class*="date"]',
                'time',
                'span[class*="timestamp"]',
                'div[class*="time"]',
                'div[class*="date"]'
            ]
            
            for selector in time_selectors:
                time_element = element.select_one(selector)
                if time_element:
                    break
            
            publish_time = time_element.get_text(strip=True) if time_element else ''
            
            # 요약 추출
            summary_element = None
            summary_selectors = [
                'p[class*="summary"]',
                'p[class*="description"]',
                'div[class*="summary"]',
                'div[class*="description"]',
                'p'
            ]
            
            for selector in summary_selectors:
                summary_element = element.select_one(selector)
                if summary_element and summary_element.get_text(strip=True):
                    break
            
            summary = summary_element.get_text(strip=True) if summary_element else ''
            
            # 카테고리/태그 추출
            category_element = None
            category_selectors = [
                'span[class*="category"]',
                'span[class*="tag"]',
                'div[class*="category"]',
                'div[class*="tag"]',
                'a[class*="category"]'
            ]
            
            for selector in category_selectors:
                category_element = element.select_one(selector)
                if category_element:
                    break
            
            category = category_element.get_text(strip=True) if category_element else ''
            
            # 중복 제거를 위한 정리
            title = re.sub(r'\s+', ' ', title).strip()
            summary = re.sub(r'\s+', ' ', summary).strip()
            
            return {
                'title': title,
                'link': link,
                'publish_time': publish_time,
                'summary': summary,
                'category': category,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"뉴스 아이템 추출 중 오류: {str(e)}")
            return None
    
    def get_news_detail(self, news_url: str) -> Optional[Dict]:
        """
        개별 뉴스 상세 정보를 가져옵니다.
        
        Args:
            news_url (str): 뉴스 상세 페이지 URL
            
        Returns:
            Optional[Dict]: 뉴스 상세 정보
        """
        try:
            response = self.session.get(news_url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 제목 추출
            title_element = None
            title_selectors = [
                'h1[class*="title"]',
                'h1[class*="headline"]',
                'h1',
                '.articleHeader h1',
                '.article-title'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    break
            
            title = title_element.get_text(strip=True) if title_element else ''
            
            # 본문 추출
            content_element = None
            content_selectors = [
                'div[class*="content"]',
                'div[class*="article-body"]',
                'article',
                '.article-content',
                '.articleBody',
                '.contentSection'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            content = content_element.get_text(strip=True) if content_element else ''
            
            # 작성자 추출
            author_element = None
            author_selectors = [
                'span[class*="author"]',
                'span[class*="writer"]',
                'div[class*="author"]',
                '.articleAuthor',
                '.author'
            ]
            
            for selector in author_selectors:
                author_element = soup.select_one(selector)
                if author_element:
                    break
            
            author = author_element.get_text(strip=True) if author_element else ''
            
            # 발행 시간 추출
            time_element = None
            time_selectors = [
                'span[class*="time"]',
                'span[class*="date"]',
                'time',
                '.articleDate',
                '.publishDate'
            ]
            
            for selector in time_selectors:
                time_element = soup.select_one(selector)
                if time_element:
                    break
            
            publish_time = time_element.get_text(strip=True) if time_element else ''
            
            return {
                'title': title,
                'content': content,
                'author': author,
                'publish_time': publish_time,
                'url': news_url,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"뉴스 상세 정보 가져오기 중 오류: {str(e)}")
            return None
    
    def save_to_csv(self, news_list: List[Dict], filename: str = None) -> str:
        """
        뉴스 목록을 CSV 파일로 저장합니다.
        
        Args:
            news_list (List[Dict]): 저장할 뉴스 목록
            filename (str): 저장할 파일명
            
        Returns:
            str: 저장된 파일 경로
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"investing_news_{timestamp}.csv"
        
        df = pd.DataFrame(news_list)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        self.logger.info(f"뉴스 {len(news_list)}개를 {filename}에 저장했습니다.")
        return filename
    
    def get_recent_news(self, hours: int = 24) -> List[Dict]:
        """
        최근 N시간 내의 뉴스를 가져옵니다.
        
        Args:
            hours (int): 몇 시간 전까지의 뉴스를 가져올지
            
        Returns:
            List[Dict]: 최근 뉴스 목록
        """
        all_news = self.get_news_list(max_pages=5)  # 더 많은 페이지를 스크래핑
        
        # 시간 필터링 (간단한 구현)
        # 실제로는 더 정교한 시간 파싱이 필요할 수 있습니다
        recent_news = []
        for news in all_news:
            # 시간 정보가 있는 경우에만 필터링
            if news.get('publish_time'):
                recent_news.append(news)
        
        return recent_news
    
    def test_connection(self) -> bool:
        """
        웹사이트 연결을 테스트합니다.
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            # 메인 페이지부터 접근
            main_response = self.session.get(self.base_url, timeout=15)
            main_response.raise_for_status()
            
            # 잠시 대기
            time.sleep(2)
            
            # 뉴스 페이지 접근
            response = self.session.get(self.news_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else ''
            
            self.logger.info(f"연결 성공! 페이지 제목: {title}")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.error("403 Forbidden 오류: 봇 차단이 감지되었습니다.")
                self.logger.info("대안 방법을 시도해보겠습니다...")
                return self._try_alternative_connection()
            else:
                self.logger.error(f"HTTP 오류: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"연결 실패: {str(e)}")
            return False
    
    def _try_alternative_connection(self) -> bool:
        """
        대안적인 연결 방법을 시도합니다.
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            # 다른 User-Agent 시도
            alternative_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            temp_session = requests.Session()
            temp_session.headers.update(alternative_headers)
            
            # 다른 URL 시도
            alternative_urls = [
                'https://www.investing.com/news/',
                'https://www.investing.com/news/stock-market-news/1',
                'https://www.investing.com/news/economic-indicators'
            ]
            
            for url in alternative_urls:
                try:
                    self.logger.info(f"대안 URL 시도: {url}")
                    response = temp_session.get(url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if soup.title:
                        self.logger.info(f"대안 URL 성공: {url}")
                        # 성공한 설정으로 업데이트
                        self.session.headers.update(alternative_headers)
                        return True
                        
                except Exception as e:
                    self.logger.warning(f"대안 URL 실패 {url}: {str(e)}")
                    continue
            
            self.logger.error("모든 대안 방법이 실패했습니다.")
            return False
            
        except Exception as e:
            self.logger.error(f"대안 연결 시도 중 오류: {str(e)}")
            return False
    
    def get_mock_news(self) -> List[Dict]:
        """
        봇 차단 시 사용할 목업 뉴스 데이터를 반환합니다.
        
        Returns:
            List[Dict]: 목업 뉴스 목록
        """
        self.logger.info("봇 차단으로 인해 목업 데이터를 사용합니다.")
        
        mock_news = [
            {
                'title': '주식 시장 뉴스: 글로벌 경제 동향 분석',
                'link': 'https://www.investing.com/news/stock-market-news',
                'publish_time': '2024-01-15 10:30:00',
                'summary': '글로벌 주식 시장의 최신 동향과 투자자들이 주목해야 할 주요 이슈들을 분석합니다.',
                'category': 'Stock Market',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': '테크 주식들의 변동성 증가',
                'link': 'https://www.investing.com/news/stock-market-news',
                'publish_time': '2024-01-15 09:15:00',
                'summary': '테크 섹터 주식들이 높은 변동성을 보이며 투자자들의 관심을 집중시키고 있습니다.',
                'category': 'Technology',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': '중국 경제 데이터 발표 예정',
                'link': 'https://www.investing.com/news/stock-market-news',
                'publish_time': '2024-01-15 08:45:00',
                'summary': '중국에서 중요한 경제 지표들이 발표될 예정이며, 이는 글로벌 시장에 영향을 미칠 것으로 예상됩니다.',
                'category': 'Economy',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        return mock_news


def main():
    """
    메인 실행 함수
    """
    scraper = InvestingScraper()
    
    print("Investing.com 주식 시장 뉴스 스크래핑을 시작합니다...")
    
    # 연결 테스트
    if not scraper.test_connection():
        print("웹사이트 연결에 실패했습니다.")
        return
    
    # 뉴스 목록 가져오기
    news_list = scraper.get_news_list(max_pages=2)
    
    if news_list:
        print(f"총 {len(news_list)}개의 뉴스를 찾았습니다.")
        
        # CSV로 저장
        filename = scraper.save_to_csv(news_list)
        print(f"뉴스가 {filename}에 저장되었습니다.")
        
        # 처음 5개 뉴스 출력
        print("\n=== 최근 뉴스 미리보기 ===")
        for i, news in enumerate(news_list[:5], 1):
            print(f"{i}. {news.get('title', '제목 없음')}")
            print(f"   시간: {news.get('publish_time', '시간 정보 없음')}")
            print(f"   링크: {news.get('link', '링크 없음')}")
            if news.get('summary'):
                print(f"   요약: {news.get('summary', '')[:100]}...")
            print()
    else:
        print("뉴스를 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
