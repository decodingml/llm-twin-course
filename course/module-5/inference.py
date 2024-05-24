import pandas as pd
from llm_components.prompt_templates import InferenceTemplateV1
from model_evaluation.evaluation import rag_eval_using_GPT
from model_evaluation.prompt_monitor import PromptMonitor
from qwak_inference import RealTimeClient
from rag.retriever import VectorRetriever
from settings import settings


class ModelInference:

    def __init__(self):
        self.qwak_client = RealTimeClient(
            model_id=settings.MODEL_ID, model_api=settings.MODEL_API
        )
        self.template = InferenceTemplateV1()
        self.prompt_monitor = PromptMonitor()

    def infer_only(self, query: str) -> dict:

        template = self.template.create_template()
        prompt = template.format(question=query)

        input_ = pd.DataFrame([{"instruction": prompt.strip()}]).to_json()

        response = self.qwak_client.predict(input_)

        return {"content": response}

    def generate_content(self, query: str) -> dict:
        retriever = VectorRetriever(query=query)
        hits = retriever.retrieve_top_k(
            k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY
        )
        context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)

        template = self.template.create_template()
        prompt = template.format(question=query, context=context)

        input_ = pd.DataFrame([{"instruction": prompt}]).to_json()

        response = self.qwak_client.predict(input_)
        evaluation = rag_eval_using_GPT(
            query=query, context=context, output=str(response)
        )

        self.prompt_monitor.log_prompt(
            prompt=prompt,
            prompt_template_variables={"question": query, "context": context},
            output=response,
        )

        return {"content": response, "evaluation": evaluation}
