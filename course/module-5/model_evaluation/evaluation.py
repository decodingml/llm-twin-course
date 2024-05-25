from langchain_openai import ChatOpenAI

from settings import settings
from llm_components.chain import GeneralChain
from llm_components.prompt_templates import EvaluationTemplate


def evaluate(query: str, context: list[str], output: str) -> str:
    evaluation_template = EvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID)
    chain = GeneralChain.get_chain(
        llm=model,
        output_key='evaluation',
        template=prompt_template
    )

    response = chain.invoke({'query': query, 'context': context, 'output': output})

    return response['evaluation']
