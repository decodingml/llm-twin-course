import llm_components.prompt_templates as templates
from datasets import Dataset
from langchain_openai import ChatOpenAI
from llm_components.chain import GeneralChain
from pandas import DataFrame
from ragas import evaluate
from ragas.embeddings import HuggingfaceEmbeddings
from ragas.metrics import (
    answer_correctness,
    answer_similarity,
    context_entity_recall,
    context_recall,
    context_relevancy,
    context_utilization,
)
from settings import settings

# Evaluating against the following metrics
# RETRIEVAL BASED
# 1. Context Utilization - How well the context is utilized
# 2. Context Relevancy - (VDB based) measures the relevance of retrieved context
# 3. Context Recall - How well the context is recalled in the answer
# 4. Context Entity Recall - a measure of what fraction of entities are recalled from ground_truths

# END-TO-END
# 5. Answer Similarity - measures the semantic resemblance between the answer and gt answer
# 6. Answer Corectness - measures the correctness of the answer compared to gt

METRICS = [
    context_utilization,
    context_relevancy,
    context_recall,
    answer_similarity,
    context_entity_recall,
    answer_correctness,
]


def evaluate_w_template(query: str, context: list[str], output: str) -> str:
    evaluation_template = templates.RAGEvaluationTemplate()
    prompt_template = evaluation_template.create_template()

    model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, api_key=settings.OPENAI_API_KEY)
    chain = GeneralChain.get_chain(
        llm=model, output_key="rag_eval", template=prompt_template
    )

    response = chain.invoke({"query": query, "context": context, "output": output})

    return response["rag_eval"]


def evaluate_w_ragas(query: str, context: list[str], output: str) -> DataFrame:
    """
    Evaluate the RAG (query,context,response) using RAGAS
    """
    data_sample = {
        "question": [query],  # Question as Sequence(str)
        "answer": [output],  # Answer as Sequence(str)
        "contexts": [context],  # Context as Sequence(str)
        "ground_truth": ["".join(context)],  # Ground Truth as Sequence(str)
    }

    oai_model = ChatOpenAI(
        model=settings.OPENAI_MODEL_ID,
        api_key=settings.OPENAI_API_KEY,
    )
    embd_model = HuggingfaceEmbeddings(model=settings.EMBEDDING_MODEL_ID)
    dataset = Dataset.from_dict(data_sample)
    score = evaluate(
        llm=oai_model,
        embeddings=embd_model,
        dataset=dataset,
        metrics=METRICS,
    )

    return score
