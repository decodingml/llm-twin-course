RED := \033[0;31m
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RESET := \033[0m

ENV_NAME := "py39upstash"
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

deploy:
	@echo "$(YELLOW)Dumping poetry env requirements to $(RESET) $(GREEN) requirements.txt $(RESET)"
	poetry export -f requirements.txt --output finetuning/requirements.txt --without-hashes
	@echo "$(GREEN)Triggering Qwak Model Build$(RESET)"
	qwak models build -f build_config.yaml .

test:
	python test_local.py


