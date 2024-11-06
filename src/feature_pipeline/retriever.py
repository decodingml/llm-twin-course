from core import get_logger
from core.config import settings
from core.rag.retriever import VectorRetriever
from dotenv import load_dotenv

logger = get_logger(__name__)

settings.patch_localhost()
logger.warning(
    "Patched settings to work with 'localhost' URLs. When deploying remove the 'settings.patch_localhost()' call."
)

if __name__ == "__main__":
    load_dotenv()
    query = """
        Could you please draft a LinkedIn post discussing RAG systems?
        I'm particularly interested in how RAG works and how it is integrated with vector DBs and large language models (LLMs).
        """
    retriever = VectorRetriever(query=query)
    hits = retriever.retrieve_top_k(k=6, to_expand_to_n_queries=5)

    reranked_hits = retriever.rerank(hits=hits, keep_top_k=5)
    for rank, hit in enumerate(reranked_hits):
        logger.info(f"{rank}: {hit}")
