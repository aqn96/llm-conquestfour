# Narrative Engine for Connect Four

This module adds an immersive storytelling experience to the Connect Four game by evaluating player moves and generating appropriate narrative prompts based on move quality (good, mediocre, or bad).

## Overview

The narrative engine:

1. Evaluates player moves using minimax and strategic heuristics
2. Classifies moves as "good", "mediocre", or "bad"
3. Generates appropriate narrative prompts for a local LLM
4. Supports multiple themes (fantasy, sci-fi)
5. Provides context-aware storytelling that evolves with gameplay

## Components

### MoveEvaluator

Analyzes player moves by comparing them to optimal AI moves and evaluating position strength.

```python
evaluator = MoveEvaluator()
move_quality = evaluator.evaluate_move(game, column)  # Returns 'good', 'mediocre', or 'bad'
```

### NarrativePromptGenerator

Creates contextually appropriate prompts for a local LLM based on move quality and game state.

```python
generator = NarrativePromptGenerator()
prompt = generator.generate_prompt(game, column, theme='fantasy')
```

### GameNarrator

High-level component that orchestrates move evaluation and narrative generation.

```python
narrator = GameNarrator(theme='fantasy')
prompt = narrator.generate_move_narrative(game, column)
```

## Integrating with Local LLMs

To integrate with your local LLM:

1. Replace the `get_llm_response()` function with code that calls your LLM of choice:

```python
def get_llm_response(prompt):
    # Example using llama-cpp-python
    from llama_cpp import Llama
    
    # Load your model (adjust parameters for your specific model)
    llm = Llama(model_path="path/to/your/model.gguf", n_ctx=2048)
    
    # Generate response
    response = llm.create_completion(
        prompt,
        max_tokens=200,
        temperature=0.7,
        stop=["User:", "\n\n"]
    )
    
    return response['choices'][0]['text']
```

2. Connect the narrative system to your game loop:

```python
# Initialize the narrator
narrator = GameNarrator(theme='fantasy')  # or 'scifi'

# When the player makes a move:
pre_move_game = game.copy()  # Save state before move
game.make_move(column)       # Make the move

# Generate narrative
prompt = narrator.generate_move_narrative(pre_move_game, column)
narrative = get_llm_response(prompt)

# Display the narrative to the player
print(narrative)
```

## Themes

The system supports two narrative themes:

- **Fantasy**: Crystal Kingdom vs. Shadow Empire on a mystical Crystal Grid
- **Sci-fi**: Quantum Alliance vs. Neural Collective in the digital Nexus-7

## Special Narrative Moments

The system also provides prompts for key game moments:

```python
# Game introduction
intro_prompt = narrator.generate_game_start_prompt()

# Game victory
victory_prompt = narrator.generate_victory_prompt(winner)

# Game draw
draw_prompt = narrator.generate_draw_prompt()
```

## Example Usage

See `narrative_game_example.py` for a complete working example that demonstrates:

- Integration with the Connect Four game logic
- Evaluating player moves and generating narratives
- Using mock LLM responses (replace with your actual LLM)
- Theming and special narrative moments

## Requirements

- A local LLM (like Llama, Mistral, etc.) for text generation
- The Connect Four game components from this project
- Python 3.7+

## Extending the System

To add new themes:

1. Add a new theme template method in `NarrativePromptGenerator`
2. Add faction names for the theme in `_player_factions`
3. Add handling for the theme in `GameNarrator`

To modify evaluation criteria:

1. Adjust the scoring thresholds in `MoveEvaluator.evaluate_move`
2. Enhance the strategic insights in `MoveEvaluator.get_move_insight` 