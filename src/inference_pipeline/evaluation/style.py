import json
from typing import Any

from config import settings
from opik.evaluation.metrics import base_metric, exceptions, score_result
from opik.evaluation.models import litellm_chat_model
from pydantic import BaseModel


class LLMJudgeStyleOutputResult(BaseModel):
    score: int
    reason: str


class Style(base_metric.BaseMetric):
    """
    A metric that evaluates whether an LLM's output tone and writing style are appropriate for a blog post or social media content.

    This metric uses another LLM to judge if the output is factual or contains hallucinations.
    It returns a score of 1.0 if the style is appropriate, 0.5 if it is somewhere in the middle and 0.0 otherwise.
    """

    def __init__(
        self, name: str = "style_metric", model_name: str = settings.OPENAI_MODEL_ID
    ) -> None:
        self.name = name
        self.llm_client = litellm_chat_model.LiteLLMChatModel(model_name=model_name)
        self.prompt_template = """
        You are an impartial expert judge. Evaluate the quality of a given answer to an instruction based on it's style. 
Style: Is the tone and writing style appropriate for a blog post or social media content? It should use simple but technical words and avoid formal or academic language.

Style scale:
1 (Poor): Too formal, uses some overly complex words
2 (Good): Good balance of technical content and accessibility, but still uses formal words and expressions
3 (Excellent): Perfectly accessible language for blog/social media, uses simple but precise technical terms when necessary

Example of bad style: The Llama2 7B model constitutes a noteworthy progression in the field of artificial intelligence, serving as the successor to its predecessor, the original Llama architecture.
Example of excellent style: Llama2 7B outperforms the original Llama model across multiple benchmarks.

Instruction: {input}

Answer: {output}

Provide your evaluation in JSON format with the following structure:
{{
    "accuracy": {{
        "reason": "...",
        "score": 0
    }},
    "style": {{
        "reason": "...",
        "score": 0
    }}
}}
"""

    def score(self, input: str, output: str, **ignored_kwargs: Any):
        """
        Score the output of an LLM.

        Args:
            output: The output of an LLM to score.
            **ignored_kwargs: Any additional keyword arguments. This is important so that the metric can be used in the `evaluate` function.
        """

        prompt = self.prompt_template.format(input=input, output=output)

        model_output = self.llm_client.generate_string(
            input=prompt, response_format=LLMJudgeStyleOutputResult
        )

        return self._parse_model_output(model_output)

    def _parse_model_output(self, content: str) -> score_result.ScoreResult:
        try:
            dict_content = json.loads(content)
        except Exception:
            raise exceptions.MetricComputationError("Failed to parse the model output.")

        score = dict_content["score"]
        try:
            assert 1 <= score <= 3, f"Invalid score value: {score}"
        except AssertionError as e:
            raise exceptions.MetricComputationError(str(e))

        score = (score - 1) / 2.0  # Normalize the score to be between 0 and 1

        return score_result.ScoreResult(
            name=self.name,
            value=score,
            reason=dict_content["reason"],
        )
