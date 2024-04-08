help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

local-start: # Buil and start mongodb and mq and qdrant.
	docker-compose -f docker-compose.yml up --build -d

local-start-cdc: # Start CDC system
	python cdc.py

local-insert-data-mongo: #Insert data to mongodb
	python insert_data_mongo.py

local-bytewax: # Run bytewax pipeline
	python -m bytewax.run data_flow/bytewax_pipeline     