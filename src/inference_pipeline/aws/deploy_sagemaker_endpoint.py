from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

from config import settings


def main() -> None:
    assert settings.HUGGINGFACE_ACCESS_TOKEN, "HUGGINGFACE_ACCESS_TOKEN is required."

    env_vars = {
        "HF_MODEL_ID": "pauliusztin/LLMTwinLlama-3.1-8B",
        "SM_NUM_GPUS": "1",
        "HUGGING_FACE_HUB_TOKEN": settings.HUGGINGFACE_ACCESS_TOKEN,
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
