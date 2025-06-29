from src.nodes.types import State
from src.service.mail_service import email_service

def email_sender(state: State):
    """
    최종 분석 결과를 이메일로 전송하는 노드
    """
    try:
        # 최종 분석 데이터가 없으면 실행하지 않음
        if not state.get("final_analyzed_data"):
            print("최종 분석 데이터가 없음 → 이메일 전송 건너뜀")
            return state
        
        final_analyzed_data = state["final_analyzed_data"]
        proposed_data = state.get("proposed_data", "")
        stock_data = state.get("stock_data", "")
        scraped_data = state.get("scraped_data", "")
        
        print("📧 이메일 전송을 시작합니다...")
        
        # 이메일 전송
        success = email_service.send_analysis_report(
            final_analyzed_data=final_analyzed_data,
            proposed_data=proposed_data,
            stock_data=stock_data,
            scraped_data=scraped_data
        )
        
        if success:
            print("✅ 이메일 전송이 완료되었습니다.")
            # 상태에 이메일 전송 완료 표시 추가
            state["email_sent"] = True
            state["email_sent_time"] = "성공"
        else:
            print("❌ 이메일 전송에 실패했습니다.")
            state["email_sent"] = False
            state["email_sent_time"] = "실패"
        
        return state
        
    except Exception as e:
        print(f"❌ 이메일 전송 중 오류 발생: {str(e)}")
        state["email_sent"] = False
        state["email_sent_time"] = f"오류: {str(e)}"
        return state 