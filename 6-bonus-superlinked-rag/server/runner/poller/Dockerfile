# --- Python base ---

FROM python:3.11.9 AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# --- Builder base ---

FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml $PYSETUP_PATH/
RUN poetry install --no-root --only poller

# --- Poller ---

FROM python:3.11.5-alpine AS poller

COPY --from=builder-base /opt/pysetup/.venv /opt/pysetup/.venv

WORKDIR /code

#COPY config /code/config
COPY poller/app /code/poller/app
COPY poller/logging_config.ini poller/poller_config.ini /code/poller/

ENTRYPOINT ["/opt/pysetup/.venv/bin/python", "-m", "poller.app.main", "--config_path", "/code/config/config.yaml"]
