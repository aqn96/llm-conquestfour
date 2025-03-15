#!/bin/bash

# Set colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set the model path - use environment variable if set, otherwise use default
MODEL_PATH=${LOCAL_LLM_PATH:-"$HOME/models/mistral-7b"}

# Print header
echo -e "${BLUE}=== Connect Four with Refactored AI Module ===${NC}"
echo -e "Starting Connect Four with our new modular AI architecture:"
echo -e "• ${GREEN}Model path: ${MODEL_PATH}${NC}"
echo -e "• ${GREEN}Memory optimization: Yes${NC}"
echo -e "• ${GREEN}Modular components: Loaders, Narrators, Utils${NC}"
echo -e "• ${GREEN}Improved resource cleanup${NC}"

# Set up environment variables
export LOCAL_LLM_PATH="$MODEL_PATH"
export USE_LOCAL_LLM="true"
export MODEL_TYPE="mistral"  # Default model type
export GENERATION_TIMEOUT="5"  # 5 seconds timeout

# Mac-specific optimizations
if [[ "$(uname)" == "Darwin" ]]; then
    echo -e "• ${BLUE}Applying Mac-specific optimizations${NC}"
    # Limit number of threads for better performance on Mac
    export OMP_NUM_THREADS=2
    export MKL_NUM_THREADS=2
    # Set PyTorch to use CPU
    export PYTORCH_DEVICE="cpu"
fi

# Check if mistral model directory exists
if [ ! -d "$MODEL_PATH" ]; then
    echo -e "${RED}Error: Model path does not exist: $MODEL_PATH${NC}"
    echo -e "Please set LOCAL_LLM_PATH environment variable to your model directory"
    echo -e "Example: ${YELLOW}export LOCAL_LLM_PATH=~/models/mistral-7b${NC}"
    exit 1
fi

# Make sure script is executed from the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

# Create the virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start the game
echo -e "${GREEN}Game is starting...${NC}"
echo -e "${YELLOW}If the game hangs, press Ctrl+C to exit${NC}"
python main.py

# Print exit message
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Game exited.${NC}"
else
    echo -e "${RED}Game crashed with error code $?${NC}"
    echo -e "${YELLOW}Check the logs above for more information${NC}"
fi 