# Local Install

## System dependencies

Before starting to install the LLM Twin project, make sure you have installed the following dependencies on your system:

- [Docker ">=v27.0.3"](https://www.docker.com/)
- [GNU Make ">=3.81"](https://www.gnu.org/software/make/)

The whole LLM Twin application will be run locally using Docker. 

## Configure

All the sensitive credentials are placed in a `.env` file that will always sit on your hardware.

Go to the root of the repository, copy our `.env.example` file and fill it with your credentials:
```shell
cp .env.example .env
```

## Supported commands

We will use `GNU Make` to install and run our application.

To see all our supported commands, run the following:
```shell
make help
```

## Set up the infrastructure

### Spin up the infrastructure

Now, the whole infrastructure can be spun up using a simple Make command:

```shell
make local-start
```

Behind the scenes it will build and run all the Docker images defined in the [docker-compose.yml](https://github.com/decodingml/llm-twin-course/blob/main/docker-compose.yml) file.

## Read this before starting 🚨 

> [!CAUTION]
> For `Mongo` to work with multiple replicas (as we use it in our Docker setup) on `macOS` or `Linux` systems, you have to add the following lines of code to `/etc/hosts`:
>
> ```
> 127.0.0.1       mongo1
> 127.0.0.1       mongo2 
> 127.0.0.1       mongo3
> ```
>
> From what we know, on `Windows`, it `works out-of-the-box`. For more details, check out this article: https://medium.com/workleap/the-only-local-mongodb-replica-set-with-docker-compose-guide-youll-ever-need-2f0b74dd8384

> [!WARNING]
> For `arm` users (e.g., `M1/M2/M3 macOS devices`), go to your Docker desktop application and enable `Use Rosetta for x86_64/amd64 emulation on Apple Silicon` from the Settings. There is a checkbox you have to check.
> Otherwise, your Docker containers will crash.

### Tear down the infrastructure

Run the following `Make` command to tear down all your docker containers:

```shell
make local-stop
```

## Run an end-to-end flow

Now that we have configured our credentials and started our infrastructure let's look at how to run an end-to-end flow of the LLM Twin application.

> [!IMPORTANT]
> Note that we won't go into the details of the system here. To fully understand it, check out our free article series, which explains everything step-by-step: [LLM Twin articles series](https://medium.com/decodingml/llm-twin-course/home).

### Step 1: Crawlers

Trigger the crawler to collect data and add it to the MongoDB:

```shell
make local-test-github
# or make local-test-medium
``` 

After the data is added to Mongo, the CDC component will be triggered, which will populate the RabbitMQ with the event.

### Step 2: Feature engineering & Vector DB

Check that the feature pipeline works and the vector DB is successfully populated.

To check the `feature pipeline`, check the logs of the `llm-twin-bytewax` Docker container by running:
```shell
docker logs llm-twin-bytewax
```
You should see logs reflecting the cleaning, chunking, and embedding operations (without any errors, of course).

To check that the Qdrant `vector DB` is populated successfully, go to its dashboard at [localhost:6333/dashboard](localhost:6333/dashboard). There, you should see the repositories or article collections created and populated.

> [!NOTE]
> If using the cloud version of Qdrant, go to your Qdrant account and cluster to see the same thing as in the local dashboard.

### Step 3: RAG retrieval step

Now that we have some data in our vector DB, let's test out the RAG retriever:
```shell
make local-test-retriever
```

> [!NOTE]
> Before running this command, check [Qdrant's dashboard](localhost:6333/dashboard) to ensure that your vector DB is populated with data.


### Step 4: Generate the instruct dataset

The last step, before fine-tuning is to generate an instruct dataset and track it as an artifact in Comet ML. To do so, run:
```shell
make generate-dataset
```

> Now open [Comet ML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github), go to your workspace, and open the `Artifacts` tab. There, you should find three artifacts as follows:
> - `articles-instruct-dataset` 
> - `posts-instruct-dataset`
> - `repositories-instruct-dataset`


### Step 5: Fine-tuning

For details on setting up the training pipeline on [Qwak](https://www.qwak.com/lp/end-to-end-mlops/?utm_source=github&utm_medium=referral&utm_campaign=decodingml) and running it, please refer to the [TRAINING](https://github.com/decodingml/llm-twin-course/blob/main/TRAINING.md) document.

### Step 6: Inference

After you have finetuned your model, the first step is to deploy the inference pipeline to Qwak as a REST API service:
```shell
deploy-inference-pipeline 
```

> [!NOTE]
> You can check out the progress of the deployment on [Qwak](https://www.qwak.com/lp/end-to-end-mlops/?utm_source=github&utm_medium=referral&utm_campaign=decodingml).

After the deployment is finished (it will take a while), you can call it by calling:
```shell
make call-inference-pipeline
```

Ultimately, after you stop using it, make sure to delete the deployment by running:
```shell
make undeploy-infernece-pipeline
```
