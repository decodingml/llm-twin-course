include .env

$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

AWS_CURRENT_REGION_ID := $(shell aws configure get region)
AWS_CURRENT_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)

PYTHONPATH := $(shell pwd)/src

RED := \033[0;31m
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RESET := \033[0m

install:
	poetry env use 3.11
	poetry install --without superlinked_rag

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# ======================================
# ---------- Infrastructure ------------
# ======================================

push: # Build & push image to docker ECR (e.g make push IMAGE_TAG=latest)
	echo "Logging into AWS ECR..."
	aws ecr get-login-password --region $(AWS_CURRENT_REGION_ID) | docker login --username AWS --password-stdin $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com
	echo "Build & Push Docker image..."
	docker buildx build --platform linux/amd64 -t $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com/crawler:$(IMAGE_TAG) .
	echo "Push completed successfully."

local-start: # Buil and start local infrastructure.
	docker compose -f docker-compose.yml up --build -d

local-stop: # Stop local infrastructure.
	docker compose -f docker-compose.yml down --remove-orphans

create-sagemaker-execution-role: # Create SageMaker execution role.
	cd src && poetry run python -m core.aws.create_execution_role

# ======================================
# ------------- Crawler ----------------
# ======================================

local-test-medium: # Send test command on local to test the lambda with a Medium article
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iusztin", "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"}'

local-test-github: # Send test command on local to test the lambda with a Github repository
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iusztin", "link": "https://github.com/decodingml/llm-twin-course"}'

local-ingest-data: # Ingest all links from data/links.txt file
	while IFS= read -r link; do \
		echo "Processing: $$link"; \
		curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
			-d "{\"user\": \"Paul Iusztin\", \"link\": \"$$link\"}"; \
		echo "\n"; \
		sleep 2; \
	done < data/links.txt

cloud-test-medium: # Send command to the cloud lambda with a Github repository
	aws lambda invoke \
		--function-name crawler \
		--cli-binary-format raw-in-base64-out \
		--payload '{"user": "Paul Iusztin", "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"}' \
		response.json

# ======================================
# -------- RAG Feature Pipeline --------
# ======================================

local-feature-pipeline: # Run the RAG feature pipeline
	RUST_BACKTRACE=full poetry run python -m bytewax.run src/feature_pipeline/main.py

local-test-retriever: # Test retriever
	docker exec -it llm-twin-bytewax python -m retriever

generate-dataset: # Generate dataset for finetuning and version it in Comet ML
	docker exec -it llm-twin-bytewax python -m finetuning.generate_data

# ======================================
# ------ AWS SageMaker: Training pipeline ------
# ======================================

generate-instruct-dataset:
	cd src/feature_pipeline && poetry run python -m generate_dataset.generate

start-training-pipeline:
	cd src/training_pipeline && poetry run python run_on_sagemaker.py

create-qwak-project: # Create Qwak project for serving the model
	@echo "$(YELLOW)Creating Qwak project...$(RESET)"
	qwak models create "llm_twin" --project "llm-twin-course"

local-test-training-pipeline: # Test Qwak model locally
	@echo "$(GREEN)Calling local Qwak build for testing and development...$(RESET)"
	cd src/training_pipeline && poetry run python test_local.py

deploy-training-pipeline: # Trigger Qwak model build and start training pipeline
	@echo "$(GREEN)Triggering Qwak model build and starting training pipeline...$(RESET)"
	cd src/training_pipeline && poetry run qwak models build -f build_config.yaml .

# ======================================
# ------ AWS SageMaker: Inference pipeline ------
# ======================================

deploy-inference-pipeline: # Deploy the inference pipeline to AWS SageMaker.
	cd src/inference_pipeline && poetry run python -m aws.deploy_sagemaker_endpoint

delete-inference-pipeline-deployment: # Delete the deployment of the AWS SageMaker inference pipeline.
	cd src/inference_pipeline && PYTHONPATH=$(PYTHONPATH) poetry run python -m aws.delete_sagemaker_endpoint

call-inference-pipeline: # Call the inference pipeline.
	cd src/inference_pipeline && poetry run python -m main

# ======================================
# ------ Superlinked Bonus Series ------
# ======================================

install-superlinked:
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