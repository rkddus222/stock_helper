import os
from dotenv import load_dotenv
from datetime import datetime
import json

from src.scrapers.get_stock import load_stock_list
from src.scrapers.naver_scraper import scrape_stock_news
from src.nodes.types import State

def news_scraper(state: State):
    """
    주식 리스트를 로드하고 각 종목에 대해 뉴스를 수집하여 state에 저장
    """
    print("=== 뉴스 데이터 수집 시작 ===")
    
    # 주식 리스트 로드
    stock_list = load_stock_list()
    
    if not stock_list:
        print("주식 리스트가 비어있습니다. 환경변수 STOCK_LIST를 확인해주세요.")
        state["scraped_data"] = "주식 리스트가 비어있습니다."
        return state
    
    # state에 주식 리스트 저장
    state["stock_list"] = list(stock_list.keys())
    
    print(f"수집 대상 종목: {len(stock_list)}개")
    for code, name in stock_list.items():
        print(f"  - {code}({name})")
    
    # get_stock.py의 scrape_stock_news 함수를 사용하여 뉴스 수집
    collected_news = scrape_stock_news(
        stock_info=stock_list,
        keyword="",  # 모든 뉴스 수집
        max_count_per_stock=10
    )
    
    # 수집 결과를 JSON 형태로 state에 저장
    scraped_data = {
        "timestamp": datetime.now().isoformat(),
        "total_stocks": len(stock_list),
        "collected_news": collected_news,
        "summary": {
            "total_news": sum(len(news) for news in collected_news.values()),
            "stocks_with_news": len([news for news in collected_news.values() if news])
        }
    }
    
    # 한글 인코딩 문제 해결을 위한 JSON 저장
    try:
        json_str = json.dumps(scraped_data, ensure_ascii=False, indent=2, default=str)
        # 디버깅을 위한 출력
        print(f"JSON 저장 테스트 - 키 확인:")
        for key in collected_news.keys():
            print(f"  키: {repr(key)}")
        state["scraped_data"] = json_str
    except Exception as e:
        print(f"JSON 저장 중 오류: {e}")
        # 대안: 문자열로 저장
        state["scraped_data"] = str(scraped_data)
    
    print(f"\n=== 주식 데이터 수집 완료 ===")
    print(f"총 {len(stock_list)}개 종목에서 {scraped_data['summary']['total_news']}개 뉴스 수집")
    print(f"뉴스가 있는 종목: {scraped_data['summary']['stocks_with_news']}개")
    
    return state
