help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

qwak-start-deploy: # Build qwak model remotely
	qwak models build --no-cache --deploy --main-dir . --model-id "copywriter_model" --instance "gpu.a10.2xl" .

local-test: # Test inference locally
	python test_local.py


