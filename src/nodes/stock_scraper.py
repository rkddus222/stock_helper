from datetime import datetime
import json

from src.service.stock_scrapers.api_scraper import get_stock_current_price
from src.nodes.types import State
from src.service.stock_scrapers.get_stock import load_stock_list


def stock_scraper(state: State):
    """
    주식 리스트를 로드하고 각 종목에 대해 현재가 정보를 수집하여 state에 저장
    """
    print("=== 주식 데이터 수집 시작 ===")

    # 주식 리스트 로드 (국내, 해외 분리)
    stocks_domestic, stocks_worldwide = load_stock_list()
    
    print(f"국내 주식: {len(stocks_domestic)}개, 해외 주식: {len(stocks_worldwide)}개")
    
    if not stocks_domestic and not stocks_worldwide:
        print("주식 리스트가 비어있습니다. 환경변수 STOCK_LIST_DOMESTIC, STOCK_LIST_WORLDWIDE를 확인해주세요.")
        state["stock_data"] = "주식 리스트가 비어있습니다."
        return state

    results = {}
    domestic_results = {}
    worldwide_results = {}
    
    # 국내 주식 처리
    if stocks_domestic:
        print(f"\n=== 국내 주식 현재가 정보 수집 시작 ===")
        print(f"수집 대상: {len(stocks_domestic)}개 종목")
        print("=" * 50)

        for i, (stock_code, stock_name) in enumerate(stocks_domestic.items(), 1):
            print(f"\n[{i}/{len(stocks_domestic)}] {stock_code}({stock_name}) 현재가 정보 수집 중...")

            try:
                # 현재가 정보 수집
                current_price_info = get_stock_current_price(stock_code)

                # 종목코드(종목명) 형태로 키 생성
                key = f"{stock_code}({stock_name})"
                results[key] = current_price_info
                domestic_results[key] = current_price_info
                
                if current_price_info:
                    print(f"  ✓ 현재가 정보 수집 완료")
                    print(f"  현재가: {current_price_info.get('현재가', 'N/A'):,}원")
                    print(f"  등락률: {current_price_info.get('등락률', 'N/A')}%")
                    print(f"  거래량: {current_price_info.get('거래량', 'N/A'):,}주")
                    print(f"  시가총액: {current_price_info.get('시가총액', 'N/A'):,}원")
                else:
                    print(f"  ✗ 현재가 정보 수집 실패")

            except Exception as e:
                print(f"  ✗ {stock_code}({stock_name}) 현재가 정보 수집 실패: {str(e)}")
                key = f"{stock_code}({stock_name})"
                results[key] = {}
                domestic_results[key] = {}

    # 해외 주식 처리
    if stocks_worldwide:
        print(f"\n=== 해외 주식 현재가 정보 수집 시작 ===")
        print(f"수집 대상: {len(stocks_worldwide)}개 종목")
        print("=" * 50)

        for i, (stock_code, stock_name) in enumerate(stocks_worldwide.items(), 1):
            print(f"\n[{i}/{len(stocks_worldwide)}] {stock_code}({stock_name}) 현재가 정보 수집 중...")

            try:
                # 현재가 정보 수집
                current_price_info = get_stock_current_price(stock_code)

                # 종목코드(종목명) 형태로 키 생성
                key = f"{stock_code}({stock_name})"
                results[key] = current_price_info
                worldwide_results[key] = current_price_info
                
                if current_price_info:
                    print(f"  ✓ 현재가 정보 수집 완료")
                    currency = current_price_info.get('통화', 'USD')
                    print(f"  현재가: {current_price_info.get('현재가', 'N/A'):,.2f} {currency}")
                    print(f"  등락률: {current_price_info.get('등락률', 'N/A')}%")
                    print(f"  거래량: {current_price_info.get('거래량', 'N/A'):,}주")
                    if current_price_info.get('시가총액'):
                        print(f"  시가총액: {current_price_info.get('시가총액', 'N/A'):,} {currency}")
                    print(f"  거래소: {current_price_info.get('거래소', 'N/A')}")
                else:
                    print(f"  ✗ 현재가 정보 수집 실패")

            except Exception as e:
                print(f"  ✗ {stock_code}({stock_name}) 현재가 정보 수집 실패: {str(e)}")
                key = f"{stock_code}({stock_name})"
                results[key] = {}
                worldwide_results[key] = {}

    # 수집 결과를 JSON 형태로 state에 저장
    stock_data = {
        "timestamp": datetime.now().isoformat(),
        "total_stocks": len(stocks_domestic) + len(stocks_worldwide),
        "domestic_stocks": len(stocks_domestic),
        "worldwide_stocks": len(stocks_worldwide),
        "collected_data": results,
        "domestic_data": domestic_results,
        "worldwide_data": worldwide_results,
        "summary": {
            "total_stocks_with_data": len([data for data in results.values() if data]),
            "domestic_stocks_with_data": len([data for data in domestic_results.values() if data]),
            "worldwide_stocks_with_data": len([data for data in worldwide_results.values() if data]),
            "stocks_without_data": len([data for data in results.values() if not data])
        }
    }
    
    # 한글 인코딩 문제 해결을 위한 JSON 저장
    try:
        json_str = json.dumps(stock_data, ensure_ascii=False, indent=2, default=str)
        state["stock_data"] = json_str
    except Exception as e:
        print(f"JSON 저장 중 오류: {e}")
        # 대안: 문자열로 저장
        state["stock_data"] = str(stock_data)
    
    print(f"\n=== 주식 데이터 수집 완료 ===")
    print(f"총 {len(stocks_domestic) + len(stocks_worldwide)}개 종목에서 데이터 수집")
    print(f"  - 국내: {len(stocks_domestic)}개, 해외: {len(stocks_worldwide)}개")
    print(f"데이터 수집 성공: {stock_data['summary']['total_stocks_with_data']}개")
    print(f"  - 국내: {stock_data['summary']['domestic_stocks_with_data']}개")
    print(f"  - 해외: {stock_data['summary']['worldwide_stocks_with_data']}개")
    print(f"데이터 수집 실패: {stock_data['summary']['stocks_without_data']}개")
    
    return state