import time
from typing import List

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

    @classmethod
    def log_chain(
        cls,
        query: str,
        context: List[str],
        llm_gen: str,
        llm_eval_output: str,
        rag_eval_scores: dict | None = None,
        timings: dict | None = None,
    ) -> None:
        """Important!!
        Workaround to get timings/chain, is to time.sleep(timing) for each step!
        To be removed in production code.
        """
        comet_llm.init(project=f"{settings.COMET_PROJECT}-monitoring")
        comet_llm.start_chain(
            inputs={"user_query": query},
            project=f"{settings.COMET_PROJECT}-monitoring",
            api_key=settings.COMET_API_KEY,
            workspace=settings.COMET_WORKSPACE,
        )
        with comet_llm.Span(
            category="Vector Retrieval",
            name="retrieval_step",
            inputs={"user_query": query},
        ) as span:
            time.sleep(timings.get("retrieval"))
            span.set_outputs(outputs={"retrieved_context": context})

        with comet_llm.Span(
            category="LLM Generation",
            name="generation_step",
            inputs={"user_query": query},
        ) as span:
            time.sleep(timings.get("generation"))
            span.set_outputs(outputs={"generation": llm_gen})

        with comet_llm.Span(
            category="Evaluation",
            name="llm_eval_step",
            inputs={"query": llm_gen, "user_query": query},
            metadata={"model_used": settings.OPENAI_MODEL_ID},
        ) as span:
            time.sleep(timings.get("evaluation_llm"))
            span.set_outputs(outputs={"llm_eval_result": llm_eval_output})

        with comet_llm.Span(
            category="Evaluation",
            name="rag_eval_step",
            inputs={
                "user_query": query,
                "retrieved_context": context,
                "llm_gen": llm_gen,
            },
            metadata={
                "model_used": settings.OPENAI_MODEL_ID,
                "embd_model": settings.EMBEDDING_MODEL_ID,
                "eval_framework": "RAGAS",
            },
        ) as span:
            time.sleep(timings.get("evaluation_rag"))
            span.set_outputs(outputs={"rag_eval_scores": rag_eval_scores})
        comet_llm.end_chain(outputs={"response": llm_gen})
