#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE} Starting LieAI Stack with Docker Compose...${NC}"

# 1. Start containers in detached mode
docker-compose up -d

# 2. Check if the start command was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN} Containers started successfully!${NC}"
    
    # 3. Show current status of services
    echo -e "${YELLOW}--- Service Status ---${NC}"
    docker-compose ps
    
    echo -e "\n${BLUE} Access Points:${NC}"
    echo -e " FastAPI:    http://localhost:8000"
    echo -e " Jupyter:    http://localhost:8888"
    echo -e " Streamlit:  http://localhost:8501"
    echo -e " Qdrant UI:  http://localhost:6333/dashboard"
    
    echo -e "\n${YELLOW} Pro-tip: Run './run.sh logs' (if you add log logic) or 'docker-compose logs -f' to see real-time output.${NC}"
else
    echo -e "${RED} Failed to start containers. Check your docker-compose.yml file.${NC}"
    exit 1
fi