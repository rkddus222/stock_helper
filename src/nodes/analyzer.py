import os
from src.nodes.models import gpt_fouro_mini as llm
from src.nodes.types import State
from src.prompts.analyzer_prompt import analyzer_prompt
from src.prompts.final_analyzer_prompt import final_analyzer_prompt

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
            return state

        prompt_template = analyzer_prompt(collected_data)
        # print(prompt_template)
        respondent_llm = prompt_template | llm

        # 빈 딕셔너리를 입력으로 제공 (입력 변수가 없으므로)
        response = respondent_llm.invoke({})

        # ChatOpenAI returns AIMessage, so we need to extract the content. use just result when using another model
        analyzed_data = response.content if hasattr(response, 'content') else str(response)

        if not analyzed_data:
            state["analyzed_data"] = ""
            return state

        state["analyzed_data"] = analyzed_data

        return state
    
    except Exception as e:
        print(f"Error in analyzer: {str(e)}")
        # 오류 발생 시에도 모의 분석 결과 반환
        mock_analysis = "API 호출 실패로 인한 모의 분석 결과입니다."
        state["analyzed_data"] = mock_analysis
        return state

def final_analyzer(state: State):
    try:
        # ✅ 수집된 데이터와 분석된 데이터가 없으면 실행하지 않음
        if state.get("scraped_data") == "" or state.get("analyzed_data") == "":
            print("수집된 데이터 또는 분석된 데이터가 없음 → final_analyzer 건너뜀")
            return state

        scraped_data = state["scraped_data"]
        analyzed_data = state["analyzed_data"]
        stock_data = state["stock_data"]

        # API 키가 없으면 모의 응답 반환
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  OpenAI API 키가 설정되지 않아 모의 최종 분석 결과를 반환합니다.")
            mock_final_analysis = """
            최종 시장 분석 보고서
            
            종합 평가: 긍정적
            
            주요 결론:
            1. 수집된 뉴스 데이터를 종합 분석한 결과, 전반적으로 긍정적인 시장 분위기
            2. 기술주 중심의 상승세가 지속될 것으로 예상
            3. 투자자들은 단기적 변동성보다는 중장기 성장성에 집중할 것을 권장
            
            투자 전략:
            - 분산 투자로 리스크 관리
            - 정기적인 포트폴리오 리밸런싱
            - 뉴스 모니터링 지속
            """
            state["final_analyzed_data"] = mock_final_analysis.strip()
            return state
        
        prompt_template = final_analyzer_prompt(analyzed_data, scraped_data, stock_data)
        respondent_llm = prompt_template | llm

        # 빈 딕셔너리를 입력으로 제공 (입력 변수가 없으므로)
        response = respondent_llm.invoke({})

        # ChatOpenAI returns AIMessage, so we need to extract the content
        final_analyzed_data = response.content if hasattr(response, 'content') else str(response)

        if not final_analyzed_data:
            state["final_analyzed_data"] = ""
            return state

        state["final_analyzed_data"] = final_analyzed_data

        print("=== 최종 분석 완료 ===")
        print(f"분석 결과 길이: {len(final_analyzed_data)} 문자")

        return state
    
    except Exception as e:
        print(f"Error in final_analyzer: {str(e)}")
        # 오류 발생 시에도 모의 분석 결과 반환
        mock_final_analysis = "최종 분석 중 오류가 발생하여 모의 분석 결과를 반환합니다."
        state["final_analyzed_data"] = mock_final_analysis
        return state
