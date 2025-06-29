import asyncio
import os
from src.nodes.graph import LangGraphManager  # LangGraphManager가 있는 파일 경로


def check_api_keys():
    """API 키들이 설정되어 있는지 확인"""
    required_keys = ['OPENAI_API_KEY', 'GOOGLE_API_KEY', 'PPLX_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    return missing_keys


async def run_langgraph_initialization():
    """LangGraph를 초기화하고 실행하는 함수"""
    try:
        print("=== LangGraph 초기화 시작 ===")

        # API 키 확인
        missing_keys = check_api_keys()
        if missing_keys:
            print(f"⚠️  다음 API 키들이 설정되지 않았습니다: {', '.join(missing_keys)}")
            print("API 키 없이 테스트 모드로 실행합니다...")
            print("실제 LLM 호출은 실패할 수 있지만, LangGraph 구조는 테스트할 수 있습니다.")

        # 이메일 설정 확인
        email_keys = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL']
        missing_email_keys = [key for key in email_keys if not os.getenv(key)]
        if missing_email_keys:
            print(f"⚠️  이메일 설정이 완료되지 않았습니다: {', '.join(missing_email_keys)}")
            print("이메일 전송 기능은 비활성화됩니다.")

        # LangGraphManager 인스턴스 생성
        graph_manager = LangGraphManager()

        # 그래프 초기화 및 컴파일
        compiled_graph = graph_manager.initialize_graph()

        print("LangGraph 초기화 및 컴파일 완료.")

        # 초기 상태 설정 (새로운 구조에 맞춰 업데이트)
        initial_state = {
            "collected_data": "",
            "analyzed_data": "",
            "scraped_data": "",
            "stock_data": "",
            "final_analyzed_data": "",
            "proposed_data": "",
            "stock_list_domestic": [],
            "stock_list_worldwide": [],
            "email_sent": False,
            "email_sent_time": ""
        }

        print("=== LangGraph 실행 시작 ===")
        
        # 컴파일된 그래프 실행
        result = compiled_graph.invoke(initial_state)
        
        print("=== LangGraph 실행 완료 ===")
        print("\n=== 최종 분석 결과 ===")
        print(result.get('final_analyzed_data', '분석 결과가 없습니다.'))
        
        print("\n=== 추천 종목 정보 ===")
        proposed_data = result.get('proposed_data', '추천 종목 정보가 없습니다.')
        print(proposed_data)
        
        print("\n=== 이메일 전송 상태 ===")
        email_sent = result.get('email_sent', False)
        email_sent_time = result.get('email_sent_time', '알 수 없음')
        if email_sent:
            print(f"✅ 이메일 전송 성공: {email_sent_time}")
        else:
            print(f"❌ 이메일 전송 실패: {email_sent_time}")

    except Exception as e:
        print(f"LangGraph 초기화 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_langgraph_initialization())
    print("\n=== LangGraph 초기화 프로세스 종료 ===")