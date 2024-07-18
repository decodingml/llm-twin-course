include .env

$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

AWS_CURRENT_REGION_ID := $(shell aws configure get region)
AWS_CURRENT_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)

PYTHONPATH := $(shell pwd)

.PHONY: build-all env-var

RED := \033[0;31m
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RESET := \033[0m

env-var:
    @echo "Environment variable VAR is: ${RABBITMQ_HOST}"

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done


# ------  Infrastructure ------ 

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


# ------ Crawler ------

local-test-medium: # Send test command on local to test the lambda with a Medium article
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iuztin", "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"}'

local-test-github: # Send test command on local to test the lambda with a Github repository
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iuztin", "link": "https://github.com/decodingml/llm-twin-course"}'

invoke: # Invoke remote lambda from local
	aws lambda invoke \
		--function-name crawler \
		--cli-binary-format raw-in-base64-out \
		--payload '{"user": "Paul Iuztin", "link": "https://github.com/iusztinpaul/hands-on-llms"}' \
		response.json

# ------ RAG Feature Pipeline ------

local-bytewax: # Run bytewax pipeline
	RUST_BACKTRACE=full poetry run python -m bytewax.run 3-feature-pipeline/main.py

generate-dataset: # Generate dataset for finetuning and version it in Comet ML
	python -m finetuning.generate_data

# ------ RAG ------

local-test-retriever: # Test retriever
	poetry run python retriever.py

# ------ Qwak: Fine-tuning & Inference ------

create-qwak-project: # Create Qwak project for serving the model
	@echo "$(YELLOW)Creating Qwak project $(RESET)"
	qwak models create "llm_twin" --project "llm-twin-course"

deploy: # Deploy the model to Qwak
	@echo "$(YELLOW)Dumping poetry env requirements to $(RESET) $(GREEN) requirements.txt $(RESET)"
	poetry export -f requirements.txt --output finetuning/requirements.txt --without-hashes
	@echo "$(GREEN)Triggering Qwak Model Build$(RESET)"
	poetry run qwak models build -f build_config.yaml .

local-test-qwak: # Test Qwak model locally
	poetry run python test_local.py


# ------ Superlinked Bonus Series ------

local-start-superlinked: # Buil and start local infrastructure used in the Superlinked series.
	docker compose -f docker-compose-superlinked.yml up --build -d

local-stop-superlinked: # Stop local infrastructure used in the Superlinked series.
	docker compose -f docker-compose-superlinked.yml down --remove-orphans

test-superlinked-server:
	poetry run python 6-bonus-superlinked-rag/local_test.py

local-bytewax-superlinked: # Run bytewax pipeline powered by superlinked
	RUST_BACKTRACE=full poetry run python -m bytewax.run 6-bonus-superlinked-rag/main.py