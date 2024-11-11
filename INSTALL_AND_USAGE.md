# Install 

## System dependencies

Before starting to install the LLM Twin project, make sure you have installed the following dependencies on your system:

- [Python "3.11"](https://www.python.org/downloads/)
- [Poetry ">=1.8.4"](https://python-poetry.org/docs/)
- [GNU Make ">=3.81"](https://www.gnu.org/software/make/)
- [Docker ">=v27.0.3"](https://www.docker.com/)
- [aws CLI ">=2.18.5"](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Cloud / services dependencies



## Supported commands

We will use `GNU Make` to install and run our application.

To see all our supported commands, run the following:
```shell
make help
```

## Configure

All the sensitive credentials are placed in a `.env` file that will always sit at the root of your directory, at the same level with the `.env.example` file.

Go to the root of the repository, copy our `.env.example` file and fill it with your credentials:
```shell
cp .env.example .env
```

## Install local dependencies

You can create a Python virtual environment and install all the necesary dependencies using Poetry, by running:
```shell
make install
```
**NOTE:** You need Python 3.11 installed. You can either install it globally or install [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python dependencies. The `.python-version` file will signal to `pyenv` what Python version it needs to use in this particular project.

After installing the dependencies into the Poetry virtual environment, you can run the following to activate it into your current CLI:
```bash
poetry shell
```

## Set up the data infrastructure

We support running the entire data infrastructure (crawling, CDC, MongoDB, and Qdrant) through Docker. Thus, with a few commands you can quickly populate the data warehouse and vector DB with relevant data to test out the RAG, training, and inference parts of the course.

### Spin up the infrastructure

You can start all the required Docker containers, by running:
```shell
make local-start
```

Behind the scenes it will build and run all the Docker images defined in the [docker-compose.yml](https://github.com/decodingml/llm-twin-course/blob/main/docker-compose.yml) file.

> [!CAUTION]
> For `MongoDB` to work with multiple replicas (as we use it in our Docker setup) on `macOS` or `Linux` systems, you have to add the following lines of code to `/etc/hosts`:
>
> ```
> 127.0.0.1       mongo1
> 127.0.0.1       mongo2 
> 127.0.0.1       mongo3
> ```
>
> From what we know, on `Windows`, it `works out-of-the-box`. For more details, check out this [article](https://medium.com/workleap/the-only-local-mongodb-replica-set-with-docker-compose-guide-youll-ever-need-2f0b74dd8384)

> [!WARNING]
> For `arm` users (e.g., `M macOS devices`), go to your Docker desktop application and enable `Use Rosetta for x86_64/amd64 emulation on Apple Silicon` from the Settings. There is a checkbox you have to check.
> Otherwise, your Docker containers will crash.

### Tear down the infrastructure

Run the following `Make` command to tear down all your docker containers:

```shell
make local-stop
```

# Usage: Run an end-to-end flow

Now that we have configured our credentials, local environemnt and Docker infrastructure let's look at how to run an end-to-end flow of the LLM Twin course.

> [!IMPORTANT]
> Note that we won't go into the details of the system here. To fully understand it, check out our free lessons, which explains everything step-by-step: [LLM Twin articles series](https://medium.com/decodingml/llm-twin-course/home).

### Step 1: Crawling data

Trigger the crawler to collect data and add it to the MongoDB:

```shell
make local-test-medium
# or make local-test-github
``` 
You should get a response with a `200` status code, as follows:
```
{"statusCode": 200, "body": "Link processed successfully"}
```

After running the command, this will happen:
1. it will crawl a Medium/GitHub link
2. process and add the data to MongoDB
3. the CDC component will be triggered, which will populate the RabbitMQ with the event
4. the RAG feature pipeline will read the event from RabbitMQ, process it for RAG, and add it to the Qdrant vector DB

### Step 2: Feature engineering & Vector DB

The previous step actually called both the crawling and RAG feature engineering pipeline. But now, let's check that everything worked as expected.

Thus, let's check that the feature pipeline works and the vector DB is successfully populated.

To do so, check the logs of the `llm-twin-feature-pipeline` Docker container by running:
```shell
docker logs llm-twin-feature-pipeline
```
You should see logs reflecting the cleaning, chunking, and embedding operations (without any errors, of course).

To check that the Qdrant `vector DB` is populated successfully, go to its dashboard at [localhost:6333/dashboard](localhost:6333/dashboard). There, you should see the repositories or article collections created and populated.

> [!NOTE]
> If using the cloud version of Qdrant, go to your Qdrant account and cluster to see the same thing as in the local dashboard.

### Step 3: Populating MongoDB and Qdrant with more data

To populate MongoDB and VectorDB with ~50 links, run the following command (but first make sure that everything runs smooth):
```bash
make local-ingest-data
```

### Step 4: Testing the RAG retrieval step

Now that our Qdrant vector DB is populated with our data, let's test out the RAG retrieval module:
```shell
make local-test-retriever
```

> [!IMPORTANT]
> Before running this command, check [Qdrant's dashboard](localhost:6333/dashboard) to ensure that your vector DB is populated with data.

### Step 5: Generating the instruct dataset

The last step before fine-tuning is to generate an instruct dataset and track it as an artifact with Comet ML. To do so, run:
```shell
make local-generate-instruct-dataset
```

Now go to [Comet ML](https://www.comet.com/signup/?utm_source=decoding_ml&utm_medium=partner&utm_content=github), then to your workspace, and open the `Artifacts` tab. There, you should find three artifacts as follows:
> - `articles-instruct-dataset` 
> - `posts-instruct-dataset`
> - `repositories-instruct-dataset`

> [!NOTE]
> We also publicly provide our own artifacts that you can use to fine-tune your LLMs in case you got stuck or don't want to generate them yourself:
> - [articles-instruct-dataset](https://www.comet.com/decodingml/artifacts/articles-instruct-dataset)
> - [posts-instruct-dataset](https://www.comet.com/decodingml/artifacts/posts-instruct-dataset)
> - [repositories-instruct-dataset](https://www.comet.com/decodingml/artifacts/repositories-instruct-dataset)

### Step 6: Setting up AWS SageMaker

For your AWS set-up to work correctly, you need the AWS CLI installed on your local machine and properly configured with an admin user (or a user with enough permissions to create new SageMaker, ECR and S3 resources; using an admin user will make everything more straightforward).

With the same configuration used to set up your AWS CLI, also fill in the following environment variables from your `.env` file:
```bash
AWS_ARN_ROLE=str
AWS_REGION=eu-central-1
AWS_ACCESS_KEY=str
AWS_SECRET_KEY=str
```
AWS credentials are typically stored in `~/.aws/credentials`. You can view this file directly using `cat` or similar commands:
```shell
cat ~/.aws/credentials
```

The next step is to create an IAM execution role used by AWS SageMaker to access other AWS resources. This is standard practice when working with SageMaker.

To automatically create it, run:
```bash
make create-sagemaker-execution-role
```

The script will generate a file found at `src/sagemaker_execution_role.json`. Open it, copy the value under the `RoleArn` key from the JSON file, and fill in the following env var from your `.env` file:
```bash
AWS_ARN_ROLE=str
```

To conclude, by the end of this section you should have filled correctly the following environment variables in your `.env` file:
```bash
AWS_ARN_ROLE=str
AWS_REGION=eu-central-1
AWS_ACCESS_KEY=str
AWS_SECRET_KEY=str
```

Now, we can move on to the fine-tunine and inference pipelines, which use AWS SagaMaker.

> [!IMPORTANT]
> Note that we use `ml.g5.2xlarge` EC2 instances to run AWS SageMaker, which cost `~$2 / hour` (depending on your region). Our tests will take only a few hours. Thus, this won't get expensive. Just run our clean-up resources scripts after you finish testing our app. 

### Step 7: Starting the fine-tuning pipeline

After setting up everything necesary for AWS SageMaker, to kick of the training in dummy mode, is as easy as. The dummy mode will reduce the dataset size and epochs to quickly see that everything works fine:
```bash
make start-training-pipeline-dummy-mode
```

To kick off the full training, run:
```bash
make start-training-pipeline
```

> [!NOTE]
> You can check out the deployment progress in the AWS console in the SageMaker dashboard.

> [!WARNING]
> If you get any `Service Quotas` errors, you must increase your AWS quotas for `ml.g5.2xlarge` instances. More exactly, you have to go to your AWS account -> Service Quatas -> AWS services -> search `SageMaker` -> search `ml.g5.2xlarge`, then increase the quotas to 1 for `ml.g5.2xlarge for training job usage` (training jobs) and `ml.g5.2xlarge for endpoint usage` (inference jobs). More details on changing service quotas are in [this article](https://docs.aws.amazon.com/servicequotas/latest/userguide/request-quota-increase.html).


### Step 8: Testing the inference pipeline

After you have finetuned your model, the first step is to deploy the LLM to AWS SageMaker as a REST API service:
```shell
deploy-inference-pipeline 
```

> [!NOTE]
> You can check out the deployment progress in the AWS console in the SageMaker dashboard.

After the deployment is finished (it will take a few minutes), you can call it with a test prompt by running:
```shell
make call-inference-pipeline
```

Ultimately, after testing it, you can delete the AWS SageMaker deployment, by running:
```shell
make delete-inference-pipeline-deployment
```
