import os
from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """ 
    Centralized Configuration Enginee created a object during startup
    Load, Parse and Validate ENvironment Variable for app

    """

    APP_NAME:str="Internal Candidate Scoreboard System"
    ENVIRONMENT:str=Field(default="production", env="APP_ENV")

    BACKEND_HOST: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    BACKEND_PORT: int = Field(default=8000, env="BACKEND_PORT")

    DATABASE_URL:str=Field("sqlite:///./techkraft.db", env="DATABASE_URL")
    GEMINI_API_KEY: str = Field(default="MOCK_API_KEY", alias="GEMINI_API_KEY")
    JWT_SECRET:str=Field(..., env="JWT_SECRET")
    JWT_ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=60

    model_config=SettingsConfigDict(env_file=".env",extra="ignore")


settings=Settings()
