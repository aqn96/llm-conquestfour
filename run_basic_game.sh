#!/bin/bash

# Script to run Connect Four with basic fallback model (no LLM)

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Connect Four with Basic Fallback Mode ===${NC}"
echo -e "${YELLOW}This mode uses simple procedural narratives instead of the Mistral LLM.${NC}"
echo -e "${YELLOW}Use this if you experience memory issues with the full model.${NC}"

# Disable local LLM and force fallback mode
export USE_LOCAL_LLM=false

# Speed up tokenizer
export TOKENIZERS_PARALLELISM=true

# Run with standard thread count
export OMP_NUM_THREADS=4

echo -e "${GREEN}Starting Connect Four in fallback mode...${NC}"

# Run the game
python main.py

echo -e "\n${GREEN}Game exited.${NC}" 