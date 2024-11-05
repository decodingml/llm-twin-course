import opik
import sagemaker
from core import logger_utils
from core.opik_utils import add_to_dataset_with_sampling
from langchain.prompts import PromptTemplate
from opik import opik_context
from sagemaker.huggingface.model import HuggingFacePredictor

from config import settings
from inference_pipeline.prompt_templates import InferenceTemplate
from core.rag.retriever import VectorRetriever
from utils import misc

logger = logger_utils.get_logger(__name__)


class LLMTwin:
    def __init__(self, mock: bool = False) -> None:
        self._mock = mock
        self._llm_endpoint = self.build_sagemaker_predictor()
        self.template = InferenceTemplate()

    def build_sagemaker_predictor(self) -> HuggingFacePredictor:
        return HuggingFacePredictor(
            endpoint_name=settings.DEPLOYMENT_ENDPOINT_NAME,
            sagemaker_session=sagemaker.Session(),
        )

    @opik.track(name="inference_pipeline.generate")
    def generate(
        self,
        query: str,
        enable_rag: bool = False,
        sample_for_evaluation: bool = False,
    ) -> dict:
        prompt_template = self.template.create_template(enable_rag=enable_rag)
        prompt_template_variables = {"question": query}

        if enable_rag is True:
            retriever = VectorRetriever(query=query)
            hits = retriever.retrieve_top_k(
                k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY
            )
            context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)
            prompt_template_variables["context"] = context
        else:
            context = None

        prompt = self.format_prompt(prompt_template, prompt_template_variables)

        logger.debug(f"Prompt: {prompt}")
        answer = self.call_llm_service(prompt=prompt)
        logger.debug(f"Answer: {answer}")

        num_prompt_tokens = misc.compute_num_tokens(prompt)
        num_answer_tokens = misc.compute_num_tokens(answer)
        opik_context.update_current_trace(
            tags=["rag"],
            metadata={
                "prompt_template": prompt_template.template,
                "prompt_template_variables": prompt_template_variables,
                "model_id": settings.MODEL_ID,
                "embedding_model_id": settings.EMBEDDING_MODEL_ID,
                "prompt_tokens": num_prompt_tokens,
                "answer_tokens": num_answer_tokens,
                "total_tokens": num_prompt_tokens + num_answer_tokens,
            },
        )

        answer = {"answer": answer, "context": context}
        if sample_for_evaluation is True:
            add_to_dataset_with_sampling(
                item={"input": {"query": query}, "expected_output": answer},
                dataset_name="LLMTwinMonitoringDataset",
            )

        return answer

    @opik.track(name="inference_pipeline.format_prompt")
    def format_prompt(
        self, prompt_template: PromptTemplate, prompt_template_variables: dict
    ) -> str:
        prompt = prompt_template.format(**prompt_template_variables)

        return prompt

    @opik.track(name="inference_pipeline.call_llm_service")
    def call_llm_service(self, prompt: str) -> str:
        if self._mock is True:
            logger.warning("Mocking LLM service call.")

            return "Mocked answer."

        answer = self._llm_endpoint.predict(
            {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 256,
                    "temperature": 0.01,
                    "top_p": 0.9,
                    "return_full_text": False,
                },
            }
        )
        answer = answer[0]["generated_text"]

        return answer
