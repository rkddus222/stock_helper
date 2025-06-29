import re
import os
import json
from datetime import datetime
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

def proposer_prompt(proposed_domestic_data, proposed_worldwide_data):
    """
    추천 주식을 위한 프롬프트 생성
    proposed_data: 수집된 추천 데이터
    """
    base_prompt = """
당신은 수집된 데이터를 분석해서 주식 종목을 추천해주는 전문가 입니다.
수집된 데이터를 바탕으로 국내 주식과 해외 주식으로 나눠서 종목을 5개씩 추천해주세요.
주어진 주식 종목을 그대로 출력하는게 아닌 정말 매력적인 주식 종목 5개만 출력해주세요.
그리고 각 종목에 대해 추천 사유와 핵심 분석 내용을 3~5 문장으로 요약해서 설명해주세요.

1. 국내주식
수집된 국내 주식 종목 추천 데이터:
{proposed_domestic_data}

2. 해외주식
수집된 해외 주식 종목 추천 데이터:
{proposed_worldwide_data} 
    """

    partial_prompt = base_prompt.format(
        proposed_domestic_data=proposed_domestic_data,
        proposed_worldwide_data=proposed_worldwide_data
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=partial_prompt)
        ]
    )
    print("Proposer Prompt 생성 완료")

    return prompt