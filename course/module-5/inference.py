from qwak.model.base import QwakModel
from qwak.model.tools import run_local

from pandas import DataFrame

from rag.retriever import VectorRetriever
from finetuning_model.model import CopywriterMistralModel
from llm_components.prompt_monitor import PromptMonitor
from llm_components.prompt_templates import InferenceTemplateV1

from settings import settings


class ModelInference:

    def __init__(self):
        self.model: QwakModel = CopywriterMistralModel()
        self.template = InferenceTemplateV1()
        self.prompt_monitor = PromptMonitor()

    def generate_content(self, query: str) -> str:
        retriever = VectorRetriever(query=query)
        hits = retriever.retrieve_top_k(k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY)
        context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)

        template = self.template.create_template()
        prompt = template.format(question=query,
                                 context=context)

        input_vector = DataFrame(
            [{
                'instruction': prompt
            }]
        ).to_json()
        result = run_local(self.model, input_vector)

        self.prompt_monitor.log_prompt(
            template=template,
            prompt=prompt,
            prompt_template_variables={'question': query, 'context': context},
            output=result
        )

        return result
