# Stock Helper

주식 관련 도구를 제공하는 파이썬 프로젝트입니다.

## 주요 기능

- **오늘의 주식 정보 요약**: Perplexity LLM API를 사용하여 주요 주식들의 정보를 분석하고 요약
- **주식 종목 추천**: AI가 시장 상황을 분석하여 맞춤형 주식 종목을 추천
  - 일반 추천 (시장 상황 기반)
  - 안정적인 배당주 추천
  - 고성장주 추천
  - 테크주 추천
- 실시간 주식 데이터 수집 (yfinance 사용)
- 한국어로 된 이해하기 쉬운 분석 및 추천 제공

## 설치 방법

1. 저장소를 클론합니다:
```bash
git clone <repository-url>
cd stock_helper
```

2. 가상환경을 생성하고 활성화합니다:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 의존성을 설치합니다:
```bash
pip install -r requirements.txt
```

4. 환경 변수를 설정합니다:
```bash
# .env 파일을 생성하고 편집
copy env_example.txt .env
# 또는
cp env_example.txt .env
```

5. `.env` 파일을 편집하여 Perplexity API 키를 설정합니다:
```
PERPLEXITY_API_KEY=your_actual_api_key_here
```

## Perplexity API 키 발급

1. [Perplexity AI](https://www.perplexity.ai/)에 가입
2. API 키 발급 페이지에서 새 키 생성
3. `.env` 파일에 API 키 설정

## 사용 방법

### 대화형 모드
```bash
python main.py
```

### 직접 모듈 사용

#### 주식 정보 요약
```python
from src.stock_summarizer import StockSummarizer

summarizer = StockSummarizer()
summary = summarizer.get_daily_stock_summary()
print(summary)
```

#### 주식 종목 추천
```python
from src.stock_recommender import StockRecommender

recommender = StockRecommender()

# 일반 추천
recommendation = recommender.get_stock_recommendations()
print(recommendation)

# 배당주 추천
recommendation = recommender.get_stock_recommendations(
    "안정적인 배당주를 중심으로 추천해주세요."
)
print(recommendation)
```

## 추천 시스템 특징

### 분석 데이터
- **시장 지수**: S&P 500, Dow Jones, NASDAQ, VIX
- **섹터 성과**: 기술, 금융, 에너지, 헬스케어 등 10개 섹터
- **실시간 데이터**: yfinance를 통한 최신 시장 정보

### 추천 유형
1. **일반 추천**: 현재 시장 상황을 종합적으로 분석하여 추천
2. **배당주 추천**: 안정적인 배당 수익률을 제공하는 기업들
3. **성장주 추천**: 고성장 기업들을 중심으로 한 추천
4. **테크주 추천**: AI, 반도체, 소프트웨어 등 기술 관련 기업들

## 설정

### 기본 주식 심볼 변경
`.env` 파일에서 `DEFAULT_STOCK_SYMBOLS`를 수정하여 분석할 주식들을 변경할 수 있습니다:

```
DEFAULT_STOCK_SYMBOLS=AAPL,MSFT,GOOGL,TSLA,AMZN,NVDA,META
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 