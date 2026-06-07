from langchain_openai import ChatOpenAI

from config import settings

# MiniMax API base URL (OpenAI-compatible)
MINIMAX_BASE_URL = "https://api.minimax.io/v1"


def get_chat_model(**kwargs) -> ChatOpenAI:
    """Create a ChatOpenAI instance based on the configured LLM provider.

    Supports 'openai' (default) and 'minimax' providers.
    MiniMax uses an OpenAI-compatible API, so we reuse ChatOpenAI
    with a custom base_url.
    """
    provider = getattr(settings, "LLM_PROVIDER", "openai").lower()

    if provider == "minimax":
        model_id = getattr(settings, "MINIMAX_MODEL_ID", "MiniMax-M3")
        api_key = getattr(settings, "MINIMAX_API_KEY", None)
        temperature = kwargs.pop("temperature", None)
        if temperature is not None:
            temperature = max(0.0, min(1.0, temperature))

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=MINIMAX_BASE_URL,
            temperature=temperature,
            **kwargs,
        )

    return ChatOpenAI(
        model=settings.OPENAI_MODEL_ID,
        api_key=settings.OPENAI_API_KEY,
        **kwargs,
    )
