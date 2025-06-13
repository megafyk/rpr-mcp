#!/bin/bash

# Docker build and run script for rpr-mcp

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

IMAGE_NAME="rpr-mcp"
CONTAINER_NAME="rpr-mcp-container"

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the container (builds if needed)"
    echo "  stop      Stop the running container"
    echo "  logs      Show container logs"
    echo "  shell     Open shell in running container"
    echo "  clean     Remove container and image"
    echo "  help      Show this help message"
}

build_image() {
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t $IMAGE_NAME .
    echo -e "${GREEN}Image built successfully!${NC}"
}

run_container() {
    # Check if container is already running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        echo -e "${YELLOW}Container is already running!${NC}"
        return
    fi

    # Check if image exists
    if ! docker images -q $IMAGE_NAME | grep -q .; then
        echo -e "${YELLOW}Image not found, building...${NC}"
        build_image
    fi

    echo -e "${YELLOW}Starting container...${NC}"
    docker run -d \
        --name $CONTAINER_NAME \
        -p 8000:8000 \
        --env-file .env \
        $IMAGE_NAME

    echo -e "${GREEN}Container started successfully!${NC}"
    echo -e "${GREEN}Application available at: http://localhost:8000${NC}"
}

stop_container() {
    echo -e "${YELLOW}Stopping container...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    echo -e "${GREEN}Container stopped and removed!${NC}"
}

show_logs() {
    docker logs -f $CONTAINER_NAME
}

open_shell() {
    docker exec -it $CONTAINER_NAME /bin/bash
}

clean_all() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    stop_container
    docker rmi $IMAGE_NAME 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete!${NC}"
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_all
        ;;
    help|*)
        show_help
        ;;
esac
