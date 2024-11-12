# Superlinked Server

This repository contains a server implementation of the [Superlinked](https://github.com/superlinked/superlinked) library. It is designed to be used by end users who want to leverage the power of Superlinked in deployable projects. With a single script, you can deploy a Superlinked-powered app instance that creates REST endpoints and connects to external Vector Databases. This makes it an ideal solution for those seeking an easy-to-deploy environment for their Superlinked projects.

## Prerequisites

Before you can use this environment, you need to ensure that you have the following prerequisites:

- A local setup or a server on AWS or GCP. Please note that Windows is not supported, you should use Linux or MacOS. You can learn how to create a server on AWS from [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) and on GCP from [here](https://cloud.google.com/compute/docs/quickstart-linux). Or take a look at our simplified [docs](docs/vm.md).
- Python 3.11 or higher. You can download it from [here](https://www.python.org/downloads/).
- Docker with the Compose plugin. You can download Docker from [here](https://www.docker.com/products/docker-desktop) and learn how to use the Compose plugin from [here](https://docs.docker.com/compose/).
- `Poetry` and `pyenv` installed on the machine. Installation steps for `Poetry` can be found [here](https://python-poetry.org/docs/#installation). For `pyenv` installation, please follow [these instructions](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation).
- An S3 bucket if you are using AWS or a GCS bucket if you are using GCP. This bucket is needed to store the `app.py` file, which contains your application's code. This setup allows you to make changes to your application without needing to SSH into the server and edit the `app.py` file in the directory with each change. You can learn how to create an S3 bucket from [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) and a GCS bucket from [here](https://cloud.google.com/storage/docs/creating-buckets). Or take a look at our simplified [docs](docs/bucket.md).

## How to start the application

Once you have all the prerequisites, you can set up and deploy the environment by following these steps:

1. **Clone the Repository**: Start by cloning this repository to your local machine using the command `git clone https://github.com/superlinked/superlinked`.

1. **Navigate to the server folder**: Change your current directory to the cloned repository's `server/` directory using the command `cd <repo-directory>/server`. Replace `<repo-directory>` with the name of the directory where the repository was cloned.

1. **Initialize the Virtual Environment**: Run the `init-venv.sh` script located in the `tools/` directory. This script will set up a Python virtual environment for the project. Use the command `./tools/init-venv.sh` to run the script.

1. **Activate the Virtual Environment**: Source the environment that was just created by the `init-venv.sh` script. Enter the `runner/` directory and use the command `source "$(poetry env info --path)/bin/activate"` to activate the environment.

1. **Configure the Application**: Edit the `config/config.yaml` file to include the bucket URI for `app.py`. The URI should end with `app.py`. This configuration allows the application to know where to find the `app.py` file in your bucket.
    > **Note**: The default value is `local`. If this is set, the `app.py` location is automatically set to the `src/app.py` location inside the repository's directory.

1. **Deploy the Application**: Finally, start the application by running the `deploy.py` script in the `tools/` directory with the `python tools/deploy.py up` command. This will deploy the application based on the configuration you provided in the previous step.

This will start the environment and make it ready for use.

Although if the AWS or GCP instance or your local setup has access to the target bucket the credential handling should be automatic, please note that you might need to configure your AWS or GCP credentials before you can use the environment. You can learn how to do this from [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for AWS and [here](https://cloud.google.com/docs/authentication/getting-started) for GCP. The configuration files for these credentials can be used under the `config` directory if needed.

### Checking the Status of the Services

Once the application is deployed, you can check the status of the services by inspecting the Docker containers. The easiest way to look for logs is to use the built-in command provided by docker compose:
```bash
docker compose logs -f
```

If you would like to check the individual containers, use the `docker ps` command to list all running containers. This will show you the status of each service, including whether it's up and running.

If you need more detailed information about a specific service, you can check its logs using the `docker logs <container-id>` command. Replace `<container-id>` with the ID of the container you're interested in. This will display the logs for that container, which can be useful for troubleshooting.

### Resetting the Environment

If something goes wrong and you need to reset the entire environment, you can do so with the following command from the `server/` directory:
```bash
python tools/deploy.py down && rm -rf cache/ && docker image rm -f server-executor server-poller
```

> Please note that that the name of the images may be different in your specific scenario, please adjust them according to your needs.

This command will stop the application, remove the cache directory, and remove the Docker containers for the executor and the poller. After running this command, you can start the application again by following the steps in the [How to start the application](#how-to-start-the-application) section.

## Usage

There are two main parts of the system which you can interact with:
- [Constructing the app.py](docs/app.md)
- [Interacting with the application via the API](docs/api.md)

To see the detailed description for each, click on the bullet points.

## Support

If you encounter any issues while using this environment, please open an issue in this repository and we will do our best to help you.

