AWS_CURRENT_REGION_ID := $(shell aws configure get region)
AWS_CURRENT_ACCOUNT_ID := $(shell aws sts get-caller-identity --query "Account" --output text)

PYTHONPATH := $(shell pwd)

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

local-build: # Build lambda crawler on local.
	docker buildx build --platform linux/amd64 -t crawler .

local-deploy: # Deploy lambda crawler custom docker image on local.
	docker run \
		-p 9000:8080 \
		--network llm-twin-course_local \
		--platform linux/amd64 \
		crawler:latest

local-test: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iuztin", "link": "https://medium.com/@pauliusztin/the-llms-kit-build-a-production-ready-real-time-financial-advisor-system-using-streaming-ffdcb2b50714"}'

invoke: # Invoke remote lambda from local
	aws lambda invoke \
		--function-name crawler \
		--cli-binary-format raw-in-base64-out \
		--payload '{"user": "Paul Iuztin", "link": "https://github.com/iusztinpaul/hands-on-llms"}' \
		response.json

push: # Build & push image to docker ECR (e.g make push IMAGE_TAG=latest)
	echo "Logging into AWS ECR..."
	aws ecr get-login-password --region $(AWS_CURRENT_REGION_ID) | docker login --username AWS --password-stdin $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com
	echo "Build & Push Docker image..."
	docker buildx build --platform linux/amd64 -t $(AWS_CURRENT_ACCOUNT_ID).dkr.ecr.$(AWS_CURRENT_REGION_ID).amazonaws.com/crawler:$(IMAGE_TAG) .
	echo "Push completed successfully."

clean: # Cleanup files generated during sam building.
	@echo "Cleaning old files..."
	rm -rf /.pytest_cache
	rm -rf /__pycache
	rm -rf */.pyc
	rm -rf .mypy_cache
	@echo "Done."


#2-data-ingestion

local-start: # Buil and start mongodb and mq.
	docker-compose -f docker-compose.yml up --build -d

local-stop-infra: # Stop mongodb, mq and qdrant.
	docker-compose -f docker-compose.yml down

local-insert-data-mongo: # Insert data to mongodb
	@PYTHONPATH=$(PYTHONPATH) poetry run python 3-feature-pipeline/insert_data_mongo.py


local-bytewax: # Run bytewax pipeline
	RUST_BACKTRACE=full poetry run python -m bytewax.run data_flow/bytewax_pipeline 

generate-dataset: # Generate dataset for finetuning and version it in Comet ML
	python -m finetuning.generate_data

local-test-retriever: # Test retriever
	poetry run python retriever.py



	RED := \033[0;31m
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RESET := \033[0m

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "-------------------"
	@echo "$(YELLOW)list$(RESET)		: List available targets with descriptions"
	@echo ""
	@echo "== Deploy =="
	@echo "$(GREEN)deploy$(RESET)		: Dumps the poetry env requirements to requirements.txt and triggers Qwak Model Build"
	@echo ""
	@echo "== Test =="
	@echo "$(YELLOW)test$(RESET)		: Runs unit-tests on local deployed model wrapped as QwakModel"
	@echo ""
	@echo ""

list: help

create-qwak-project:
	@echo "$(YELLOW)Creating Qwak project $(RESET)"
	qwak models create "llm_twin" --project "llm-twin-course"

deploy:
	@echo "$(YELLOW)Dumping poetry env requirements to $(RESET) $(GREEN) requirements.txt $(RESET)"
	poetry export -f requirements.txt --output finetuning/requirements.txt --without-hashes
	@echo "$(GREEN)Triggering Qwak Model Build$(RESET)"
	poetry run qwak models build -f build_config.yaml .

test:
	poetry run python test_local.py


