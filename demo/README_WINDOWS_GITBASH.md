# Running Connect Four on Windows with Git Bash

This guide provides instructions on how to set up and run the Connect Four game on Windows using Git Bash.

## Quick Start

If you have Git Bash installed, simply:

1. Open Git Bash in the demo directory
2. Run the setup script:
   ```bash
   ./setup_windows_gitbash.sh
   ```
3. Run the game:
   ```bash
   ./run_refactored_game.sh
   ```

## Prerequisites

- [Git for Windows](https://git-scm.com/download/win) (which includes Git Bash)
- [Python 3.9+](https://www.python.org/downloads/windows/) (make sure to check "Add Python to PATH")
- [FFmpeg](https://ffmpeg.org/download.html#build-windows) (optional, required for speech)

## Manual Setup Steps

If the automatic setup script doesn't work, you can follow these manual steps:

1. Create models directory:
   ```bash
   mkdir -p ~/models/mistral-7b
   ```

2. Create and activate Python virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download model files (if needed):
   ```bash
   python download_model.py
   ```

5. Run the game:
   ```bash
   ./run_refactored_game.sh
   ```

## Running with Command Prompt

If you prefer using Windows Command Prompt instead of Git Bash, use the batch file created by the setup script:

```
run_game_windows.bat
```

## Troubleshooting

- **Python not found**: Make sure Python is in your PATH.
- **Permission errors**: Try running Git Bash as Administrator.
- **Model download issues**: Make sure you have internet access or download the model files manually.
- **Import errors**: Make sure all dependencies are installed in the virtual environment.

For more detailed setup instructions, see the `WINDOWS_SETUP.md` file. 