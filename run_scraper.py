#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.investing_scraper import InvestingScraper

def main():
    print("Investing.com 주식 시장 뉴스 스크래핑을 시작합니다...")
    
    scraper = InvestingScraper()
    
    # 연결 테스트
    if not scraper.test_connection():
        print("웹사이트 연결에 실패했습니다.")
        return
    
    # 뉴스 목록 가져오기
    print("뉴스 목록을 가져오는 중...")
    news_list = scraper.get_news_list(max_pages=2)
    
    if news_list:
        print(f"총 {len(news_list)}개의 뉴스를 찾았습니다.")
        
        # CSV로 저장
        filename = scraper.save_to_csv(news_list)
        print(f"뉴스가 {filename}에 저장되었습니다.")
        
        # 처음 5개 뉴스 출력
        print("\n=== 최근 뉴스 미리보기 ===")
        for i, news in enumerate(news_list[:5], 1):
            print(f"{i}. {news.get('title', '제목 없음')}")
            print(f"   시간: {news.get('publish_time', '시간 정보 없음')}")
            print(f"   링크: {news.get('link', '링크 없음')}")
            if news.get('summary'):
                print(f"   요약: {news.get('summary', '')[:100]}...")
            print()
    else:
        print("뉴스를 찾을 수 없습니다.")

if __name__ == "__main__":
    main() 