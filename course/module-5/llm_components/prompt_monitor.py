import comet_llm
from langchain.prompts import PromptTemplate

from settings import settings


class PromptMonitor:

    @classmethod
    def log_prompt(cls, template: PromptTemplate,
                   prompt: str,
                   prompt_template_variables: dict,
                   output: str):

        comet_llm.init()
        comet_llm.log_prompt(
            workspace=settings.COMET_WORKSPACE,
            project=settings.COMET_PROJECT,
            api_key=settings.COMET_API_KEY,
            prompt_template=template,
            prompt=prompt,
            prompt_template_variables=prompt_template_variables,
            output=output,
            metadata={
                'model': settings.MODEL_TYPE
            }
        )
