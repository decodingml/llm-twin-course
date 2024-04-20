help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

local-start-infra: # Buil and start mongodb, mq and qdrant.
	docker-compose -f docker-compose.yml up --build -d

local-stop-infra: # Stop mongodb, mq and qdrant.
	docker-compose -f docker-compose.yml down

local-start-cdc: # Start CDC system
	poetry run python cdc.py

local-insert-data-mongo: #Insert data to mongodb
	poetry run python insert_data_mongo.py

local-bytewax: # Run bytewax pipeline
	poetry run python -m bytewax.run data_flow/bytewax_pipeline     