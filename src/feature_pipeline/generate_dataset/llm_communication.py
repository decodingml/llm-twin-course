import json

from core import get_logger
from core.rag.llm_provider import get_model_id, get_openai_client

MAX_LENGTH = 16384
SYSTEM_PROMPT = (
    "You are a technical writer handing someone's account to post about AI and MLOps."
)

logger = get_logger(__name__)


class GptCommunicator:
    def __init__(self, gpt_model: str | None = None):
        self.gpt_model = gpt_model or get_model_id()

    def send_prompt(self, prompt: str) -> list:
        try:
            client = get_openai_client()
            logger.info(f"Sending batch to LLM = '{self.gpt_model}'.")

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt[:MAX_LENGTH]},
                ],
                model=self.gpt_model,
            )
            response = chat_completion.choices[0].message.content
            return json.loads(self.clean_response(response))
        except Exception:
            logger.exception(
                f"Skipping batch! An error occurred while communicating with API."
            )

            return []

    @staticmethod
    def clean_response(response: str) -> str:
        start_index = response.find("[")
        end_index = response.rfind("]")
        return response[start_index : end_index + 1]
