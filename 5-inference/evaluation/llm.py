from config import settings
from langchain_openai import ChatOpenAI
from llm.prompt_templates import LLMEvaluationTemplate


def evaluate(query: str, output: str) -> str:
    evaluation_template = LLMEvaluationTemplate()
    prompt = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)
    chain = prompt | model | str

    response = chain.invoke({"query": query, "output": output})

    return response
