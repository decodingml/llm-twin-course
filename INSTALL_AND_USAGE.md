# Local Install

## System dependencies

Before starting to install the LLM Twin project, make sure you have installed the following dependencies on your system:

- (Docker ">=v27.0.3")[https://www.docker.com/]
- (GNU Make ">=3.81")[https://www.gnu.org/software/make/]

The whole LLM Twin application will be run locally using Docker. 

## Configure

All the sensitive credentials are placed in a `.env` file that will always sit on your hardware.

Go to the root of the repository, copy our `.env.example` file and fill it with your credentials:
```shell
cp .env.example .env
```

## Run

### Check all possible `Make` commands
```shell
make help
```

### Spin up the infrastructure

Now, the whole infrastructure can be spun up using a simple Make command:

```shell
make local-start
```

Behind the scenes it will build and run all the Docker images defined in the [docker-compose.yml[(https://github.com/decodingml/llm-twin-course/blob/main/docker-compose.yml)] file.


> [!CAUTION]
> For `Mongo`` to work with multiple replicas on MacOs or linux systems you have to add the following lines of code to `/etc/hosts`:
>
> ```
> 127.0.0.1       mongo1
> 127.0.0.1       mongo2 
> 127.0.0.1       mongo3
> ```
>
> From what we know on Windows, it works out-of-the-box.
>
>
