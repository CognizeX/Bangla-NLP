#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE} Shutting down server ${NC}"

# 1. Stop and remove containers, networks, and images defined in the compose file
# Note: This does NOT delete your named volumes (postgres_data, model_weights)
docker-compose down

# 2. Verify if containers are gone
if [ $? -eq 0 ]; then
    echo -e "${RED} All services stopped and containers removed.${NC}"
    
    # 3. Optional: Clean up dangling Docker resources to keep your system fast
    echo -e "${YELLOW} Cleaning up unused networks and build cache...${NC}"
    docker network prune -f
    
    echo -e "${BLUE}System is now clean. Ready for your next session!${NC}"
else
    echo -e "${RED} Failed to stop services cleanly. You might need to use 'docker kill'.${NC}"
    exit 1
fi