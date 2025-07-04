import os

from dotenv import load_dotenv
import json

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_perplexity import ChatPerplexity

gpt_fouro_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0, top_p=1)
gpt_fouro = ChatOpenAI(model="gpt-4o", temperature=0, top_p=1)

# Perplexity 모델들 (명시적으로 키 전달)
perplexity_sonar_small = ChatPerplexity(
    model="sonar-pro",
    temperature=0
)
perplexity_sonar_large = ChatPerplexity(
    model="llama-3.1-sonar-large-128k-online",
    temperature=0
)
# Gemini 모델들
gemini_pro = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, top_p=1)
gemini_pro_vision = ChatGoogleGenerativeAI(model="gemini-pro-vision", temperature=0, top_p=1)