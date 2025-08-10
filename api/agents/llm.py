from config.settings import settings
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

def get_llm():
    """Initialize LLM based on configuration"""
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0
        )

def get_llm_json():
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            response_format={"type": "json_object"},
        )
    else:
        return None


llm = get_llm()
llm_json = get_llm_json()
