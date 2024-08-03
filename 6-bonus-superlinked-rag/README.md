# Dependencies

- [Docker](https://www.docker.com/)
- [Poetry](https://python-poetry.org/)
- [PyEnv](https://github.com/pyenv/pyenv)
- [Python](https://www.python.org/)
- [GNU Make](https://www.gnu.org/software/make/)

# Install

## 1. Start the Superlinked server

Make sure you have `pyenv` installed. For example, on MacOS you can install it as:
```shell
brew update
brew install pyenv
```

Now, let's start the Superlinked server by running the following commands:
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

> [!NOTE]
> After the server started, you can check out it works and also it's API at http://localhost:8080/docs/

You can test that the Superlinked server started successfully by running the following command from the `root directory` of the `llm-twin-course`:
```
make test-superlinked-server
```
You should see that some mock data has been sent to the Superlinked server and it was queried successfully. 

## 2. Start the rest of the infrastructure

From the root of the repository, run the following to start all necessary components to run locally the LLM twin project powered by Superlinked:
```shell
make local-start-superlinked
```

> [!IMPORTANT]
> Before starting, ensure you have your `.env` file filled with everything required to run the system. 
>
> For more details on setting up the local infrastructure, you can check out the course's main [INSTALL_AND_USAGE](https://github.com/decodingml/llm-twin-course/blob/main/INSTALL_AND_USAGE.md) document.

To stop the local infrastructure, run:
```shell
make local-stop-superlinked
```

> [!NOTE]
> After running the ingestion pipeline, you can visualize what's inside the Redis vector DB at http://localhost:8001/redis-stack/browser


# Usage

To trigger the ingestion, run:
```shell
make local-test-medium
# OR
make local-test-github
```
You can use other Medium or GitHub links to populate the vector DB with more data.

To query the vector DB, run:
```shell
make ... # TO BE ADDED
```

> [!IMPORTANT]
> You can check out the main [INSTALL_AND_USAGE](https://github.com/decodingml/llm-twin-course/blob/main/INSTALL_AND_USAGE.md) document of the course for more details on an end-to-end flow.


# Next steps

If you enjoyed our [Superlinked](https://rebrand.ly/superlinked-github) bonus series, we recommend checking out their site for more examples. As Superlinked is not just a RAG tool but a general vector compute engine, you can build other awesome stuff with it, such as recommender systems. 

→ 🔗 More on [Superlinked](https://rebrand.ly/superlinked-github) ←