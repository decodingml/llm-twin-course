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
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python -

# --- Executor base ---

FROM builder-base as executor-base

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml $PYSETUP_PATH/
RUN poetry install --no-root --only executor

# --- Executor ---

FROM python:3.11.5-slim AS executor

COPY --from=executor-base /opt/pysetup/.venv/ /opt/pysetup/.venv/

WORKDIR /code

RUN apt-get update && apt-get install --no-install-recommends -y supervisor && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY executor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY executor/.env /code/executor/
COPY executor/app /code/executor/app

EXPOSE 8080
ENTRYPOINT ["/usr/bin/supervisord", "-n"]
