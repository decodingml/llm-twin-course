import comet_llm
from settings import settings


class PromptMonitoringManager:
    @classmethod
    def log(
        cls,
        prompt: str,
        output: str,
        prompt_template: str | None = None,
        prompt_template_variables: dict | None = None,
        metadata: dict | None = None,
    ) -> None:
        comet_llm.init()

        metadata = metadata or {}
        metadata = {
            "model": settings.MODEL_TYPE,
            **metadata,
        }

        comet_llm.log_prompt(
            workspace=settings.COMET_WORKSPACE,
            project=f"{settings.COMET_PROJECT}-monitoring",
            api_key=settings.COMET_API_KEY,
            prompt=prompt,
            prompt_template=prompt_template,
            prompt_template_variables=prompt_template_variables,
            output=output,
            metadata=metadata,
        )
