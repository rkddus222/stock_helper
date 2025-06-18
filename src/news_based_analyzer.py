"""
뉴스 기반 주식 분석 모듈

네이버 금융 뉴스를 기반으로 주식 시장을 분석하고 추천합니다.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import yfinance as yf
from dotenv import load_dotenv
from scrapers.naver_scraper import scrape_naver_finance_news_titles
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import json

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)


class NewsBasedAnalyzer:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # NLTK 데이터 다운로드
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.sia = SentimentIntensityAnalyzer()
        
    def analyze_sentiment(self, text):
        """뉴스 텍스트의 감성 분석"""
        scores = self.sia.polarity_scores(text)
        return scores['compound']  # -1(부정) ~ 1(긍정)
        
    def analyze_news_data(self, news_df):
        """뉴스 데이터 분석"""
        if news_df.empty:
            return pd.DataFrame()
            
        print("감성 분석을 시작합니다...")
        # 제목만 있으므로 제목을 content로 사용하여 감성 분석
        news_df['sentiment_score'] = news_df['title'].apply(self.analyze_sentiment)
        print("감성 분석 완료!")
        
        print("AI 종합 분석을 시작합니다...")
        
        # 모든 기사 제목을 모아서 한 번에 분석
        all_titles = "\n".join([f"{i+1}. {title}" for i, title in enumerate(news_df['title'])])
        
        comprehensive_prompt = f"""
        다음은 오늘의 주요 금융 뉴스 제목들입니다:
        
        {all_titles}
        
        이 뉴스들을 종합적으로 분석하여 다음 사항들을 포함한 투자 시사점을 제시해주세요:
        
        1. 전반적인 시장 분위기와 주요 이슈
        2. 주목해야 할 업종이나 종목
        3. 투자자들이 유의해야 할 점
        4. 시장 전망 및 투자 전략 제안
        
        8-10문장으로 상세히 분석해주세요.
        """
        
        try:
            print("  종합 AI 분석 요청 중...")
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 금융 뉴스를 종합적으로 분석하고 투자 시사점을 도출하는 전문가입니다. 주식 시장과 경제 동향에 대한 깊은 이해를 바탕으로 실용적인 투자 조언을 제공합니다."
                    },
                    {
                        "role": "user",
                        "content": comprehensive_prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                comprehensive_analysis = result['choices'][0]['message']['content']
                print("  종합 AI 분석 완료!")
                
                # 모든 기사에 동일한 종합 분석 결과 적용
                news_df['ai_analysis'] = comprehensive_analysis
                
            else:
                print(f"  종합 분석 API 요청 실패: {response.status_code}")
                print(f"  응답 내용: {response.text}")
                news_df['ai_analysis'] = "AI 분석 실패"
        
        except Exception as e:
            print(f"  종합 분석 중 오류 발생: {e}")
            news_df['ai_analysis'] = "AI 분석 실패"
        
        print("AI 분석 완료!")
        return news_df
        
    def _get_ai_analysis(self, title, content):
        """개별 뉴스 분석 (현재는 사용하지 않음)"""
        return "개별 분석은 현재 사용하지 않습니다. 종합 분석을 참조하세요."
            
    def get_stock_data(self, symbol, days=30):
        """주식 데이터 가져오기"""
        try:
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            df = stock.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"주식 데이터 조회 중 오류 발생: {e}")
            return pd.DataFrame()
            
    def find_similar_news(self, target_news, news_df, n=3):
        """유사한 뉴스 찾기"""
        if news_df.empty:
            return pd.DataFrame()
            
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(news_df['title'])
        
        target_vector = vectorizer.transform([target_news])
        similarities = cosine_similarity(target_vector, tfidf_matrix)
        
        similar_indices = similarities[0].argsort()[-n:][::-1]
        return news_df.iloc[similar_indices]
        
    def generate_investment_summary(self, news_df):
        """투자 관련 요약 생성"""
        if news_df.empty:
            return "분석할 뉴스가 없습니다."
            
        print("투자 요약 생성을 시작합니다...")
        
        # 감성 점수 평균
        avg_sentiment = news_df['sentiment_score'].mean()
        
        # 가장 긍정적/부정적인 뉴스
        most_positive = news_df.loc[news_df['sentiment_score'].idxmax()]
        most_negative = news_df.loc[news_df['sentiment_score'].idxmin()]
        
        # 이미 완료된 AI 종합 분석 사용
        ai_summary = news_df['ai_analysis'].iloc[0] if not news_df.empty else "AI 분석 없음"
        
        summary = f"""
        뉴스 분석 요약:
        
        전체 감성 지수: {avg_sentiment:.2f} (-1: 매우 부정적, 1: 매우 긍정적)
        
        주목할 만한 긍정적 뉴스:
        - {most_positive['title']}
        - 감성 지수: {most_positive['sentiment_score']:.2f}
        
        주의해야 할 부정적 뉴스:
        - {most_negative['title']}
        - 감성 지수: {most_negative['sentiment_score']:.2f}
        
        AI 종합 분석:
        {ai_summary}
        """
        
        print("투자 요약 생성 완료!")
        return summary


def main():
    """테스트용 메인 함수"""
    try:
        analyzer = NewsBasedAnalyzer()
        
        print("=== 뉴스 기반 주식 분석 시스템 ===")
        print("테스트를 위해 간단한 뉴스 분석을 수행합니다...")
        
        # 테스트용 뉴스 데이터
        test_news = pd.DataFrame({
            'title': ['테스트 뉴스 제목'],
            'content': ['테스트 뉴스 내용입니다.'],
            'date': [datetime.now()],
            'url': ['http://test.com']
        })
        
        # 분석 수행
        result = analyzer.analyze_news_data(test_news)
        print("분석 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    main() 