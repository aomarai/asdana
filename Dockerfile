# Use Python slim image
FROM python:3.12-slim AS build

# Set working directory
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock (if present) for efficient dependency installation
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure Poetry to create virtual environment in project
RUN poetry config virtualenvs.in-project true

# Install dependencies (excluding dev dependencies)
RUN poetry install --no-root --without dev,test

# Copy the rest of the application code
COPY . .

# Final runtime image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the application code and virtual environment from build stage
COPY --from=build /app /app

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Copy and set entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
