from langchain_openai import ChatOpenAI
from openai import OpenAI

from config import settings

# MiniMax API base URL (OpenAI-compatible)
MINIMAX_BASE_URL = "https://api.minimax.io/v1"


def get_chat_model(**kwargs) -> ChatOpenAI:
    """Create a ChatOpenAI instance based on the configured LLM provider.

    Supports 'openai' (default) and 'minimax' providers.
    MiniMax uses an OpenAI-compatible API, so we reuse ChatOpenAI
    with a custom base_url.

    Args:
        **kwargs: Additional keyword arguments passed to ChatOpenAI
            (e.g., temperature, max_tokens).

    Returns:
        A configured ChatOpenAI instance.
    """
    provider = getattr(settings, "LLM_PROVIDER", "openai").lower()

    if provider == "minimax":
        model_id = getattr(settings, "MINIMAX_MODEL_ID", "MiniMax-M3")
        api_key = getattr(settings, "MINIMAX_API_KEY", None)
        temperature = kwargs.pop("temperature", None)
        # MiniMax accepts temperature in [0, 1.0]
        if temperature is not None:
            temperature = max(0.0, min(1.0, temperature))

        return ChatOpenAI(
            model=model_id,
            api_key=api_key,
            base_url=MINIMAX_BASE_URL,
            temperature=temperature,
            **kwargs,
        )

    # Default: OpenAI
    return ChatOpenAI(
        model=settings.OPENAI_MODEL_ID,
        api_key=settings.OPENAI_API_KEY,
        **kwargs,
    )


def get_openai_client() -> OpenAI:
    """Create an OpenAI client based on the configured LLM provider.

    Returns an OpenAI SDK client configured for either OpenAI or MiniMax.
    MiniMax's API is OpenAI-compatible, so we reuse the OpenAI client
    with a custom base_url.

    Returns:
        A configured OpenAI client instance.
    """
    provider = getattr(settings, "LLM_PROVIDER", "openai").lower()

    if provider == "minimax":
        api_key = getattr(settings, "MINIMAX_API_KEY", None)
        return OpenAI(api_key=api_key, base_url=MINIMAX_BASE_URL)

    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_model_id() -> str:
    """Return the model ID for the current LLM provider."""
    provider = getattr(settings, "LLM_PROVIDER", "openai").lower()
    if provider == "minimax":
        return getattr(settings, "MINIMAX_MODEL_ID", "MiniMax-M3")
    return settings.OPENAI_MODEL_ID
