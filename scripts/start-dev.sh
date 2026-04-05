#!/bin/bash

# Project Management System Development Environment Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Project Management System Development  ${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker daemon first"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: docker-compose not found, trying docker compose${NC}"
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# Create necessary directories
mkdir -p nginx/ssl logs/{backend,frontend,nginx} monitoring

# Function to check service health
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Waiting for $service to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f $url > /dev/null 2>&1; then
            echo -e "${GREEN}$service is ready!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}Failed to start $service${NC}"
    return 1
}

# Stop any existing containers
echo -e "${YELLOW}Stopping any existing containers...${NC}"
$DOCKER_COMPOSE_CMD down

# Build and start containers
echo -e "${YELLOW}Building and starting development environment...${NC}"
$DOCKER_COMPOSE_CMD up -d --build

# Wait for services to be ready
echo -e "${YELLOW}Starting services...${NC}"
sleep 10

# Check backend service
check_service "Backend API" "http://localhost:8000/health" || exit 1

# Check frontend service (if available)
check_service "Frontend" "http://localhost:3000" || echo -e "${YELLOW}Frontend may still be starting...${NC}"

# Check MySQL service
echo -e "${YELLOW}Checking MySQL database...${NC}"
if docker exec project-mgr-mysql mysqladmin ping --silent; then
    echo -e "${GREEN}MySQL is ready!${NC}"
else
    echo -e "${YELLOW}MySQL is still starting...${NC}"
fi

# Display service information
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}        Development Services Ready        ${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Frontend (Vue 3):${NC}   http://localhost:3000"
echo -e "${YELLOW}Backend API:${NC}        http://localhost:8000"
echo -e "${YELLOW}API Documentation:${NC}  http://localhost:8000/docs"
echo -e "${YELLOW}Nginx Proxy:${NC}        http://localhost"
echo -e "${YELLOW}MySQL Admin:${NC}        http://localhost:8080"
echo -e "${YELLOW}PostgreSQL Admin:${NC}   http://localhost:5050"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Default credentials:${NC}"
echo -e "MySQL: root/rootpassword"
echo -e "PgAdmin: admin@projectmgr.local/admin123"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "  Stop services:   $DOCKER_COMPOSE_CMD down"
echo -e "  View logs:       $DOCKER_COMPOSE_CMD logs -f"
echo -e "  Restart backend: $DOCKER_COMPOSE_CMD restart backend"
echo -e "  Restart frontend: $DOCKER_COMPOSE_CMD restart frontend"
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}        Development Environment Ready!    ${NC}"
echo -e "${GREEN}========================================${NC}"

# Keep script running to show logs
echo -e "\n${YELLOW}Press Ctrl+C to stop viewing logs...${NC}"
echo -e "${YELLOW}To exit without stopping services, press Ctrl+C then Ctrl+D${NC}"
$DOCKER_COMPOSE_CMD logs -f