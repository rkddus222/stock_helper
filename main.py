#!/usr/bin/env python3
"""
주식 도우미 메인 애플리케이션

네이버 금융 뉴스를 스크래핑하고 분석하여 투자 의사결정을 돕습니다.
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
    
    print("=== 네이버 금융 뉴스 기반 투자 분석 시스템 ===")
    
    # 분석기 초기화
    analyzer = NewsBasedAnalyzer()
    
    while True:
        print("\n1. 오늘의 뉴스 수집 및 분석")
        print("2. 특정 페이지 수만큼 뉴스 분석")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ")
        
        if choice == '1':
            print("\n오늘의 뉴스를 수집하고 분석합니다...")
            
            # 네이버 뉴스 스크래핑 (기본 5페이지)
            news_articles = scrape_naver_finance_news_titles(max_pages=5)
            
            if not news_articles:
                print("수집된 뉴스가 없습니다.")
                continue
            
            print(f"\n총 {len(news_articles)}개의 뉴스를 수집했습니다.")
            
            # DataFrame으로 변환
            news_df = pd.DataFrame(news_articles)
            news_df['date'] = datetime.now()  # 현재 시간 추가
            
            # 뉴스 분석
            print("\n뉴스를 분석하고 있습니다...")
            analyzed_df = analyzer.analyze_news_data(news_df)
            
            # 투자 요약 생성
            summary = analyzer.generate_investment_summary(analyzed_df)
            print("\n=== 투자 분석 요약 ===")
            print(summary)
            
            # 결과 저장
            save = input("\n분석 결과를 저장하시겠습니까? (y/n): ")
            if save.lower() == 'y':
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_result_{timestamp}.csv"
                analyzed_df.to_csv(filename, encoding='utf-8-sig', index=False)
                print(f"분석 결과가 {filename}에 저장되었습니다.")
        
        elif choice == '2':
            pages = input("\n수집할 최대 페이지 수를 입력하세요 (1-10): ")
            try:
                pages = int(pages)
                if pages <= 0 or pages > 10:
                    print("1-10 사이의 숫자를 입력하세요.")
                    continue
                
                print(f"\n최대 {pages}페이지까지 뉴스를 수집하고 분석합니다...")
                
                # 네이버 뉴스 스크래핑
                news_articles = scrape_naver_finance_news_titles(max_pages=pages)
                
                if not news_articles:
                    print("수집된 뉴스가 없습니다.")
                    continue
                
                print(f"\n총 {len(news_articles)}개의 뉴스를 수집했습니다.")
                
                # DataFrame으로 변환
                news_df = pd.DataFrame(news_articles)
                news_df['date'] = datetime.now()  # 현재 시간 추가
                
                # 뉴스 분석
                print("\n뉴스를 분석하고 있습니다...")
                analyzed_df = analyzer.analyze_news_data(news_df)
                
                # 투자 요약 생성
                summary = analyzer.generate_investment_summary(analyzed_df)
                print("\n=== 투자 분석 요약 ===")
                print(summary)
            
            except ValueError:
                print("올바른 숫자를 입력하세요.")
        
        elif choice == '3':
            print("\n프로그램을 종료합니다.")
            break
        
        else:
            print("\n올바른 선택지를 입력하세요.")

if __name__ == "__main__":
    main() 