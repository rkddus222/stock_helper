from typing import TypedDict

# agent가 유지할 state를 정의
class State(TypedDict):
    collected_data: str
    market_preview: str
    analyzed_data: str
    stock_list: list
    scraped_data: str