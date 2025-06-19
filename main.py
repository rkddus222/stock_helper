#!/usr/bin/env python3
"""
주식 도우미 메인 애플리케이션

네이버 금융 뉴스와 Investing.com 뉴스를 스크래핑하고 분석하여 투자 의사결정을 돕습니다.
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# src 폴더를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.naver_scraper import scrape_naver_finance_news_titles
from scrapers.yahoo_finance_scraper import YahooFinanceScraper
from news_based_analyzer import NewsBasedAnalyzer

def main():
    """메인 애플리케이션"""
    # 환경 변수 로드
    load_dotenv()
    
    # API 키 확인
    if not os.getenv('PERPLEXITY_API_KEY'):
        print("Error: PERPLEXITY_API_KEY가 설정되지 않았습니다.")
        print("1. .env 파일을 생성하세요.")
        print("2. PERPLEXITY_API_KEY=your_api_key를 추가하세요.")
        return
    
    print("=== 주식 뉴스 기반 투자 분석 시스템 ===")
    
    # 분석기 초기화
    analyzer = NewsBasedAnalyzer()
    
    # Yahoo Finance 스크래퍼 초기화
    yahoo_scraper = YahooFinanceScraper()
    
    all_news_articles = []
    
    # 네이버 뉴스 수집 (기본 5페이지)
    print("\n네이버 금융 뉴스를 수집하는 중...")
    naver_articles = scrape_naver_finance_news_titles(max_pages=5)
    if naver_articles:
        for article in naver_articles:
            article['source'] = '네이버'
        all_news_articles.extend(naver_articles)
        print(f"네이버 뉴스 {len(naver_articles)}개 수집 완료.")
    else:
        print("네이버 뉴스 수집에 실패했습니다.")

    # Yahoo Finance 뉴스 수집 (기본 2페이지)
    print("\nYahoo Finance 뉴스를 수집하는 중...")
    if yahoo_scraper.test_connection():
        yahoo_articles = yahoo_scraper.get_news_list(max_pages=2)
        if yahoo_articles:
            for article in yahoo_articles:
                article['source'] = 'Yahoo Finance'
            all_news_articles.extend(yahoo_articles)
            print(f"Yahoo Finance 뉴스 {len(yahoo_articles)}개 수집 완료.")
        else:
            print("Yahoo Finance 뉴스 수집에 실패했습니다.")
    else:
        print("Yahoo Finance 연결에 실패했습니다. 목업 데이터를 사용합니다.")
        # 봇 차단 시 목업 데이터 사용
        mock_articles = yahoo_scraper.get_mock_news()
        for article in mock_articles:
            article['source'] = 'Yahoo Finance (Mock)'
        all_news_articles.extend(mock_articles)
        print(f"Yahoo Finance 목업 뉴스 {len(mock_articles)}개 사용.")
    
    if not all_news_articles:
        print("수집된 뉴스가 없습니다. 프로그램을 종료합니다.")
        return
    
    print(f"\n총 {len(all_news_articles)}개의 뉴스를 수집했습니다.")
    
    # DataFrame으로 변환
    news_df = pd.DataFrame(all_news_articles)
    news_df['date'] = datetime.now()  # 현재 시간 추가
    
    # 뉴스 분석
    print("\n뉴스를 분석하고 있습니다...")
    analyzed_df = analyzer.analyze_news_data(news_df)
    
    # 투자 요약 생성
    summary = analyzer.generate_investment_summary(analyzed_df)
    print("\n=== 통합 뉴스 투자 분석 요약 ===")
    print(summary)
    
    # 결과 저장
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"combined_analysis_result_{timestamp}.csv"
    analyzed_df.to_csv(filename, encoding='utf-8-sig', index=False)
    print(f"\n분석 결과가 {filename}에 저장되었습니다.")
    
    print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()