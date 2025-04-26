# Use Python slim image
FROM python:3.12-slim AS build

# Set working directory
WORKDIR /asdana

# Copy only the pyproject.toml and poetry.lock (if present) for efficient dependency installation
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install poetry

# Install dependencies (excluding dev dependencies)
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . .

# Final runtime image
FROM python:slim

# Set the working directory
WORKDIR /asdana

# Copy the virtual environment from the build stage
COPY --from=build /asdana /asdana

# Set environment variables from runtime secrets or use .env files if necessary
ENV BOT_TOKEN=${BOT_TOKEN}
ENV BOT_DESCRIPTION=${BOT_DESCRIPTION}
ENV DB_NAME=${DB_NAME}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV YT_API_KEY=${YT_API_KEY}
ENV TESTING_GUILD_ID=${TESTING_GUILD_ID}

# Command to run the bot
CMD ["poetry", "run", "python", "main.py"]
