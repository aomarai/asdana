#!/bin/bash
# Development container helper script
# Works on Linux, macOS, and Windows (Git Bash/WSL)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
CONTAINER_NAME="asdana-devcontainer"

# Detect docker compose command (with or without hyphen)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "Error: Docker Compose is not installed."
    echo "Please install Docker Desktop or Docker Compose."
    exit 1
fi

show_help() {
    echo "Asdana Development Container Helper"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       Build and start the development container"
    echo "  stop        Stop the development container"
    echo "  restart     Restart the development container"
    echo "  shell       Open a shell in the running container"
    echo "  logs        Show container logs"
    echo "  rebuild     Rebuild the container from scratch"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the dev environment"
    echo "  $0 shell    # Enter the container"
    echo "  $0 logs     # View logs"
}

start_container() {
    echo "Starting development container..."
    cd "$PROJECT_ROOT"
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d
    echo ""
    echo "✓ Development container started!"
    echo ""
    echo "To access the container:"
    echo "  $0 shell"
    echo ""
    echo "Or use:"
    echo "  docker exec -it $CONTAINER_NAME bash"
}

stop_container() {
    echo "Stopping development container..."
    cd "$PROJECT_ROOT"
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" down
    echo "✓ Container stopped"
}

restart_container() {
    stop_container
    start_container
}

open_shell() {
    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo "Error: Container is not running. Start it first with:"
        echo "  $0 start"
        exit 1
    fi
    
    echo "Opening shell in container..."
    docker exec -it "$CONTAINER_NAME" bash
}

show_logs() {
    cd "$PROJECT_ROOT"
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" logs -f
}

rebuild_container() {
    echo "Rebuilding development container..."
    cd "$PROJECT_ROOT"
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" down -v
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" build --no-cache
    $DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d
    echo "✓ Container rebuilt and started"
}

# Main script logic
case "${1:-help}" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    shell)
        open_shell
        ;;
    logs)
        show_logs
        ;;
    rebuild)
        rebuild_container
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo ""
        show_help
        exit 1
        ;;
esac
