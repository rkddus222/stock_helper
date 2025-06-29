# Stock Helper

AI 기반 주식 시장 분석 도구입니다. 뉴스 데이터 수집, 주식 데이터 분석, 증권사 추천 종목 수집, 그리고 최종 분석 결과를 이메일로 전송하는 기능을 제공합니다.

## 주요 기능

- 📰 뉴스 데이터 수집 및 분석
- 📈 주식 데이터 스크래핑
- 🎯 증권사 추천 종목 수집
  - 유안타증권 국내 주식 추천 종목
  - 삼성증권 해외 주식/ETF 추천 종목
  - 씽크풀 AI 종목 추천
- 🤖 AI 기반 시장 분석
- 📧 분석 결과 이메일 전송

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env` 파일을 생성하고 다음 환경변수들을 설정하세요:

```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# 이메일 설정 (Gmail 사용 시)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=your_email@gmail.com
```

### 3. Gmail 앱 비밀번호 설정 (이메일 전송용)

1. Google 계정 설정에서 2단계 인증을 활성화하세요
2. 앱 비밀번호를 생성하세요:
   - Google 계정 → 보안 → 2단계 인증 → 앱 비밀번호
   - "메일" 앱을 선택하고 비밀번호를 생성
   - 생성된 16자리 비밀번호를 `SENDER_PASSWORD`에 설정

## 사용법

```bash
python main.py
```

## 워크플로우

1. **Collector**: 초기 데이터 수집
2. **Propose Scraper**: 증권사 추천 종목 수집
   - 유안타증권 국내 주식 추천 종목
   - 삼성증권 해외 주식/ETF 추천 종목
   - 씽크풀 AI 종목 추천
3. **Analyzer**: 수집된 데이터 분석
4. **News Scraper**: 뉴스 데이터 스크래핑
5. **Stock Scraper**: 주식 데이터 수집
6. **Final Analyzer**: 최종 종합 분석
7. **Email Sender**: 분석 결과 이메일 전송

## 수집되는 추천 종목 정보

### 유안타증권 (국내 주식)
- 종목명 및 종목코드
- 편입가, 현재가, 수익률
- 추천자 정보
- 상세 추천 이유

### 삼성증권 (해외 주식/ETF)
- 종목명 및 종목코드
- 시장 정보 (뉴욕 등)
- 현재가
- 추천일
- 수익률
- 추천 이유

### 씽크풀 (AI 종목 추천)
- 종목명 및 종목코드
- 기업 정보
- 관련 태그 (면세점, 엔터, NFT 등)
- AI 투자 포인트 분석

## 주의사항

- 이메일 전송을 위해서는 Gmail 계정과 앱 비밀번호가 필요합니다
- OpenAI API 키가 없으면 모의 분석 결과가 반환됩니다
- 웹 스크래핑은 해당 웹사이트의 이용약관을 준수하여 사용하세요
- 투자 결정 시 추가적인 검토를 권장합니다
