#!/bin/bash

# Ultra-simple script to test just model loading with minimal settings

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Testing Mistral Model Loading ===${NC}"

# Set the path to the Mistral-7B model
export LOCAL_LLM_PATH=~/models/mistral-7b

# Add Mac-specific optimizations (if available)
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export OMP_NUM_THREADS=2

echo -e "${YELLOW}Testing if model can be loaded...${NC}"
echo "This will try to load the model with minimal settings and generate a tiny response."
echo "If this doesn't work, there might be an issue with your model installation."

# Run the test script
python test_model.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "\n${GREEN}Test completed successfully!${NC}"
    echo "The model appears to be working. You can try running the game with:"
    echo -e "${YELLOW}./run_optimized_game.sh${NC}"
else
    echo -e "\n${RED}Test failed!${NC}"
    echo "The model couldn't be loaded or generated text. You can try:"
    echo "1. Check if your model path is correct"
    echo "2. Run the game without the model: ./run_basic_game.sh"
fi 