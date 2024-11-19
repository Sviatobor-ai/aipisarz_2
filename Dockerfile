# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy project files
COPY ./pyproject.toml ./poetry.lock* /app/

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy application code
COPY ./app /app/app

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
