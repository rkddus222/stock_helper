from src.nodes.types import State
from src.service.propose_scrapers.yuanta_propose import yuanta_scraper
from src.service.propose_scrapers.samsung_propose import samsung_scraper
from src.service.propose_scrapers.thinkpool_propose import thinkpool_scraper
from src.service.propose_scrapers.worldnews_propose import worldnews_scraper
from src.prompts.proposer_prompt import proposer_prompt
from src.nodes.models import gpt_fouro_mini as llm

def propose_scraper(state: State):
    try:
        print("🎯 추천 종목 및 뉴스 스크래핑을 시작합니다...")

        domestic_recommendations = []  # 국내 추천 종목
        overseas_recommendations = []  # 해외 추천 종목

        # 1. 유안타증권 추천 종목 스크래핑 (국내)
        print("📈 유안타증권 추천 종목 수집 중...")
        yuanta_stocks = yuanta_scraper.scrape_recommended_stocks()
        if yuanta_stocks:
            yuanta_formatted = yuanta_scraper.format_recommendations(yuanta_stocks)
            domestic_recommendations.append(yuanta_formatted)
            print(f"✅ 유안타증권: {len(yuanta_stocks)}개 종목 수집 완료")
        else:
            print("⚠️  유안타증권 추천 종목 수집 실패")

        # 2. 씽크풀 AI 종목 추천 스크래핑 (국내)
        print("🤖 씽크풀 AI 종목 추천 수집 중...")
        thinkpool_stocks = thinkpool_scraper.scrape_recommended_stocks()
        if thinkpool_stocks:
            thinkpool_formatted = thinkpool_scraper.format_recommendations(thinkpool_stocks)
            domestic_recommendations.append(thinkpool_formatted)
            print(f"✅ 씽크풀: {len(thinkpool_stocks)}개 종목 수집 완료")
        else:
            print("⚠️  씽크풀 AI 종목 추천 수집 실패")

        # 3. 삼성증권 해외 주식/ETF 추천 종목 스크래핑 (해외)
        print("🌍 삼성증권 해외 주식/ETF 추천 종목 수집 중...")
        samsung_stocks = samsung_scraper.scrape_recommended_stocks()
        if samsung_stocks:
            samsung_formatted = samsung_scraper.format_recommendations(samsung_stocks)
            overseas_recommendations.append(samsung_formatted)
            print(f"✅ 삼성증권: {len(samsung_stocks)}개 종목 수집 완료")
        else:
            print("⚠️  삼성증권 해외 주식/ETF 추천 종목 수집 실패")

        # 4. StockAnalysis.com 뉴스 스크래핑 (해외)
        print("📰 StockAnalysis.com 뉴스 수집 중...")
        worldnews_articles = worldnews_scraper.scrape_recommended_stocks()
        if worldnews_articles:
            worldnews_formatted = worldnews_scraper.format_recommendations(worldnews_articles)
            overseas_recommendations.append(worldnews_formatted)
            print(f"✅ StockAnalysis: {len(worldnews_articles)}개 뉴스 수집 완료")
        else:
            print("⚠️  StockAnalysis.com 뉴스 수집 실패")

        # 국내 추천 종목 결합
        if domestic_recommendations:
            combined_domestic = "\n\n" + "=" * 60 + "\n\n".join(domestic_recommendations)
            state["proposed_domestic_data"] = combined_domestic
            print("✅ 국내 추천 종목 수집 완료")
        else:
            state["proposed_domestic_data"] = "국내 추천 종목을 수집할 수 없습니다."
            print("❌ 국내 추천 종목 수집 실패")

        # 해외 추천 종목 및 뉴스 결합
        if overseas_recommendations:
            combined_overseas = "\n\n" + "=" * 60 + "\n\n".join(overseas_recommendations)
            state["proposed_worldwide_data"] = combined_overseas
            print("✅ 해외 추천 종목 및 뉴스 수집 완료")
        else:
            state["proposed_worldwide_data"] = "해외 추천 종목 및 뉴스를 수집할 수 없습니다."
            print("❌ 해외 추천 종목 및 뉴스 수집 실패")

        return state

    except Exception as e:
        print(f"❌ 추천 종목 및 뉴스 스크래핑 중 오류 발생: {str(e)}")
        state["proposed_domestic_data"] = f"국내 추천 종목 스크래핑 오류: {str(e)}"
        state["proposed_worldwide_data"] = f"해외 추천 종목 스크래핑 오류: {str(e)}"
        return state

def proposer(state: State):
    """
    추천 종목과 뉴스를 분석하는 노드
    """
    try:
        propose_scraper(state)

        # 기본값 설정
        proposed_domestic_data = state.get("proposed_domestic_data", "국내 추천 종목 데이터가 없습니다.")
        proposed_worldwide_data = state.get("proposed_worldwide_data", "해외 추천 종목 데이터가 없습니다.")

        if not proposed_domestic_data and not proposed_worldwide_data:
            print("수집된 데이터가 없음 → analyzer 건너뜀")
            state["proposed_data"] = "수집된 데이터가 없습니다."
            return state

        prompt_template = proposer_prompt(proposed_domestic_data, proposed_worldwide_data)
        # print(prompt_template)
        proposer_llm = prompt_template | llm

        # 빈 딕셔너리를 입력으로 제공 (입력 변수가 없으므로)
        response = proposer_llm.invoke({})

        # ChatOpenAI returns AIMessage, so we need to extract the content. use just result when using another model
        proposed_data = response.content if hasattr(response, 'content') else str(response)

        if not proposed_data:
            state["proposed_data"] = ""
            return state

        state["proposed_data"] = proposed_data

        return state

    except Exception as e:
        print(f"Error in analyzer: {str(e)}")
        # 오류 발생 시에도 기본값 설정
        state["proposed_data"] = f"분석 중 오류가 발생했습니다: {str(e)}"
        return state

if __name__ == "__main__":
    state = State()
    proposer(state)
    print(state["proposed_data"])