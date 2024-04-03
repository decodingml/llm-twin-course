# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Upgrade pip and install Poetry
RUN python3 -m pip install --upgrade pip && pip3 install poetry

# Copy only the pyproject.toml and poetry.lock (if exists) to use Docker cache
COPY pyproject.toml poetry.lock* /usr/src/app/

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the rest of the application
COPY . /usr/src/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run cdc.py when the container launches
CMD ["python", "cdc.py"]
