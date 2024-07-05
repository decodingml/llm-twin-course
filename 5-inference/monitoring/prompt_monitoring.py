import comet_llm

from config import settings


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

    @classmethod
    def log_chain(cls, query: str, response: str, eval_output: str):
        comet_llm.init(project=f"{settings.COMET_PROJECT}-monitoring")
        comet_llm.start_chain(
            inputs={"user_query": query},
            project=f"{settings.COMET_PROJECT}-monitoring",
            api_key=settings.COMET_API_KEY,
            workspace=settings.COMET_WORKSPACE,
        )
        with comet_llm.Span(
            category="twin_response",
            inputs={"user_query": query},
        ) as span:
            span.set_outputs(outputs=response)

        with comet_llm.Span(
            category="gpt3.5-eval",
            inputs={"eval_result": eval_output},
        ) as span:
            span.set_outputs(outputs=response)
        comet_llm.end_chain(outputs={"response": response, "eval_output": eval_output})
