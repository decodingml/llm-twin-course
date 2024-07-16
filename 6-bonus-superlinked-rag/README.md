# Install Local Setup

## 1. Start the Superlinked server

Make sure you have `pyenv` installed. For example, on MacOS you can install it as:
```shell
brew update
brew install pyenv
```

Now, let's the Superlinked server by running the following commands:
```shell
# Create a virtual environment and install all necesary dependencies to deploy the server.
cd 6-bonus-superlinked-rag/server
./tools/init-venv.sh
cd runner
source "$(poetry env info --path)/bin/activate"
cd ..

# Make sure you have your docker engine running (e.g. start the docker desktop app).
./tools/deploy.py up
```

> [NOTE!]
> After the server started, you can check out it works and also it's API at http://localhost:8080/docs/

## 2. Start the rest of the infrastructure

From the root of the repository, run the following to start all necessary components to run locally the LLM twin project powered by Superlinked:
```shell
make local-start-superlinked
```

To stop the local infrastructure, run:
```shell
make local-stop-superlinked
```

> After running the ingestion pipeline, you can visualize what's inside the Redis vector DB at http://localhost:8001/redis-stack/browser
