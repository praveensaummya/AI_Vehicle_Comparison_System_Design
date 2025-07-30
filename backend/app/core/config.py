# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM and Agent Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Tool Configuration
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

settings = Settings()

# It's a good practice to set the environment variable for CrewAI tools
os.environ["SERPER_API_KEY"] = settings.SERPER_API_KEY