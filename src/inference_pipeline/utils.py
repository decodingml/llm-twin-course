from transformers import AutoTokenizer

from config import settings


def compute_num_tokens(text: str) -> int:
    tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_ID)

    return len(tokenizer.encode(text, add_special_tokens=False))
