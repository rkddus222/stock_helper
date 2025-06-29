from datetime import datetime
import json

from src.service.stock_scrapers.get_stock import load_stock_list
from src.service.news_scrapers.naver_scraper import scrape_stock_domestic_news
from src.nodes.types import State
from src.service.news_scrapers.yahoo_scraper import scrape_stock_worldwide_news


def news_scraper(state: State):
    """
    주식 리스트를 로드하고 각 종목에 대해 뉴스를 수집하여 state에 저장
    """
    print("=== 뉴스 데이터 수집 시작 ===")
    
    # 주식 리스트 로드 (국내, 해외 분리)
    stocks_domestic, stocks_worldwide = load_stock_list()
    
    if not stocks_domestic and not stocks_worldwide:
        print("주식 리스트가 비어있습니다. 환경변수 STOCK_LIST_DOMESTIC, STOCK_LIST_WORLDWIDE를 확인해주세요.")
        state["scraped_data"] = "주식 리스트가 비어있습니다."
        return state
    
    # state에 주식 리스트 저장
    state["stock_list_domestic"] = list(stocks_domestic.keys())
    state["stock_list_worldwide"] = list(stocks_worldwide.keys())

    total_stocks = len(stocks_domestic) + len(stocks_worldwide)
    print(f"수집 대상 종목: {total_stocks}개 (국내: {len(stocks_domestic)}개, 해외: {len(stocks_worldwide)}개)")

    # 국내 주식 뉴스 수집
    if stocks_domestic:
        print(f"\n=== 국내 주식 뉴스 수집 ===")
        for code, name in stocks_domestic.items():
            print(f"  - {code}({name})")

        collected_domestic_news = scrape_stock_domestic_news(
            stock_info=stocks_domestic,
            keyword="",  # 모든 뉴스 수집
            max_count_per_stock=10
        )
    else:
        collected_domestic_news = {}

    # 해외 주식 뉴스 수집
    if stocks_worldwide:
        print(f"\n=== 해외 주식 뉴스 수집 ===")
        for code, name in stocks_worldwide.items():
            print(f"  - {code}({name})")

        collected_worldwide_news = scrape_stock_worldwide_news(
            stock_info=stocks_worldwide,
            keyword="",  # 모든 뉴스 수집
            max_count_per_stock=10
        )
    else:
        collected_worldwide_news = {}
    
    # 국내와 해외 뉴스 합치기
    all_collected_news = {}
    all_collected_news.update(collected_domestic_news)
    all_collected_news.update(collected_worldwide_news)
    
    # 수집 결과를 JSON 형태로 state에 저장
    scraped_data = {
        "timestamp": datetime.now().isoformat(),
        "total_stocks": total_stocks,
        "domestic_stocks": len(stocks_domestic),
        "worldwide_stocks": len(stocks_worldwide),
        "collected_news": all_collected_news,
        "domestic_news": collected_domestic_news,
        "worldwide_news": collected_worldwide_news,
        "summary": {
            "total_news": sum(len(news) for news in all_collected_news.values()),
            "domestic_news_count": sum(len(news) for news in collected_domestic_news.values()),
            "worldwide_news_count": sum(len(news) for news in collected_worldwide_news.values()),
            "stocks_with_news": len([news for news in all_collected_news.values() if news]),
            "domestic_stocks_with_news": len([news for news in collected_domestic_news.values() if news]),
            "worldwide_stocks_with_news": len([news for news in collected_worldwide_news.values() if news])
        }
    }
    
    # 한글 인코딩 문제 해결을 위한 JSON 저장
    try:
        json_str = json.dumps(scraped_data, ensure_ascii=False, indent=2, default=str)
        # 디버깅을 위한 출력
        print(f"JSON 저장 테스트 - 키 확인:")
        for key in all_collected_news.keys():
            print(f"  키: {repr(key)}")
        state["scraped_data"] = json_str
    except Exception as e:
        print(f"JSON 저장 중 오류: {e}")
        # 대안: 문자열로 저장
        state["scraped_data"] = str(scraped_data)
    
    print(f"\n=== 주식 데이터 수집 완료 ===")
    print(f"총 {total_stocks}개 종목에서 {scraped_data['summary']['total_news']}개 뉴스 수집")
    print(f"  - 국내: {scraped_data['summary']['domestic_news_count']}개 뉴스")
    print(f"  - 해외: {scraped_data['summary']['worldwide_news_count']}개 뉴스")
    print(f"뉴스가 있는 종목: {scraped_data['summary']['stocks_with_news']}개")
    print(f"  - 국내: {scraped_data['summary']['domestic_stocks_with_news']}개 종목")
    print(f"  - 해외: {scraped_data['summary']['worldwide_stocks_with_news']}개 종목")
    
    return state
