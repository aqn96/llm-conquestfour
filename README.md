# LLM GameMaster: Strategic Connect Four

A modern, AI-powered implementation of Connect Four with dynamic battle narration powered by LLM technology.

## Features

- **Strategic Gameplay**: Classic Connect Four with AI opponents of adjustable difficulty levels
- **LLM Battle Narration**: Dynamic, contextual battle narratives powered by LLM technology
- **Multiple Themes**: Choose between Fantasy, Sci-Fi, and Western themes
- **Thermal Monitoring**: Adaptive AI that responds to system temperature
- **Flexible Architecture**: Supports both local LLM models and cloud API models

## Requirements

- Python 3.8+
- PyQt6 for the graphical interface
- Additional requirements in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-conquestfour.git
   cd llm-conquestfour
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

### Standard Mode

Run the game in standard mode (using simpler narrative models):

```bash
python main.py
```

### Local LLM Mode

To use a locally-hosted LLM like Mistral 7B for narrative generation:

```bash
python main.py --use-local-llm --model-path "path/to/model"
```

Or set environment variables:

```bash
export USE_LOCAL_LLM=true
export LOCAL_LLM_PATH="path/to/model"
python main.py
```

## Game Modes and Difficulty

The game offers three difficulty levels:

- **Easy (Level 1-3)**: AI looks ahead 1 move, perfect for beginners
- **Medium (Level 4-7)**: AI looks ahead 3 moves, balanced challenge
- **Hard (Level 8-10)**: AI looks ahead 5 moves, serious challenge for experienced players

## LLM Narrative Themes

The game features three narrative themes:

- **Fantasy**: Battle between Crystal Lords and Shadow Keepers
- **Sci-Fi**: Conflict between Quantum Collective and Void Syndicate
- **Western**: Showdown between Desperados and Lawmen

## Project Structure

```
llm-conquestfour/
├── ai/                    # AI and LLM components
│   ├── model_loader.py    # Unified model loader
│   └── context_prompter.py # Context-aware prompt generation
├── app/                   # Main application code
│   ├── controllers/       # Game and UI controllers
│   ├── handlers/          # Event handlers
│   ├── ui/                # UI components
│   └── utils/             # Utility functions
├── game/                  # Core game logic
├── assets/                # Images and other assets
├── tests/                 # Test files
├── main.py                # Main entry point
└── requirements.txt       # Python dependencies
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run a specific test:

```bash
python tests/test_model_loader.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dynamic Battle Narrator

The Connect Four game now includes a Dynamic Battle Narrator that generates contextual, engaging narratives based on the quality of moves made by players. This feature:

- Analyzes move quality (good, bad, or neutral) based on strategic value
- Creates varied, non-repetitive narratives that reflect the game state
- Adjusts the story based on how good a player's move is
- Supports multiple themes (fantasy, sci-fi, western)
- Uses local LLM (Mistral 7B) for generation

### How It Works

The Dynamic Battle Narrator analyzes each move using these criteria:
- **Good moves**: Creating winning threats, blocking opponent's potential wins, or winning the game
- **Bad moves**: Edge placements when better options exist, missed opportunities
- **Neutral moves**: Standard development moves, center placements

### Testing the Feature

You can test the dynamic battle narrator using the provided test script:

```bash
# Set the path to your local LLM model
export LOCAL_LLM_PATH="~/models/mistral-7b"

# Run the test script
python tests/test_dynamic_battle_narrator.py
```

### Integration

The dynamic battle narrator is fully integrated with the existing game system:
- The `LocalLLMNarrator` class now analyzes move quality and generates appropriate narratives
- Past narratives are tracked to avoid repetition
- The model adapts the story based on the quality of moves by each player
