# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Add Poetry to PATH
ENV PATH="/etc/poetry/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files from the root directory
COPY ./pyproject.toml ./poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the 2-data-ingestion and core directories
COPY ./2-data-ingestion ./2-data-ingestion
COPY ./core ./core

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Command to run the script
CMD poetry run python /app/2-data-ingestion/cdc.py && tail -f /dev/null