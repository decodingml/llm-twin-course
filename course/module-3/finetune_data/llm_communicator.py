import json

from openai import OpenAI

from finetune_data.exceptions import APICommunicationError
from settings import settings

MAX_LENGTH = 16384
SYSTEM_PROMPT = "You are a technical writer handing someone's account to post about AI and MLOps."


class GptCommunicator:
    def __init__(self, gpt_model: str = "gpt-3.5-turbo"):
        self.api_key = settings.OPENAI_API_KEY
        self.gpt_model = gpt_model

    def send_prompt(self, prompt: str) -> list:
        try:
            client = OpenAI(api_key=self.api_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt[:MAX_LENGTH]},
                ],
                model=self.gpt_model,
            )
            response = chat_completion.choices[0].message.content
            return json.loads(self.clean_response(response))
        except Exception as e:
            raise APICommunicationError(f"An error occurred while communicating with API: {e}")

    @staticmethod
    def clean_response(response: str) -> str:
        start_index = response.find("[")
        end_index = response.rfind("]")
        return response[start_index : end_index + 1]
