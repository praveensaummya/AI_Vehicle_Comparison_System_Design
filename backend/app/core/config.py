# app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # gemini, openai, or mock
    
    # OpenAI Configuration (legacy support)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Gemini Configuration (primary)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Free tier model
    
    # Mock Mode Configuration (for testing without API calls)
    USE_MOCK_CREW = os.getenv("USE_MOCK_CREW", "false").lower() == "true"

    # Tool Configuration
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

settings = Settings()

# It's a good practice to set the environment variable for CrewAI tools
os.environ["SERPER_API_KEY"] = settings.SERPER_API_KEY