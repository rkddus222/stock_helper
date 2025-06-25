import os
from dotenv import load_dotenv
from datetime import datetime
import json

from src.scrapers.api_scraper import get_stock_current_price
from src.nodes.types import State
from src.scrapers.get_stock import load_stock_list


def stock_scraper(state: State):
    """
    주식 리스트를 로드하고 각 종목에 대해 현재가 정보를 수집하여 state에 저장
    """
    print("=== 주식 데이터 수집 시작 ===")

    # 주식 리스트 로드
    stock_list = load_stock_list()
    print(stock_list)
    if not stock_list:
        print("주식 리스트가 비어있습니다. 환경변수 STOCK_LIST를 확인해주세요.")
        state["scraped_data"] = "주식 리스트가 비어있습니다."
        return state

    results = {}
    
    print(f"\n=== 주식 현재가 정보 수집 시작 ===")
    print(f"수집 대상: {len(stock_list)}개 종목")
    print("=" * 50)

    for i, (stock_code, stock_name) in enumerate(stock_list.items(), 1):
        print(f"\n[{i}/{len(stock_list)}] {stock_code}({stock_name}) 현재가 정보 수집 중...")

        try:
            # 현재가 정보 수집
            current_price_info = get_stock_current_price(
                stock_info=stock_code
            )

            # 종목코드(종목명) 형태로 키 생성
            key = f"{stock_code}({stock_name})"
            results[key] = current_price_info
            
            if current_price_info:
                print(f"  ✓ 현재가 정보 수집 완료")
                print(f"  현재가: {current_price_info.get('현재가', 'N/A'):,}원")
                print(f"  등락률: {current_price_info.get('등락률', 'N/A')}%")
            else:
                print(f"  ✗ 현재가 정보 수집 실패")

        except Exception as e:
            print(f"  ✗ {stock_code}({stock_name}) 현재가 정보 수집 실패: {str(e)}")
            key = f"{stock_code}({stock_name})"
            results[key] = {}

    # 수집 결과를 JSON 형태로 state에 저장
    scraped_data = {
        "timestamp": datetime.now().isoformat(),
        "total_stocks": len(stock_list),
        "collected_data": results,
        "summary": {
            "total_stocks_with_data": len([data for data in results.values() if data]),
            "stocks_without_data": len([data for data in results.values() if not data])
        }
    }
    
    # 한글 인코딩 문제 해결을 위한 JSON 저장
    try:
        json_str = json.dumps(scraped_data, ensure_ascii=False, indent=2, default=str)
        # 디버깅을 위한 출력
        print(f"JSON 저장 테스트 - 키 확인:")
        for key in results.keys():
            print(f"  키: {repr(key)}")
        state["scraped_data"] = json_str
    except Exception as e:
        print(f"JSON 저장 중 오류: {e}")
        # 대안: 문자열로 저장
        state["scraped_data"] = str(scraped_data)
    
    print(f"\n=== 주식 데이터 수집 완료 ===")
    print(f"총 {len(stock_list)}개 종목에서 데이터 수집")
    print(f"데이터 수집 성공: {scraped_data['summary']['total_stocks_with_data']}개")
    print(f"데이터 수집 실패: {scraped_data['summary']['stocks_without_data']}개")
    
    return state