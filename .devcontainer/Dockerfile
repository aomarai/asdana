# .devcontainer/Dockerfile
FROM python:3.12-slim

# Install dependencies and PostgreSQL prerequisites
RUN apt-get update && apt-get install -y \
  curl \
  git \
  lsb-release \
  gnupg \
  && rm -rf /var/lib/apt/lists/*

# Add PostgreSQL repository
RUN sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
  && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg

# Install PostgreSQL 17.4
RUN apt-get update && apt-get install -y \
  postgresql-17 \
  postgresql-client-17 \
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

# After copying pyproject.toml and before running install
COPY pyproject.toml poetry.lock* ./
RUN poetry lock --no-update || true

# Install dependencies
RUN poetry install --no-root

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1
