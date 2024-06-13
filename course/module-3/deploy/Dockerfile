FROM python:3.11-slim-bullseye

# Set environment variables
ENV WORKSPACE_ROOT=/usr/src/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

RUN mkdir -p $WORKSPACE_ROOT

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends build-essential \
    curl \
    libssl-dev \
    && apt-get clean

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get remove -y curl

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false  \
    && poetry install \
    && rm poetry.lock pyproject.toml

WORKDIR $WORKSPACE_ROOT

COPY . .

# Give execution permission to your shell script
RUN chmod +x ./deploy/entrypoint.sh

# Run your shell script
CMD ["./deploy/entrypoint.sh"]
