import os
import json
import sys
from dotenv import load_dotenv

from src.scrapers.naver_scraper import scrape_naver_stock_news_filtered

# 환경변수 로드
load_dotenv()

def load_stock_list() -> dict:
    """
    환경변수에서 주식 리스트를 로드
    지원하는 형식:
    1. 주식코드만: "005930,000660,035420"
    2. 종목명만: "삼성전자,SK하이닉스,NAVER"
    3. 주식코드+종목명: "005930(삼성전자),000660(SK하이닉스)"
    4. JSON 형태: '{"005930":"삼성전자","000660":"SK하이닉스"}'
    """
    # UTF-8 인코딩으로 환경변수 읽기
    stock_list_str = os.getenv("STOCK_LIST", "")
    
    # 한글 인코딩 문제 해결을 위한 처리
    if isinstance(stock_list_str, bytes):
        stock_list_str = stock_list_str.decode('utf-8')
    
    # 디버깅을 위한 출력
    print(f"원본 STOCK_LIST: {repr(stock_list_str)}")

    if not stock_list_str:
        print("환경변수 STOCK_LIST가 설정되지 않았습니다.")
        print("\n지원하는 형식:")
        print("1. 주식코드만: STOCK_LIST=005930,000660,035420")
        print("2. 종목명만: STOCK_LIST=삼성전자,SK하이닉스,NAVER")
        print("3. 주식코드+종목명: STOCK_LIST=005930(삼성전자),000660(SK하이닉스)")
        print("4. JSON 형태: STOCK_LIST={\"005930\":\"삼성전자\",\"000660\":\"SK하이닉스\"}")
        return {}

    stock_info = {}

    # JSON 형태인지 확인
    if stock_list_str.strip().startswith('{'):
        try:
            stock_dict = json.loads(stock_list_str)
            stock_info = stock_dict
            print(f"JSON 형태로 로드된 주식 리스트: {list(stock_dict.items())}")
        except json.JSONDecodeError:
            print("JSON 형식이 올바르지 않습니다.")
            return {}
    else:
        # 쉼표로 구분된 리스트 처리
        items = [item.strip() for item in stock_list_str.split(",") if item.strip()]

        for item in items:
            # 주식코드(종목명) 형태인지 확인
            if '(' in item and ')' in item:
                # 005930(삼성전자) 형태
                code = item.split('(')[0].strip()
                name = item.split('(')[1].split(')')[0].strip()
                stock_info[code] = name
            else:
                # 주식코드만 또는 종목명만 (종목명을 모르므로 코드를 그대로 사용)
                stock_info[item] = item

    print(f"로드된 주식 정보: {stock_info}")
    return stock_info