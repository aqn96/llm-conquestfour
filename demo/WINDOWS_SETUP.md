# Windows Setup Guide

This guide will help you set up and run the Connect Four game on Windows.

## Prerequisites

Before you start, ensure you have the following installed:

1. **Python 3.9+**: Download and install from the [official Python website](https://www.python.org/downloads/windows/).
   - Make sure to check "Add Python to PATH" during installation.

2. **FFmpeg**: Required for audio processing.
   - Download from [FFmpeg.org](https://ffmpeg.org/download.html#build-windows) or install using [Chocolatey](https://community.chocolatey.org/packages/ffmpeg): `choco install ffmpeg`
   - Add FFmpeg to your PATH

3. **Git** (optional): Download from [git-scm.com](https://git-scm.com/download/win) if you want to clone the repository.

## Setup Steps

1. **Clone or download the repository**:
   ```
   git clone [repository-url]
   cd llm-conquestfour/demo
   ```

2. **Prepare the Mistral-7B model**:
   - Create a models directory:
     ```
     mkdir %USERPROFILE%\models\mistral-7b
     ```
   - Download the model files using the provided script:
     ```
     python download_model.py
     ```
   - Alternatively, set the `LOCAL_LLM_PATH` environment variable to point to your model:
     ```
     set LOCAL_LLM_PATH=C:\path\to\your\model
     ```

3. **Run the setup script**:
   - Right-click on `run_refactored_game.bat` and select "Run as administrator"
   - This will create a virtual environment and install all required dependencies

## Running the Game

After setup is complete, you can run the game by:

1. Double-clicking `run_refactored_game.bat`
   - This script activates the virtual environment and starts the game

## Troubleshooting

### Common Issues:

1. **Color codes not working in Windows console**:
   - Try using Windows Terminal instead of the default command prompt
   - Or modify the .bat file to remove color codes

2. **"Python is not recognized as an internal or external command"**:
   - Ensure Python is added to your PATH environment variable

3. **Module import errors**:
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

4. **GPU acceleration issues**:
   - The game is configured to use CPU by default on Windows
   - For GPU support, install appropriate CUDA drivers and PyTorch with CUDA support

5. **FFMPEG not found**:
   - Ensure FFmpeg is installed and added to your PATH
   - Restart your command prompt after installation

## Advanced Configuration

Set these environment variables for custom configurations:

- `LOCAL_LLM_PATH`: Path to your local language model
- `USE_LOCAL_LLM`: Set to "true" to use local LLM instead of API
- `MODEL_TYPE`: Model type (default: "mistral")
- `GENERATION_TIMEOUT`: Timeout in seconds for model generation

Example:
```
set LOCAL_LLM_PATH=C:\models\custom-model
set USE_LOCAL_LLM=true
set MODEL_TYPE=llama
set GENERATION_TIMEOUT=10
``` 