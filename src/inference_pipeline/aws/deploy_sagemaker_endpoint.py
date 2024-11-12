from config import settings
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri


def main() -> None:
    assert settings.HUGGINGFACE_ACCESS_TOKEN, "HUGGINGFACE_ACCESS_TOKEN is required."

    env_vars = {
        "HF_MODEL_ID": settings.MODEL_ID,
        "SM_NUM_GPUS": "1",  # Number of GPU used per replica.
        "HUGGING_FACE_HUB_TOKEN": settings.HUGGINGFACE_ACCESS_TOKEN,
        "MAX_INPUT_TOKENS": str(
            settings.MAX_INPUT_TOKENS
        ),  # Max length of input tokens.
        "MAX_TOTAL_TOKENS": str(
            settings.MAX_TOTAL_TOKENS
        ),  # Max length of the generation (including input text).
        "MAX_BATCH_TOTAL_TOKENS": str(
            settings.MAX_BATCH_TOTAL_TOKENS
        ),  # Limits the number of tokens that can be processed in parallel during the generation.
        "MESSAGES_API_ENABLED": "true",  # Enable/disable the messages API, following OpenAI's standard.
        "HF_MODEL_QUANTIZE": "bitsandbytes",
    }

    image_uri = get_huggingface_llm_image_uri("huggingface", version="2.2.0")

    model = HuggingFaceModel(
        env=env_vars, role=settings.AWS_ARN_ROLE, image_uri=image_uri
    )

    model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.2xlarge",
        container_startup_health_check_timeout=900,
        endpoint_name=settings.DEPLOYMENT_ENDPOINT_NAME,
    )


if __name__ == "__main__":
    main()
