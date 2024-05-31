help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

deploy-llm-microservice: # Deploy the Qwak model.
	qwak models deploy realtime --model-id "llm_twin" --instance "gpu.a10.2xl" --timeout 50000 --replicas 2 --server-workers 2

undeploy-llm-microservice: # Deploy the Qwak model.
	qwak models undeploy --model-id "llm_twin"

call-inference-pipeline: # Call the inference pipeline.
	poetry run python main.py

