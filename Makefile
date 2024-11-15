include .env

$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

PYTHONPATH := $(shell pwd)/src

install: # Create a local Poetry virtual environment and install all required Python dependencies.
	poetry env use 3.11
	poetry install --without superlinked_rag

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# ======================================
# ------- Docker Infrastructure --------
# ======================================

local-start: # Build and start your local Docker infrastructure.
	docker compose -f docker-compose.yml up --build -d

local-stop: # Stop your local Docker infrastructure.
	docker compose -f docker-compose.yml down --remove-orphans

# ======================================
# ---------- Crawling Data -------------
# ======================================

local-test-medium: # Make a call to your local AWS Lambda (hosted in Docker) to crawl a Medium article.
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iusztin", "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"}'

local-test-github: # Make a call to your local AWS Lambda (hosted in Docker) to crawl a Github repository.
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iusztin", "link": "https://github.com/decodingml/llm-twin-course"}'

local-ingest-data: # Ingest all links from data/links.txt by calling your local AWS Lambda hosted in Docker.
	while IFS= read -r link; do \
		echo "Processing: $$link"; \
		curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
			-d "{\"user\": \"Paul Iusztin\", \"link\": \"$$link\"}"; \
		echo "\n"; \
		sleep 2; \
	done < data/links.txt

# ======================================
# -------- RAG Feature Pipeline --------
# ======================================

local-test-retriever: # Test the RAG retriever using your Poetry env
	cd src/feature_pipeline && poetry run python -m retriever

local-generate-instruct-dataset: # Generate the fine-tuning instruct dataset using your Poetry env.
	cd src/feature_pipeline && poetry run python -m generate_dataset.generate

# ===================================================
# -- AWS SageMaker: Training & Inference pipelines --
# ===================================================

create-sagemaker-execution-role: # Create an AWS SageMaker execution role you need for the training and inference pipelines.
	cd src && PYTHONPATH=$(PYTHONPATH) poetry run python -m core.aws.create_execution_role

start-training-pipeline-dummy-mode: # Start the training pipeline in AWS SageMaker.
	cd src/training_pipeline && poetry run python run_on_sagemaker.py --is-dummy

start-training-pipeline: # Start the training pipeline in AWS SageMaker.
	cd src/training_pipeline && poetry run python run_on_sagemaker.py

local-start-training-pipeline: # Start the training pipeline in your Poetry env.
	cd src/training_pipeline && poetry run python -m finetune

deploy-inference-pipeline: # Deploy the inference pipeline to AWS SageMaker.
	cd src/inference_pipeline && poetry run python -m aws.deploy_sagemaker_endpoint

call-inference-pipeline: # Call the inference pipeline client using your Poetry env.
	cd src/inference_pipeline && poetry run python -m main

delete-inference-pipeline-deployment: # Delete the deployment of the AWS SageMaker inference pipeline.
	cd src/inference_pipeline && PYTHONPATH=$(PYTHONPATH) poetry run python -m aws.delete_sagemaker_endpoint

local-start-ui: # Start the Gradio UI for chatting with your LLM Twin using your Poetry env.
	cd src/inference_pipeline && poetry run python -m ui

evaluate-llm: # Run evaluation tests on the LLM model's performance using your Poetry env.
	cd src/inference_pipeline && poetry run python -m evaluation.evaluate

evaluate-rag: # Run evaluation tests specifically on the RAG system's performance using your Poetry env.
	cd src/inference_pipeline && poetry run python -m evaluation.evaluate_rag

evaluate-llm-monitoring: # Run evaluation tests for monitoring the LLM system using your Poetry env.
	cd src/inference_pipeline && poetry run python -m evaluation.evaluate_monitoring

# ======================================
# ------ Superlinked Bonus Series ------
# ======================================

install-superlinked: # Create a local Poetry virtual environment and install all required Python dependencies (with Superlinked enabled).
	poetry env use 3.11
	poetry install

local-start-superlinked: # Buil and start local infrastructure used in the Superlinked series.
	docker compose -f docker-compose-superlinked.yml up --build -d

local-stop-superlinked: # Stop local infrastructure used in the Superlinked series.
	docker compose -f docker-compose-superlinked.yml down --remove-orphans

test-superlinked-server: # Ingest dummy data into the local superlinked server to check if it's working.
	poetry run python src/bonus_superlinked_rag/local_test.py

local-bytewax-superlinked: # Run the Bytewax streaming pipeline powered by Superlinked.
	RUST_BACKTRACE=full poetry run python -m bytewax.run src/bonus_superlinked_rag/main.py

local-test-retriever-superlinked: # Call the retrieval module and query the Superlinked server & vector DB
	docker exec -it llm-twin-bytewax-superlinked python -m retriever