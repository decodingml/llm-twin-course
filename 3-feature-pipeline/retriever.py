from dotenv import load_dotenv
from langchain.globals import set_verbose
from rag.retriever import VectorRetriever

import core.logger_utils as logger_utils

set_verbose(True)

logger = logger_utils.get_logger(__name__)

if __name__ == "__main__":
    load_dotenv()
    query = """
        Hello my author_id is 1.
        
        Could you please draft a LinkedIn post discussing RAG systems?
        I'm particularly interested in how RAG works and how it is integrated with vector DBs and large language models (LLMs).
        """
    retriever = VectorRetriever(query=query)
    hits = retriever.retrieve_top_k(k=6, to_expand_to_n_queries=5)

    reranked_hits = retriever.rerank(hits=hits, keep_top_k=5)
    for rank, hit in enumerate(reranked_hits):
        logger.info(f"{rank}: {hit}")
