#!/bin/bash
# Windows setup script for Connect Four (Git Bash version)
# This script sets up everything needed to run the demo on Windows

# Set colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Connect Four Game Setup - Windows (Git Bash) ===${NC}"
echo -e "This script will set up all dependencies needed to run the demo."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# --------------------
# Check for Python
# --------------------
echo -e "${YELLOW}Checking for Python...${NC}"
if ! command -v python --version &> /dev/null; then
    echo -e "${RED}Python not found. Please install Python 3.9+ from https://www.python.org/downloads/windows/${NC}"
    echo -e "${YELLOW}Make sure to check 'Add Python to PATH' during installation.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}Found $PYTHON_VERSION${NC}"

# --------------------
# Set up model directory
# --------------------
MODEL_DIR="$HOME/models/mistral-7b"
echo -e "${YELLOW}Setting up model directory at $MODEL_DIR${NC}"
mkdir -p "$MODEL_DIR"

# --------------------
# Create virtual environment
# --------------------
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python -m venv venv
    # In Git Bash, we need to use the UNIX-style path for activation
    source venv/Scripts/activate
    
    echo -e "${GREEN}Virtual environment created and activated${NC}"
else
    source venv/Scripts/activate
    echo -e "${GREEN}Using existing virtual environment${NC}"
fi

# --------------------
# Install Python dependencies
# --------------------
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# --------------------
# Check for FFmpeg
# --------------------
echo -e "${YELLOW}Checking for FFmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}FFmpeg not found.${NC}"
    echo -e "${YELLOW}Please install FFmpeg manually:${NC}"
    echo -e "${YELLOW}1. Download from https://ffmpeg.org/download.html#build-windows${NC}"
    echo -e "${YELLOW}2. Extract to a directory${NC}"
    echo -e "${YELLOW}3. Add the bin directory to your PATH${NC}"
    echo -e "${YELLOW}Alternatively, if you have Chocolatey installed, run:${NC}"
    echo -e "${YELLOW}   choco install ffmpeg${NC}"
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
    echo -e "${GREEN}Found $FFMPEG_VERSION${NC}"
fi

# --------------------
# Download model if needed
# --------------------
echo -e "${YELLOW}Checking for model files...${NC}"
MODEL_FILES=("config.json" "tokenizer.json" "tokenizer_config.json" "pytorch_model.bin")
MISSING_FILES=0

for FILE in "${MODEL_FILES[@]}"; do
    if [ ! -f "$MODEL_DIR/$FILE" ]; then
        MISSING_FILES=$((MISSING_FILES+1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo -e "${YELLOW}Some model files are missing. Would you like to download them? (y/n)${NC}"
    read -r DOWNLOAD_CHOICE
    
    if [[ $DOWNLOAD_CHOICE == "y" || $DOWNLOAD_CHOICE == "Y" ]]; then
        echo -e "${YELLOW}Downloading Mistral-7B model using download_model.py...${NC}"
        python download_model.py
    else
        echo -e "${YELLOW}Skipping model download. You'll need to provide the model files manually.${NC}"
    fi
else
    echo -e "${GREEN}Model files already exist in $MODEL_DIR${NC}"
fi

# --------------------
# Create a Windows-compatible batch wrapper
# --------------------
echo -e "${YELLOW}Creating Windows batch wrapper...${NC}"
cat > run_game_windows.bat << 'EOL'
@echo off
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set LOCAL_LLM_PATH=%USERPROFILE%\models\mistral-7b
set USE_LOCAL_LLM=true
set MODEL_TYPE=mistral
set GENERATION_TIMEOUT=5

:: Run the game
python main.py

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat
EOL

echo -e "${GREEN}Created run_game_windows.bat${NC}"

# --------------------
# Setup complete
# --------------------
echo -e "${GREEN}Setup complete!${NC}"
echo -e "You can now run the game using:"
echo -e "  ${YELLOW}1. Git Bash: ./run_refactored_game.sh${NC}"
echo -e "  ${YELLOW}2. Command Prompt: run_game_windows.bat${NC}"
echo -e ""
echo -e "${BLUE}If you encounter any issues, please check the WINDOWS_SETUP.md file.${NC}"

# Deactivate virtual environment
deactivate 