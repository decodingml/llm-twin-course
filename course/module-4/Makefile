help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

local-start-infra: # Build and start mongodb, mq and qdrant.
	docker-compose -f docker-compose.yml up --build -d

local-stop-infra: # Stop mongodb, mq and qdrant.
	docker-compose -f docker-compose.yml down --remove-orphans

local-run-test: # Start retrival process
	poetry run python cdc.py

