import re
import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

def final_analyzer_prompt(scraped_data, analyzed_data):
    """
    최종 분석을 위한 프롬프트 생성
    scraped_data: 수집된 뉴스 데이터
    analyzed_data: 이전 분석 결과
    """
    base_prompt = """
당신은 최고의 투자 전략가이자 시장 분석 전문가입니다.
제공된 시장 분석 결과와 개별 주식 데이터를 바탕으로 다음 지침에 따라 최종 투자 전략을 수립하고, 각각의 주식에 대한 구체적인 전망을 제시해주세요.

---

**1. 시장 분석 결과:**
{analyzed_data}

**2. 수집된 주식 데이터 (뉴스 포함):**
{scraped_data}

---

**3. 투자 전략 수립 및 주식 전망 제시 지침:**

* **투자 기간 및 스타일:** {예: 단기 (3개월 이내) 모멘텀 투자 / 중장기 (1년 이상) 가치 투자}
* **위험 허용 수준:** {예: 보수적 (안정성 우선) / 중립적 (적정 위험 추구) / 공격적 (고수익-고위험 감수)}
* **수익률 목표:** {예: 시장 평균 수익률 대비 5%p 초과 달성 / 연 15% 이상 수익률}
* **포트폴리오 구성 원칙 (선택 사항):** {예: 특정 섹터 집중 (예: 반도체, AI) / 업종 분산 / 대형주 위주}

* **뉴스 데이터 활용:**
    * 수집된 뉴스 데이터는 **감성 분석(긍정/부정)을 통해 주가에 미칠 영향을 평가**하고, 주요 키워드와 트렌드를 파악하여 분석에 적극 반영해주세요.

* **최종 투자 전략 제시:**
    * 전반적인 시장 상황(거시 경제, 섹터 트렌드)을 고려한 **종합적인 투자 전략 방향**을 제시해주세요.

* **개별 주식 전망 제시:**
    * 각 주식에 대해 **매수/유지/매도 의견**을 명확히 제시합니다.
    * 의견과 함께 **핵심적인 근거**를 명확하게 설명합니다. (예: 기업 실적 개선, 긍정적 뉴스 모멘텀, 수급 개선, 저평가 등)
    * 가능하다면 **구체적인 목표 가격** 또는 **예상 변동폭**을 제시해주세요.

---

**4. 최종 답변 형식:**

* 명확하고 간결한 문체로 작성해주세요.
* 전문 용어는 최소화하고 이해하기 쉽게 설명합니다.
* 결론적으로 어떤 주식에 어떤 전략으로 접근해야 할지 명확하게 제시해주세요.
    """

    partial_prompt = base_prompt.format(
        scraped_data=scraped_data,
        analyzed_data=analyzed_data
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=partial_prompt)
        ]
    )
    print("Final Analyzer Prompt 생성 완료")

    return prompt