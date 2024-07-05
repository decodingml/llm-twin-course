import core.logger_utils as logger_utils
from inference_pipeline import LLMTwin

logger = logger_utils.get_logger(__name__)


if __name__ == "__main__":
    inference_endpoint = LLMTwin()

    query = """
        Hello my author_id is 1.
        
        Could you please draft a LinkedIn post discussing Feature Stores? 
        I'm particularly interested in their importance and how they can be used in ML systems.
        """

    response = inference_endpoint.generate(
        query=query,
        enable_rag=True,
        enable_evaluation=True,
        enable_monitoring=True,
    )

    logger.info(f"Answer: {response['answer']}")
    logger.info("=" * 50)
    logger.info(f"LLM Evaluation Result: {response['llm_evaluation_result']}")
