#!/usr/bin/env python3
"""
Stock Helper - 주식 관련 도구

이 모듈은 주식 관련 기능을 제공하는 메인 애플리케이션입니다.
"""

import sys
import logging
from typing import Optional
from src.stock_summarizer import StockSummarizer
from src.stock_recommender import StockRecommender

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_stock_summary(symbols: Optional[list] = None) -> str:
    """
    주식 정보 요약을 가져오는 함수
    
    Args:
        symbols: 분석할 주식 심볼 리스트
        
    Returns:
        요약 텍스트
    """
    try:
        summarizer = StockSummarizer()
        summary = summarizer.get_daily_stock_summary(symbols)
        return summary
    except Exception as e:
        logger.error(f"주식 요약 생성 중 오류: {e}")
        return f"주식 정보 요약을 가져오는 중 오류가 발생했습니다: {e}"


def get_stock_recommendations(preference_type: str = "1") -> str:
    """
    주식 종목 추천을 가져오는 함수
    
    Args:
        preference_type: 선호사항 유형 ("1": 일반, "2": 배당주, "3": 성장주, "4": 테크주)
        
    Returns:
        추천 텍스트
    """
    try:
        recommender = StockRecommender()
        
        preferences = {
            "1": None,
            "2": "안정적인 배당주를 중심으로 추천해주세요. 배당 수익률이 높고 안정적인 기업들을 선호합니다.",
            "3": "고성장 기업들을 중심으로 추천해주세요. 매출과 이익이 빠르게 성장하는 기업들을 선호합니다.",
            "4": "기술주를 중심으로 추천해주세요. AI, 반도체, 소프트웨어 등 기술 관련 기업들을 선호합니다."
        }
        
        user_preference = preferences.get(preference_type)
        recommendation = recommender.get_stock_recommendations(user_preference)
        return recommendation
        
    except Exception as e:
        logger.error(f"주식 추천 생성 중 오류: {e}")
        return f"주식 종목 추천을 가져오는 중 오류가 발생했습니다: {e}"


def show_recommendation_menu() -> str:
    """
    추천 메뉴를 표시하고 사용자 선택을 받는 함수
    
    Returns:
        선택된 추천 유형
    """
    print("\n=== 추천 유형 선택 ===")
    print("1. 일반 추천 (시장 상황 기반)")
    print("2. 안정적인 배당주 추천")
    print("3. 고성장주 추천")
    print("4. 테크주 추천")
    print("5. 돌아가기")
    
    while True:
        choice = input("\n원하는 추천 유형을 선택하세요 (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        else:
            print("잘못된 선택입니다. 1-5 중에서 선택하세요.")


def main() -> None:
    """
    메인 함수 - 애플리케이션의 진입점
    """
    logger.info("Stock Helper 애플리케이션이 시작되었습니다.")
    
    try:
        print("=== Stock Helper ===")
        print("1. 오늘의 주식 정보 요약")
        print("2. 주식 종목 추천")
        print("3. 종료")
        
        while True:
            choice = input("\n원하는 기능을 선택하세요 (1-3): ").strip()
            
            if choice == "1":
                print("\n주식 정보 요약을 생성 중입니다...")
                summary = get_stock_summary()
                print("\n" + "="*50)
                print("오늘의 주식 정보 요약")
                print("="*50)
                print(summary)
                print("="*50)
                
            elif choice == "2":
                recommendation_type = show_recommendation_menu()
                
                if recommendation_type == "5":
                    continue
                
                print(f"\n주식 종목을 분석하고 추천을 생성 중입니다...")
                recommendation = get_stock_recommendations(recommendation_type)
                print("\n" + "="*60)
                print("주식 종목 추천")
                print("="*60)
                print(recommendation)
                print("="*60)
                
            elif choice == "3":
                print("Stock Helper를 종료합니다.")
                break
                
            else:
                print("잘못된 선택입니다. 1, 2 또는 3을 입력하세요.")
        
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 