#!/bin/bash

# Script to run Connect Four with optimized Phi-2 settings for CPU

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Connect Four with Ultra-Optimized Phi-2 for CPU ===${NC}"

# Set the path to the Phi-2 model (smaller and more efficient than Mistral-7B)
export LOCAL_LLM_PATH=~/models/phi-2

# Enable use of local LLM
export USE_LOCAL_LLM=true

# Use CPU optimizations instead of quantization
export LLM_QUANTIZATION=none

# Set PyTorch to use smaller memory footprint
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64

# Optimize memory cleanup
export CUDA_LAUNCH_BLOCKING=1

# Speed up tokenizer
export TOKENIZERS_PARALLELISM=true

# Limit PyTorch threads to improve latency
export OMP_NUM_THREADS=2

# Mac-specific optimizations (if available)
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0

# Set memory limit to prevent OOM errors
# Much smaller context window to prevent hangs - Phi-2 works well with small contexts
export MAX_CONTEXT_LENGTH=128

# Shorter timeout for faster responses
export GENERATION_TIMEOUT=5

# Enable aggressive garbage collection
export PYTHONMALLOC=debug

# Force CPU mode only
export FORCE_CPU=true

# Enable Python's built-in garbage collection
export PYTHONGC=1

echo -e "${GREEN}Starting Connect Four with Phi-2 memory-optimized settings:${NC}"
echo "• Model path: $LOCAL_LLM_PATH"
echo "• Memory optimization: Ultra"
echo "• Maximum context length: $MAX_CONTEXT_LENGTH tokens (ultra-small)"
echo "• Thread limit: $OMP_NUM_THREADS threads" 
echo "• Generation timeout: $GENERATION_TIMEOUT seconds"
echo -e "${YELLOW}Note: Phi-2 is smaller and more efficient than Mistral-7B, but still creative${NC}"

echo -e "\n${YELLOW}Game is starting...${NC}"
echo -e "${RED}If the game hangs, press Ctrl+C to exit and try run_basic_game.sh instead${NC}"

# Run the game (without memory profiler which isn't installed)
python main.py

echo -e "\n${GREEN}Game exited.${NC}" 