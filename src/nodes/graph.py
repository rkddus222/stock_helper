from langgraph.graph import END, StateGraph, START

from src.nodes.news_scraper import news_scraper
from src.nodes.stock_scraper import stock_scraper
from src.nodes.types import State
from src.nodes.collector import collector
from src.nodes.analyzer import analyzer

class LangGraphManager:
    def __init__(self):
        self.graph = None

    def initialize_graph(self):

        graph = StateGraph(State)

        graph.add_node("collector", collector)
        graph.add_node("analyzer", analyzer)
        graph.add_node("news_scraper", news_scraper)
        
        graph.set_entry_point("collector")

        graph.add_edge(START, "collector")
        graph.add_edge("collector", "analyzer")
        graph.add_edge("analyzer", "news_scraper")
        graph.add_edge("news_scraper", "stcok_scraper")
        # graph.add_conditional_edges(
        #     "executor",
        #     lambda x: (
        #         "executor_like" if x["query_result_status"] == "need_like_query" else
        #         "respondent"
        #     ),
        #     {
        #         "executor_like": "executor_like",
        #         "respondent": "respondent"
        #     }
        # )
        self.graph = graph.compile()
        return self.graph