import os
from src.nodes.models import gpt_fouro_mini as llm
from src.nodes.types import State
from src.prompts.analyzer_prompt import analyzer_prompt

def analyzer(state: State):
    try:
        # ✅ result status 확인해서 success가 아니면 실행하지 않음
        if state["collected_data"] == "":
            print("수집된 데이터가 없음 → analyzer 건너뜀")
            return state

        collected_data = state["collected_data"]

        # API 키가 없으면 모의 응답 반환
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  OpenAI API 키가 설정되지 않아 모의 분석 결과를 반환합니다.")
            mock_analysis = """
            시장 전망: 중립
            
            핵심 근거:
            1. 주요 지수들이 소폭 상승세를 보이고 있어 시장 심리가 안정적임
            2. 금리 정책이 현재 수준에서 유지될 것으로 예상되어 큰 변동성은 없을 것으로 판단
            3. 글로벌 경제 뉴스들이 혼재되어 있어 명확한 방향성을 제시하기 어려운 상황
            """
            state["analyzed_data"] = mock_analysis.strip()
            return state

        prompt_template = analyzer_prompt(collected_data)
        # print(prompt_template)
        respondent_llm = prompt_template | llm

        # 빈 딕셔너리를 입력으로 제공 (입력 변수가 없으므로)
        response = respondent_llm.invoke({})

        # ChatOpenAI returns AIMessage, so we need to extract the content. use just result when using another model
        analyzed_data = response.content if hasattr(response, 'content') else str(response)

        if not analyzed_data:
            return state.update({"analyzed_data": ""})

        state["analyzed_data"] = analyzed_data

        return state
    
    except Exception as e:
        print(f"Error in analyzer: {str(e)}")
        # 오류 발생 시에도 모의 분석 결과 반환
        mock_analysis = "API 호출 실패로 인한 모의 분석 결과입니다."
        state["analyzed_data"] = mock_analysis
        return state