from config import settings
from transformers import AutoTokenizer


def compute_num_tokens(text: str) -> int:
    tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_ID)

    return len(tokenizer.encode(text, add_special_tokens=False))


def truncate_text_to_max_tokens(text: str, max_tokens: int) -> tuple[str, int]:
    """Truncates text to not exceed max_tokens while trying to preserve complete sentences.

    Args:
        text: The text to truncate
        max_tokens: Maximum number of tokens allowed

    Returns:
        Truncated text that fits within max_tokens and the number of tokens in the truncated text.
    """

    current_tokens = compute_num_tokens(text)

    if current_tokens <= max_tokens:
        return text, current_tokens

    tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_ID)
    tokens = tokenizer.encode(text, add_special_tokens=False)

    # Take first max_tokens tokens and decode
    truncated_tokens = tokens[:max_tokens]
    truncated_text = tokenizer.decode(truncated_tokens)

    # Try to end at last complete sentence
    last_period = truncated_text.rfind(".")
    if last_period > 0:
        truncated_text = truncated_text[: last_period + 1]

    truncated_tokens = compute_num_tokens(truncated_text)

    return truncated_text, truncated_tokens
