#!/bin/bash

# Colors for terminal output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}  Starting Docker Build for NLP Project...${NC}"

# 1. Clean up dangling images to save space (Optional but recommended for ML)
echo -e "${BLUE} Cleaning up old builds...${NC}"
docker image prune -f

# 2. Build the image
# We use --progress=plain to see the PyTorch/PyG installation details
echo -e "${BLUE}  Building nlp:latest...${NC}"
docker build -t nlp:latest .

# 3. Verify the build
if [ $? -eq 0 ]; then
    echo -e "${GREEN} Build Successful!${NC}"
    echo -e "${GREEN} Image 'nlp:latest' is ready for your GNN research.${NC}"
    docker images nlp:latest
else
    echo -e "${RED} Build Failed. Check the logs above for errors.${NC}"
    exit 1
fi