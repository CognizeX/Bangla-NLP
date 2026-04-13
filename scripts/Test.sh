#!/bin/bash

# Colors for terminal output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE} Running Unit Tests inside nlp-container...${NC}"

# 1. Check if the container is running
if [ ! "$(docker ps -q -f name=nlp-container)" ]; then
    echo -e "${YELLOW}  Container is not running. Starting it temporarily...${NC}"
    docker-compose up -d nlp
fi

# 2. Execute Pytest
# -v: Verbose output
# --maxfail=3: Stop after 3 failures to save time
echo -e "${BLUE} Executing: pytest -v --maxfail=3${NC}"
docker-compose exec nlp pytest -v --maxfail=3

# 3. Capture exit code
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN} ALL TESTS PASSED! Your NLP logic is solid.${NC}"
else
    echo -e "${RED} TESTS FAILED! Check the traceback above.${NC}"
    exit $RESULT
fi