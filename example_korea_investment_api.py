#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국투자증권 API - 주식 일별 가격 데이터 조회 예제
주식 분석을 위한 OHLCV 데이터 수집
"""

import os
from dotenv import load_dotenv
from src.scrapers.api_scraper import KoreaInvestmentAPIScraper
from datetime import datetime, timedelta
import json

# 환경변수 로드
load_dotenv()

def main():
    """
    한국투자증권 API를 사용한 주식 일별 가격 데이터 조회 예제
    """
    
    # 환경변수에서 API 키 정보 가져오기
    app_key = os.getenv("KOREA_INVESTMENT_APP_KEY")
    app_secret = os.getenv("KOREA_INVESTMENT_APP_SECRET")
    
    if not all([app_key, app_secret]):
        print("환경변수를 설정해주세요:")
        print("KOREA_INVESTMENT_APP_KEY: 한국투자증권 앱키")
        print("KOREA_INVESTMENT_APP_SECRET: 한국투자증권 앱시크릿")
        return
    
    # API 스크래퍼 초기화 (모의투자 환경)
    scraper = KoreaInvestmentAPIScraper(
        app_key=app_key,
        app_secret=app_secret,
        is_production=False  # 모의투자 환경
    )
    
    print("=== 한국투자증권 API - 주식 일별 가격 데이터 조회 ===\n")
    
    # 1. 종목 검색 (종목코드 찾기)
    print("1. 종목 검색 (삼성전자)")
    search_results = scraper.get_stock_search("삼성전자")
    if search_results:
        for result in search_results:
            print(f"  - {result['종목명']} ({result['종목코드']}) - {result['시장구분']}")
    else:
        print("  검색 결과가 없습니다.")
    print()
    
    # 2. 일별 가격 데이터 조회 (최근 30일)
    print("2. 삼성전자 일별 가격 데이터 조회 (최근 30일)")
    
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    daily_prices = scraper.get_stock_daily_price("005930", start_date, end_date)
    
    if daily_prices:
        print(f"  총 {len(daily_prices)}일간의 데이터를 조회했습니다.\n")
        
        # 최근 10일간 데이터 표시
        print("  최근 10일간 OHLCV 데이터:")
        print("  날짜        시가      고가      저가      종가      거래량      등락률")
        print("  " + "-" * 80)
        
        for i, price in enumerate(daily_prices[:10]):
            date = price['날짜']
            open_price = price['시가']
            high_price = price['고가']
            low_price = price['저가']
            close_price = price['종가']
            volume = price['거래량']
            change_rate = price['등락률']
            
            print(f"  {date}  {open_price:8,}  {high_price:8,}  {low_price:8,}  "
                  f"{close_price:8,}  {volume:10,}  {change_rate:6.2f}%")
        
        # 데이터를 JSON 파일로 저장 (분석용)
        output_file = f"삼성전자_일별가격_{start_date}_{end_date}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(daily_prices, f, ensure_ascii=False, indent=2)
        
        print(f"\n  데이터가 '{output_file}' 파일로 저장되었습니다.")
        print("  이 데이터를 사용하여 기술적 분석, 차트 분석, 백테스팅 등을 수행할 수 있습니다.")
        
    else:
        print("  일별 가격 데이터 조회에 실패했습니다.")
    
    print("\n=== 조회 완료 ===")

if __name__ == "__main__":
    main() 