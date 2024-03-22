help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

local-build: # Build lambda crawler on local.
	docker buildx build --platform linux/amd64 -t crawler .

local-deploy: # Deploy lambda crawler custom docker image on local.
	docker run \
		-p 9000:8080 \
		--network llm-twin-course_local \
		crawler:latest

local-test: # Send test command on local to test  the lambda
	curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
	  	-d '{"user": "Paul Iuztin", "link": "https://medium.com/@pauliusztin/the-llms-kit-build-a-production-ready-real-time-financial-advisor-system-using-streaming-ffdcb2b50714"}'

invoke:
	aws lambda invoke \
		--function-name crawler \
		--cli-binary-format raw-in-base64-out \
		--payload '{"user": "Paul Iuztin", "link": "https://github.com/iusztinpaul/hands-on-llms"}' \
		response.json

clean: # Cleanup files generated during sam building.
	@echo "Cleaning old files..."
	rm -rf /.pytest_cache
	rm -rf /__pycache
	rm -rf */.pyc
	rm -rf .mypy_cache
	@echo "Done."
