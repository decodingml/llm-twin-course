import pprint

import opik
import sagemaker
from config import settings
from core import logger_utils
from core.opik_utils import add_to_dataset_with_sampling
from core.rag.retriever import VectorRetriever
from langchain.prompts import PromptTemplate
from opik import opik_context
from prompt_templates import InferenceTemplate
from sagemaker.huggingface.model import HuggingFacePredictor
from utils import compute_num_tokens, truncate_text_to_max_tokens

logger = logger_utils.get_logger(__name__)


class LLMTwin:
    def __init__(self, mock: bool = False) -> None:
        self._mock = mock
        self._llm_endpoint = self.build_sagemaker_predictor()
        self.prompt_template_builder = InferenceTemplate()

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
        system_prompt, prompt_template = self.prompt_template_builder.create_template(
            enable_rag=enable_rag
        )
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

        messages, input_num_tokens = self.format_prompt(
            system_prompt, prompt_template, prompt_template_variables
        )

        logger.debug(f"Prompt: {pprint.pformat(messages)}")
        answer = self.call_llm_service(messages=messages)
        logger.debug(f"Answer: {answer}")

        num_answer_tokens = compute_num_tokens(answer)
        opik_context.update_current_trace(
            tags=["rag"],
            metadata={
                "prompt_template": prompt_template.template,
                "prompt_template_variables": prompt_template_variables,
                "model_id": settings.MODEL_ID,
                "embedding_model_id": settings.EMBEDDING_MODEL_ID,
                "input_tokens": input_num_tokens,
                "answer_tokens": num_answer_tokens,
                "total_tokens": input_num_tokens + num_answer_tokens,
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
        self,
        system_prompt,
        prompt_template: PromptTemplate,
        prompt_template_variables: dict,
    ) -> tuple[list[dict[str, str]], int]:
        prompt = prompt_template.format(**prompt_template_variables)

        num_system_prompt_tokens = compute_num_tokens(system_prompt)
        prompt, prompt_num_tokens = truncate_text_to_max_tokens(
            prompt, max_tokens=settings.MAX_INPUT_TOKENS - num_system_prompt_tokens
        )
        total_input_tokens = num_system_prompt_tokens + prompt_num_tokens

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        return messages, total_input_tokens

    @opik.track(name="inference_pipeline.call_llm_service")
    def call_llm_service(self, messages: list[dict[str, str]]) -> str:
        if self._mock is True:
            logger.warning("Mocking LLM service call.")

            return "Mocked answer."

        answer = self._llm_endpoint.predict(
            data={
                "messages": messages,
                "parameters": {
                    "max_new_tokens": settings.MAX_TOTAL_TOKENS
                    - settings.MAX_INPUT_TOKENS,
                    "temperature": 0.01,
                    "top_p": 0.6,
                    "stop": ["<|eot_id|>"],
                    "return_full_text": False,
                },
            }
        )
        answer = answer["choices"][0]["message"]["content"].strip()

        return answer
