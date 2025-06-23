import re
import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

def analyzer_prompt(collected_data):
    base_prompt = """
    목표: 수집된 데이터를 바탕으로 현재 시장의 전반적인 분위기와 방향성을 분석하고, 명확한 시장 전망을 도출합니다.

    수집된 데이터: {collected_data}
    
    지시사항:
    거시 경제 지표 분석: 입력된 시장 지수, 환율, 금리, 원자재 가격 데이터를 종합하여 현재 거시 경제 상황이 주식 시장에 미치는 영향을 분석해 주세요.
    뉴스 분석: 수집된 최신 경제 뉴스를 바탕으로 현재 시장에 긍정적/부정적 영향을 미칠 수 있는 주요 이슈들을 파악하고 그 중요도를 평가해 주세요.
    시장 전망 도출: 위 분석 결과를 종합하여 현재 주식 시장의 전반적인 시장 전망을 다음 세 가지 중 하나로 명확히 제시해 주세요.
    긍정 (Bullish): 전반적인 상승세가 예상되거나 투자 환경이 우호적임.
    중립 (Neutral): 특별한 방향성 없이 관망세가 예상되거나 상승/하락 요인이 혼재함.
    부정 (Bearish): 전반적인 하락세가 예상되거나 투자 환경이 비우호적임.
    전망 근거: 도출된 시장 전망에 대한 핵심 근거 2~3가지를 간략하게 설명해 주세요.
    
    출력 형식:
    시장 전망: [긍정/중립/부정]
    핵심 근거:
    [근거 1]
    [근거 2]
    ... (필요 시 추가)
"""

    partial_prompt = base_prompt.format(
        collected_data=collected_data
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=partial_prompt)
        ]
    )
    print(prompt)

    return prompt