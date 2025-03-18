# ConquestFour: AI-Powered Narrative Connect Four
On-Device AI Hackathon co-hosted by Qualcomm Technologies, Microsoft, and Northeastern University

![ConquestFour Logo](assets/images/logo.png)

> A narrative-driven Connect Four game powered by local LLMs that react to your moves with dynamic storytelling.

## Overview

ConquestFour transforms the classic Connect Four game into an immersive narrative experience using local large language models. Instead of reinventing the wheel, we've enhanced a familiar game with AI-powered storytelling that runs entirely on your device - no internet connection required!

The game features an intelligent AI opponent that not only challenges your strategic thinking but also narrates the game with contextual commentary, adapting its tone based on your play style and move quality.

## Features

- **Intelligent AI Opponent**: Three difficulty levels (Easy, Medium, Hard) with different play styles
- **Narrative Generation**: LLM provides contextual commentary on moves using Mistral-7B
- **Thermal Management**: Automatically detects system temperature and scales AI operations
- **Themed Experience**: Narratives adapt to different contextual themes (Western, Fantasy, Sci-Fi)
- **Interactive Chat**: Communicate directly with the AI during gameplay
- **Local Processing**: All AI processing runs locally - no data leaves your device

## Screenshots

![Gameplay Screenshot](assets/images/gameplay.png)
![Narrative Example](assets/images/narrative.png)

## Installation

### Prerequisites

- Python 3.9-3.12 (Do not go pass 3.12 or compatibility issues)
- [Ollama](https://ollama.com/) - for running local LLMs
- FFmpeg (for speech features)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/llm-conquestfour.git
   cd llm-conquestfour
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install and start Ollama:
   ```bash
   # Install from https://ollama.com/
   # Then run:
   ollama serve
   ```

5. Download the Mistral model:
   ```bash
   # In a separate terminal
   ollama pull mistral
   ```

### Windows-Specific Setup

For Windows users, we provide automated setup scripts:

```bash
# Using Git Bash
./demo/setup_windows_gitbash.sh

# Or using Command Prompt
demo\run_game_windows.bat
```

See [Windows Setup Guide](demo/WINDOWS_SETUP.md) for detailed instructions.

## Usage

### Starting the Game

# Game Title (Replace with your actual game title)

## Getting Started

This section outlines how to set up and run the game.

### Prerequisites

* Python (Specify version if necessary, e.g., Python 3.8+)
* pip (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [repository URL]
    cd [repository directory]
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the Game

To start the game, execute the following command:

```bash
python main.py

### Game Controls

- Click on a column to drop your piece
- Use the chat box to communicate with the AI narrator
- Select different themes and difficulty levels in the settings menu

## Technical Architecture

ConquestFour is built with a modular architecture:

1. **Game Logic Core**: Python implementation with minimax algorithm and alpha-beta pruning
2. **UI Layer**: PyQt6-based responsive user interface
3. **AI Engine**: Local LLM integration via Ollama (Mistral-7B)
4. **Narrative System**: Context-aware prompt generation with themed templates
5. **System Monitoring**: Thermal-aware performance adjustment

```
├── ai/               # AI and LLM integration
├── game/             # Core game logic and minimax implementation
├── ui/               # PyQt6 user interface
├── speech_to_text/   # Speech recognition (optional)
├── text_to_speech/   # Text-to-speech synthesis (optional)
├── templates/        # Narrative templates
└── assets/           # Game assets and images
```

## Planned Features

- **Voice Integration**: Speech-to-text and text-to-speech for natural conversation
- **NPU Acceleration**: Optimizations for neural processing units
- **Dynamic Difficulty**: AI that learns from your play style
- **Extended Narrative Memory**: AI remembers previous games
- **Expanded Themes**: Additional themes with unique narrative styles

## Troubleshooting

### Common Issues

- **"Connection refused" error**: Make sure Ollama is running (`ollama serve`)
- **"Model 'mistral' not found"**: Download the model (`ollama pull mistral`)
- **Performance issues**: Check system temperature, the game will automatically reduce computational load

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for a 24-hour Hackathon
- Inspired by classic Connect Four gameplay
- Powered by [Ollama](https://ollama.com/) and [Mistral AI](https://mistral.ai/)
- UI built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
