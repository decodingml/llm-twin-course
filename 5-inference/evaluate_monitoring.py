import opik
from config import settings
from opik.evaluation import evaluate
from opik.evaluation.metrics import Hallucination

from core.logger_utils import get_logger

logger = get_logger(__name__)


def evaluation_task(x: dict) -> dict:
    return {
        "input": x["input"]["query"],
        "context": x["expected_output"]["context"],
        "output": x["expected_output"]["answer"],
    }


if __name__ == "__main__":
    client = opik.Opik()
    dataset_name = "LLMTwinMonitoringDataset"
    try:
        dataset = client.get_dataset(dataset_name)
    except Exception as e:
        logger.error("Monitoring dataset not found in Opik. Exiting.")
        exit(1)

    experiment_config = {
        "model_id": settings.QWAK_DEPLOYMENT_MODEL_ID,
    }

    res = evaluate(
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=[Hallucination(model=settings.OPENAI_MODEL_ID)],
        experiment_config=experiment_config,
    )
