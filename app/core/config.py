from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from functools import lru_cache
from dotenv import load_dotenv



class Settings(BaseSettings):
    """
    Configuration settings for the AI Dermatology Assistant.
    Reads values from the environment using Pydantic.
    """

    # Project Settings
    PROJECT_NAME: str

    # API Keys
    GOOGLE_API_KEY: str

    # LangSmith Settings
    LANGSMITH_TRACING: bool
    LANGSMITH_ENDPOINT: AnyUrl
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str

    PORT: int = 8000    


    # SERVER_PORT: int


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    load_dotenv(override=True)
    return Settings()


settings = get_settings()