import re
import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

def final_analyzer_prompt(scraped_data, analyzed_data, stock_data):
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

**2. 수집된 주식 뉴스:**
{scraped_data}

**3. 수집된 현재 주식 현황:**
{stock_data}
---

**4. 투자 전략 수립 및 주식 전망 제시 지침:**

* **뉴스 데이터 활용:**
    * 수집된 뉴스 데이터는 **감성 분석(긍정/부정)을 통해 주가에 미칠 영향을 평가**하고, 주요 키워드와 트렌드를 파악하여 분석에 적극 반영해주세요.

* **최종 투자 전략 제시:**
    * 전반적인 시장 상황(거시 경제, 섹터 트렌드)을 고려한 **종합적인 투자 전략 방향**을 제시해주세요.

* **개별 주식 전망 제시:**
    * 각 주식에 대해 **매수/유지/매도 의견**을 명확히 제시합니다.
    * 의견과 함께 **핵심적인 근거**를 명확하게 설명합니다. (예: 기업 실적 개선, 긍정적 뉴스 모멘텀, 수급 개선, 저평가, 신기술 개발 등)
    * 가능하다면 **구체적인 목표 가격** 또는 **예상 변동폭**을 제시하고, **산출 근거(예: PER 밴드 상단, PBR 적용, 과거 고점 돌파 가능성 등)를 간략하게 설명**해주세요.

---

**5. 최종 답변 형식:**

* 명확하고 간결한 문체로 작성해주세요.
* 전문 용어는 최소화하고 이해하기 쉽게 설명합니다.
* 결론적으로 어떤 주식에 어떤 전략으로 접근해야 할지 명확하게 제시하고, **투자 시 고려해야 할 잠재적 리스크**와 **대응 전략**도 간략하게 언급해주세요.
* **각 섹션별(시장 분석, 투자 전략, 개별 주식 전망)로 명확하게 구분하여 제시**해주세요.
    """

    partial_prompt = base_prompt.format(
        scraped_data=scraped_data,
        analyzed_data=analyzed_data,
        stock_data=stock_data
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=partial_prompt)
        ]
    )
    print("Final Analyzer Prompt 생성 완료")

    return prompt