# Use an official Python runtime as a parent image
FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry using pip and clear cache
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"
RUN poetry config installer.max-workers 20

# Add Poetry to PATH
ENV PATH="/etc/poetry/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files from the root directory
COPY ./pyproject.toml ./poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the data_cdc and core directories
COPY ./src/data_cdc ./data_cdc
COPY ./src/core ./core

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Command to run the script
CMD poetry run python /app/data_cdc/cdc.py && tail -f /dev/null