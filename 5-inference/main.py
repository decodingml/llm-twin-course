import sys
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.append(ROOT_DIR)

from core import logger_utils

from inference_pipeline import LLMTwin

logger = logger_utils.get_logger(__name__)
logger.info(
    f"Added the following directory to PYTHONPATH to simulate multiple modules: {ROOT_DIR}"
)


if __name__ == "__main__":
    inference_endpoint = LLMTwin()

    query = """
        Hello I am Paul Iusztin.
        
        Could you draft a LinkedIn post discussing RAG? 
        I'm particularly interested in how it works.
        """

    response = inference_endpoint.generate(
        query=query,
        enable_rag=True,
        enable_evaluation=False,
    )

    logger.info("=" * 50)
    logger.info(f"Query: {query}")
    logger.info("=" * 50)
    logger.info(f"Answer: {response['answer']}")
    logger.info("=" * 50)
    logger.info(f"LLM Evaluation Result: {response['llm_evaluation_result']}")
    logger.info("=" * 50)
