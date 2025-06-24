#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주식 뉴스 스크래퍼 실행 예제
환경변수에서 주식 리스트를 받아와서 네이버 주식 뉴스를 수집
"""

import os
from dotenv import load_dotenv
from src.nodes.scraper import StockNewsScraper

# 환경변수 로드
load_dotenv()

def main():
    """주식 뉴스 스크래퍼 실행"""
    
    # 환경변수에서 주식 리스트 확인
    stock_list_str = os.getenv("STOCK_LIST", "")
    
    if not stock_list_str:
        print("환경변수 STOCK_LIST가 설정되지 않았습니다.")
        print("\n.env 파일에 다음을 추가해주세요:")
        print("STOCK_LIST=005930,000660,035420,051910,006400")
        print("\n또는 직접 설정:")
        print("export STOCK_LIST=005930,000660,035420,051910,006400")
        return
    
    # 스크래퍼 초기화 및 실행
    scraper = StockNewsScraper()
    
    if not scraper.stock_list:
        print("주식 리스트를 로드할 수 없습니다.")
        return
    
    print("=== 주식 뉴스 스크래퍼 시작 ===")
    
    # 1. 모든 뉴스 수집
    print("\n1. 모든 뉴스 수집 중...")
    all_news = scraper.scrape_stock_news(
        keyword="",  # 빈 문자열이면 모든 뉴스
        max_count_per_stock=10
    )
    
    # 결과 출력
    scraper.print_summary(all_news)
    
    # 결과 저장
    filename = scraper.save_results(all_news)
    
    # 2. 특정 키워드로 필터링된 뉴스 수집 (예시)
    print("\n2. '실적' 키워드로 필터링된 뉴스 수집 중...")
    filtered_news = scraper.scrape_stock_news(
        keyword="실적",
        max_count_per_stock=5
    )
    
    # 필터링된 결과 출력
    scraper.print_summary(filtered_news)
    
    # 필터링된 결과 저장
    filtered_filename = scraper.save_results(filtered_news, "stock_news_filtered.json")
    
    print(f"\n=== 수집 완료 ===")
    print(f"전체 뉴스: {filename}")
    print(f"필터링된 뉴스: {filtered_filename}")

if __name__ == "__main__":
    main() 