from langgraph.graph import END, StateGraph, START

from src.nodes.news_scraper import news_scraper
from src.nodes.stock_scraper import stock_scraper
from src.nodes.types import State
from src.nodes.collector import collector
from src.nodes.analyzer import analyzer, final_analyzer
from src.nodes.email_sender import email_sender
from src.nodes.proposer import proposer

class LangGraphManager:
    def __init__(self):
        self.graph = None

    def initialize_graph(self):

        graph = StateGraph(State)

        graph.add_node("collector", collector)
        graph.add_node("analyzer", analyzer)
        graph.add_node("news_scraper", news_scraper)
        graph.add_node("stock_scraper", stock_scraper)
        graph.add_node("final_analyzer", final_analyzer)
        graph.add_node("proposer", proposer)
        graph.add_node("email_sender", email_sender)

        graph.set_entry_point("collector")

        graph.add_edge(START, "collector")
        graph.add_edge("collector", "analyzer")
        graph.add_edge("analyzer", "news_scraper")
        graph.add_edge("news_scraper", "stock_scraper")
        graph.add_edge("stock_scraper", "final_analyzer")
        graph.add_edge("final_analyzer", "proposer")
        graph.add_edge("proposer", "email_sender")
        graph.add_edge("email_sender", END)

        self.graph = graph.compile()
        return self.graph