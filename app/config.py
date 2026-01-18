from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        env_file = ".env"
settings = Settings()