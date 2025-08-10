import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Database Settings
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/finance_db")
    
    # Flask Settings
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Redis
    REDIS_HOST=os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT=os.getenv("REDIS_PORT", 6379)
    REDIS_DB=os.getenv("REDIS_DB", 0)
    REDIS_PASSWORD=os.getenv("REDIS_PASSWORD")
    REDIS_TTL=os.getenv("REDIS_TTL", 300)
    REDIS_NAMESPACE=os.getenv("REDIS_NAMESPACE", "finance_agent")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings"""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

settings = Settings()