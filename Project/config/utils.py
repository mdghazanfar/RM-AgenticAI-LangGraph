from typing import Optional, Literal
from config.logging_config import get_logger
from config.settings import get_settings

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

logger = get_logger("config.utils")

def get_gemini_model(

    model: Literal[
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-3.0-flash-preview",
    ] = "gemini-2.5-flash",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
):
    """
    Initialize and return a ChatGoogleGenerativeAI model.
    """
    settings = get_settings()
    
    if not ChatGoogleGenerativeAI:
        logger.error("langchain-google-genai is not installed/imported.")
        return None
        
    if not settings.gemini_api_key:
        logger.warning("gemini_api_key is not set in configuration.")
        return None

    try:
        temp = temperature if temperature is not None else settings.default_temperature
        tokens = max_tokens if max_tokens is not None else settings.max_tokens

        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.gemini_api_key,
            temperature=temp,
            max_tokens=tokens
        )
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Gemini LLM ({model}): {e}")
        return None