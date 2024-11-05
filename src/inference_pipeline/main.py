import sys
from pathlib import Path

# To mimic using multiple Python modules, such as 'core' and 'feature_pipeline',
# we will add the './src' directory to the PYTHONPATH. This is not intended for
# production use cases but for development and educational purposes.
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.append(ROOT_DIR)

from core import logger_utils

from llm_twin import LLMTwin

logger = logger_utils.get_logger(__name__)
logger.info(
    f"Added the following directory to PYTHONPATH to simulate multiple modules: {ROOT_DIR}"
)


if __name__ == "__main__":
    inference_endpoint = LLMTwin(mock=False)

    query = """
        Hello I am Paul Iusztin.
        
        Could you draft a LinkedIn post discussing RAG? 
        I'm particularly interested in how it works.
        """

    response = inference_endpoint.generate(
        query=query, enable_rag=True, sample_for_evaluation=True
    )

    logger.info("=" * 50)
    logger.info(f"Query: {query}")
    logger.info("=" * 50)
    logger.info(f"Answer: {response['answer']}")
    logger.info("=" * 50)
