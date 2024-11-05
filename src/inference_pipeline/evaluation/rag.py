import llm as templates
from config import settings
from langchain_openai import ChatOpenAI


def evaluate(query: str, context: list[str], output: str) -> str:
    evaluation_template = templates.RAGEvaluationTemplate()
    prompt = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID)
    chain = prompt | model

    response = chain.invoke({"query": query, "context": context, "output": output})
    response = response.content

    return response
