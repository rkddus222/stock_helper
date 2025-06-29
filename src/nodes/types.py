from typing import TypedDict

# agent가 유지할 state를 정의
class State(TypedDict):
    collected_data: str
    analyzed_data: str
    stock_list_domestic: list
    stock_list_worldwide: list
    scraped_data: str
    stock_data: str
    final_analyzed_data: str
    proposed_domestic_data: str
    proposed_worldwide_data: str
    proposed_data: str
    email_sent: bool
    email_sent_time: str