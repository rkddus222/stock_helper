# 중소형주 뉴스 기반 투자 분석 시스템

이 프로젝트는 네이버 금융 뉴스를 스크래핑하여 대형주를 제외한 중소형주 관련 뉴스를 분석하고, 투자 의사결정에 도움을 주는 시스템입니다.

## 주요 기능

1. 중소형주 관련 뉴스 스크래핑
   - 네이버 금융 뉴스에서 대형주 관련 뉴스를 제외하고 수집
   - 설정 가능한 기간 동안의 뉴스 수집

2. 뉴스 분석
   - 감성 분석 (긍정/부정)
   - Perplexity API를 활용한 AI 기반 뉴스 분석
   - 유사 뉴스 검색

3. 투자 분석
   - 뉴스 기반 투자 시사점 도출
   - 종합 투자 분석 리포트 생성
   - 분석 결과 CSV 파일 저장

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/stock_helper.git
cd stock_helper
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
- `.env` 파일을 생성하고 다음 내용을 추가:
```
PERPLEXITY_API_KEY=your_api_key_here
```

## 사용 방법

1. 프로그램 실행
```bash
python main.py
```

2. 메뉴 선택
- 1: 최신 뉴스 수집 및 분석
- 2: 특정 기간 뉴스 분석
- 3: 종료

3. 분석 결과
- 분석이 완료되면 투자 분석 요약이 표시됩니다.
- 결과를 CSV 파일로 저장할 수 있습니다.

## 주의사항

1. API 키
- Perplexity API 키가 필요합니다.
- API 키는 절대로 공개 저장소에 커밋하지 마세요.

2. 뉴스 스크래핑
- 네이버 금융의 robots.txt를 준수합니다.
- 과도한 요청을 피하기 위해 적절한 간격을 두고 스크래핑합니다.

3. 투자 주의
- 이 시스템의 분석 결과는 참고용입니다.
- 실제 투자는 충분한 검토와 판단 후에 진행하세요.

## 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요. 