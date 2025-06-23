import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.nodes.models import perplexity_sonar_small

from src.nodes.types import State
from src.prompts.collector_prompt import collector_prompt

def collector(state: State):
    try:
        print("#" * 80)

        prompt_template = collector_prompt()
        prompt = ChatPromptTemplate.from_template(prompt_template)

        # 빈 딕셔너리를 입력으로 제공 (입력 변수가 없으므로)
        output_parser = StrOutputParser()
        chain = prompt | perplexity_sonar_small | output_parser
        response = chain.invoke({})

        # ChatOpenAI returns AIMessage, so we need to extract the content
        result = response.content if hasattr(response, 'content') else str(response)

        print(f"collector: {result}")

        state["collected_data"] = result.strip()
        return state

    except Exception as e:
        print(f"Error in collector: {str(e)}")
        state["collected_data"] = ""
        return state