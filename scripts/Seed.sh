#!/bin/bash

# Colors for terminal output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE} Initializing Data Seeding for LieAI...${NC}"

# 1. Check if the containers are running
if [ ! "$(docker ps -q -f name=nlp-container)" ]; then
    echo -e "${RED} Error: nlp-container is not running.${NC}"
    echo -e "${YELLOW}Please run ./run.sh first.${NC}"
    exit 1
fi

# 2. Run the seeding script inside the container
# This assumes you have a file at app/seed_data.py in your project
echo -e "${BLUE}📡 Executing seed_data.py inside the container...${NC}"

docker-compose exec nlp python app/seed_data.py

# 3. Final Check
if [ $? -eq 0 ]; then
    echo -e "${GREEN} Seeding completed successfully!${NC}"
    echo -e "${GREEN} Your Vector Database are now ready for research.${NC}"
else
    echo -e "${RED} Seeding failed. Check your Python script logic or database connections.${NC}"
    exit 1
fi