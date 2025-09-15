@echo off
setlocal enabledelayedexpansion

:: Set colors for better readability
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: Set the model path - use environment variable if set, otherwise use default
if defined LOCAL_LLM_PATH (
    set "MODEL_PATH=%LOCAL_LLM_PATH%"
) else (
    set "MODEL_PATH=%USERPROFILE%\models\mistral-7b"
)

:: Print header
echo %BLUE%=== Connect Four with Refactored AI Module ===%NC%
echo Starting Connect Four with our new modular AI architecture:
echo • %GREEN%Model path: %MODEL_PATH%%NC%
echo • %GREEN%Memory optimization: Yes%NC%
echo • %GREEN%Modular components: Loaders, Narrators, Utils%NC%
echo • %GREEN%Improved resource cleanup%NC%

:: Set up environment variables
set "LOCAL_LLM_PATH=%MODEL_PATH%"
set "USE_LOCAL_LLM=true"
set "MODEL_TYPE=mistral"
set "GENERATION_TIMEOUT=5"

:: Windows-specific optimizations
echo • %BLUE%Applying Windows-specific optimizations%NC%
set "OMP_NUM_THREADS=2"
set "MKL_NUM_THREADS=2"
set "PYTORCH_DEVICE=cpu"

:: Check if mistral model directory exists
if not exist "%MODEL_PATH%" (
    echo %RED%Error: Model path does not exist: %MODEL_PATH%%NC%
    echo Please set LOCAL_LLM_PATH environment variable to your model directory
    echo Example: %YELLOW%set LOCAL_LLM_PATH=C:\models\mistral-7b%NC%
    exit /b 1
)

:: Make sure script is executed from the right directory
cd /d "%~dp0"

:: Create the virtual environment if it doesn't exist
if not exist "venv" (
    echo %YELLOW%Creating Python virtual environment...%NC%
    python -m venv venv
    call venv\Scripts\activate.bat
    echo %YELLOW%Installing requirements...%NC%
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: Start the game
echo %GREEN%Game is starting...%NC%
echo %YELLOW%If the game hangs, press Ctrl+C to exit%NC%
python main.py

:: Print exit message
if %ERRORLEVEL% EQU 0 (
    echo %GREEN%Game exited.%NC%
) else (
    echo %RED%Game crashed with error code %ERRORLEVEL%%NC%
    echo %YELLOW%Check the logs above for more information%NC%
)

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

endlocal 