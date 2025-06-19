import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
from typing import List, Dict, Optional
import logging
import re

class YahooFinanceScraper:
    """
    Yahoo Finance에서 주식 시장 뉴스를 스크래핑하는 클래스
    """
    
    def __init__(self):
        self.base_url = "https://finance.yahoo.com"
        self.news_url = "https://finance.yahoo.com/news/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
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
                    url = f"{self.news_url}?offset={(page-1)*20}"
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                news_items = self._parse_news_list(soup)
                
                all_news.extend(news_items)
                self.logger.info(f"페이지 {page}에서 {len(news_items)}개의 뉴스를 찾았습니다.")
                
                # 요청 간 딜레이
                time.sleep(random.uniform(2, 4))
                
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
        
        # Yahoo Finance의 뉴스 선택자들
        news_selectors = [
            'h3 a[href*="/news/"]',
            '.js-content-viewer a[href*="/news/"]',
            'a[href*="/news/"]',
            '.js-stream-content a[href*="/news/"]'
        ]
        
        news_elements = []
        for selector in news_selectors:
            news_elements = soup.select(selector)
            if news_elements:
                self.logger.info(f"선택자 '{selector}'로 {len(news_elements)}개의 뉴스 요소를 찾았습니다.")
                break
        
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
            title = element.get_text(strip=True)
            link = element.get('href', '')
            
            if not title or not link:
                return None
            
            # 상대 URL을 절대 URL로 변환
            if link.startswith('/'):
                link = self.base_url + link
            elif not link.startswith('http'):
                link = self.base_url + '/' + link
            
            # 부모 요소에서 시간 정보 찾기
            parent = element.find_parent(['div', 'article'])
            time_element = None
            if parent:
                time_element = parent.find(['time', 'span'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['time', 'date']))
            
            publish_time = time_element.get_text(strip=True) if time_element else ''
            
            return {
                'title': title,
                'link': link,
                'publish_time': publish_time,
                'summary': '',
                'category': 'Finance',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"뉴스 아이템 추출 중 오류: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """
        웹사이트 연결을 테스트합니다.
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            response = self.session.get(self.news_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else ''
            
            self.logger.info(f"연결 성공! 페이지 제목: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"연결 실패: {str(e)}")
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
                'title': 'Yahoo Finance: 글로벌 주식 시장 동향',
                'link': 'https://finance.yahoo.com/news/',
                'publish_time': '2024-01-15 11:00:00',
                'summary': '글로벌 주식 시장의 최신 동향과 투자 전략에 대한 분석을 제공합니다.',
                'category': 'Finance',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': '테크 기업들의 실적 발표 예정',
                'link': 'https://finance.yahoo.com/news/',
                'publish_time': '2024-01-15 10:30:00',
                'summary': '주요 테크 기업들의 분기 실적 발표가 예정되어 있어 시장의 관심이 집중되고 있습니다.',
                'category': 'Technology',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': '연준의 금리 정책에 대한 시장 반응',
                'link': 'https://finance.yahoo.com/news/',
                'publish_time': '2024-01-15 10:00:00',
                'summary': '연방준비제도(Fed)의 금리 정책 결정에 대한 시장의 반응과 전망을 분석합니다.',
                'category': 'Economy',
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        return mock_news 