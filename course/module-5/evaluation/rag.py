import llm_components.prompt_templates as templates
from llm_components.chain import GeneralChain

from langchain_openai import ChatOpenAI
from pandas import DataFrame

from settings import settings
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import context_precision, context_relevancy, context_recall


def evaluate(query: str, context: list[str], output: str) -> str:
    evaluation_template = templates.RAGEvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID)
    chain = GeneralChain.get_chain(
        llm=model, output_key="rag_eval", template=prompt_template
    )

    response = chain.invoke({"query": query, "context": context, "output": output})

    return response["rag_eval"]


def evaluate_with_ragas(query: str, context: list[str], output: str) -> DataFrame:

    data_sample = {
        "question": query,
        "answer": output,
        "context": context
    }

    dataset = Dataset.from_dict(data_sample)
    score = evaluate(dataset=dataset, metrics=[context_precision, context_relevancy, context_recall])

    return score.to_pandas()