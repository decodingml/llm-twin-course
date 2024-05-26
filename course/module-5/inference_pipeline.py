import pandas as pd
from evaluation import evaluate_llm
from llm_components.prompt_templates import InferenceTemplate
from monitoring import PromptMonitoringManager
from qwak_inference import RealTimeClient
from rag.retriever import VectorRetriever
from settings import settings


class LLMTwin:
    def __init__(self) -> None:
        self.qwak_client = RealTimeClient(
            model_id=settings.QWAK_DEPLOYMENT_MODEL_ID,
            model_api=settings.QWAK_DEPLOYMENT_MODEL_API,
        )
        self.template = InferenceTemplate()
        self.prompt_monitoring_manager = PromptMonitoringManager()

    def generate(
        self,
        query: str,
        enable_rag: bool = False,
        enable_evaluation: bool = False,
        enable_monitoring: bool = True,
    ) -> dict:
        prompt_template = self.template.create_template(enable_rag=enable_rag)
        prompt_template_variables = {
            "question": query,
        }

        if enable_rag is True:
            retriever = VectorRetriever(query=query)
            hits = retriever.retrieve_top_k(
                k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY
            )
            context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)
            prompt_template_variables["context"] = context

            prompt = prompt_template.format(question=query, context=context)
        else:
            prompt = prompt_template.format(question=query)

        input_ = pd.DataFrame([{"instruction": prompt}]).to_json()

        response: list[dict] = self.qwak_client.predict(input_)
        answer = response[0]["content"][0]

        if enable_evaluation is True:
            evaluation_result = evaluate_llm(query=query, output=answer)
        else:
            evaluation_result = None

        if enable_monitoring is True:
            if evaluation_result is not None:
                metadata = {"llm_evaluation_result": evaluation_result}
            else:
                metadata = None

            self.prompt_monitoring_manager.log(
                prompt=prompt,
                prompt_template=prompt_template.template,
                prompt_template_variables=prompt_template_variables,
                output=answer,
                metadata=metadata,
            )
            self.prompt_monitoring_manager.log_chain(
                query=query, response=answer, eval_output=evaluation_result
            )

        return {"answer": answer, "llm_evaluation_result": evaluation_result}
