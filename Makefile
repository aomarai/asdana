.PHONY: build run stop clean logs shell help

# Docker image name
IMAGE_NAME=asdana
CONTAINER_NAME=asdana-bot

# Default target
help:
	@echo "Available targets:"
	@echo "  build        - Build the Docker image"
	@echo "  run          - Run the bot container (requires environment variables)"
	@echo "  stop         - Stop and remove the bot container"
	@echo "  clean        - Remove Docker image and container"
	@echo "  logs         - View bot container logs"
	@echo "  shell        - Open a shell in the running container"
	@echo ""
	@echo "Example: make build && make run"

# Build the Docker image
build:
	@echo "Building Docker image..."
	docker build -t $(IMAGE_NAME):latest .

# Run the bot container
# Environment variables should be provided via .env file or -e flags
run:
	@echo "Starting bot container..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		--restart unless-stopped \
		--env-file .env \
		$(IMAGE_NAME):latest

# Stop and remove the container
stop:
	@echo "Stopping bot container..."
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Clean up Docker resources
clean: stop
	@echo "Removing Docker image..."
	docker rmi $(IMAGE_NAME):latest || true

# View container logs
logs:
	docker logs -f $(CONTAINER_NAME)

# Open a shell in the running container
shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash
