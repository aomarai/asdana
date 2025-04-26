# .devcontainer/Dockerfile
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set workdir
WORKDIR /workspace

# Configure Poetry to not create virtual environments inside the project
RUN poetry config virtualenvs.in-project false

# Copy pyproject.toml and poetry.lock files (if they exist)
COPY pyproject.toml poetry.lock* /workspace/

# Install dependencies
RUN poetry install --no-root

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1
