# LLM GameMaster: AI-Powered Connect Four

This project implements the game logic and AI components for an AI-powered Connect Four game with advanced features. It's designed as part of a larger system that integrates NPU-accelerated language models to create dynamic narratives around the game.

## Game Logic and AI Components

The project is organized into the following modules:

### Core Game Logic (`connect_four.py`)

- `ConnectFourGame`: Manages the game state, rules, and mechanics
- `Player`: Enum representing the players (EMPTY, ONE, TWO)

### AI Engines (`minimax.py`)

- `MinimaxEngine`: Implements the minimax algorithm with alpha-beta pruning
- `DepthLimitedMinimax`: A simplified version of the minimax engine for thermal management

### State Validation (`state_validator.py`)

- `StateValidator`: Uses the Z3 theorem prover to validate game states and properties

### Thermal Management (`thermal_aware_ai.py`)

- `ThermalMonitor`: Monitors system temperature
- `ThermalAwareAI`: Selects AI strategies based on system temperature

## Features

- **Advanced AI**: Minimax algorithm with alpha-beta pruning for optimal play
- **Formal Verification**: Z3-based state validation to ensure game correctness
- **Thermal Adaptation**: Dynamic AI strategy selection based on system temperature
- **Modular Design**: Clean separation of concerns between game logic and AI

## Requirements

- Python 3.8+
- NumPy
- Z3 Theorem Prover (`pip install z3-solver`)
- psutil (`pip install psutil`)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd connect-four-ai/game

# Install dependencies
pip install -r requirements.txt
```

## How to Use

The game components can be used independently or together. Here's a simple example:

```python
from connect_four import ConnectFourGame
from thermal_aware_ai import ThermalAwareAI

# Create a new game
game = ConnectFourGame()

# Create an AI that adapts to system temperature
ai = ThermalAwareAI()

# Make an AI move
col = ai.find_best_move(game)
game.make_move(col)
```

For a complete example with user interaction, run:

```bash
python game_example.py
```

## Integration Points for UI and Narrative Teams

### For UI Team

The game logic exposes these key methods for integration with the UI:

- `game.make_move(col)`: Make a move in the specified column
- `game.is_game_over()`: Check if the game is over
- `game.get_winner()`: Get the winner (if any)
- `game.get_valid_columns()`: Get the list of valid columns for moves

### For Narrative Team

The AI classes expose information about their decision-making process:

- `ai.find_best_move(game)`: Get the best move along with reasoning
- `ai.get_current_temperature()`: Get the current system temperature

## Project Structure

```
.
├── __init__.py
├── connect_four.py   # Core game logic
├── minimax.py        # Minimax AI with alpha-beta pruning
├── state_validator.py # Z3-based state validation
├── thermal_aware_ai.py # Temperature-adaptive AI
├── game_example.py   # Example command-line game
├── requirements.txt  # Dependencies
└── README.md        # This file
```

## Next Steps

This implementation focuses on the game logic and AI components. The following components would be integrated by other teams:

1. UI implementation using PyQt6
2. Narrative generation using Mistral-7B LLM
3. NPU acceleration and optimization
4. Full application integration

## License

[MIT License](LICENSE) 