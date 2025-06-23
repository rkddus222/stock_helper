from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import json # json 임포트는 필요 없지만, 기존 코드에 있었으니 일단 남겨둡니다.

class Settings(BaseSettings):
    """애플리케이션 설정"""

    # API 설정 (LangGraph에서 AI 모델을 사용할 때 필요)
    OPENAI_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")
    PERPLEXITY_API_KEY: str = Field(default="")

    # .env 파일 로드를 위한 설정 (필요시)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# 설정 인스턴스 생성
settings = Settings()