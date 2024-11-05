from config import settings
from langchain_openai import ChatOpenAI
from inference_pipeline.prompt_templates import LLMEvaluationTemplate


def evaluate(query: str, output: str) -> str:
    evaluation_template = LLMEvaluationTemplate()
    prompt = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)
    chain = prompt | model

    response = chain.invoke({"query": query, "output": output})
    response = response.content

    return response
