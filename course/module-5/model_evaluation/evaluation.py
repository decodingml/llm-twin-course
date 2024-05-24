import llm_components.prompt_templates as templates
from langchain_openai import ChatOpenAI
from llm_components.chain import GeneralChain
from settings import settings


def llm_eval_using_GPT(query: str, output: str) -> str:
    evaluation_template = templates.LLMEvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)
    chain = GeneralChain.get_chain(
        llm=model, output_key="llm_eval", template=prompt_template
    )

    response = chain.invoke({"query": query, "output": output})

    return response["llm_eval"]


def rag_eval_using_GPT(query: str, context: list[str], output: str) -> str:
    evaluation_template = templates.RAGEvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID)
    chain = GeneralChain.get_chain(
        llm=model, output_key="rag_eval", template=prompt_template
    )

    response = chain.invoke({"query": query, "context": context, "output": output})

    return response["rag_eval"]
