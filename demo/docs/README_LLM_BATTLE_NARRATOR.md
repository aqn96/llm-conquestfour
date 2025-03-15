# LLM Battle Narrator for Connect Four

This document explains how to use the LLM-powered battle narrator feature in the Connect Four game.

## Overview

The LLM Battle Narrator enhances the gaming experience by providing dynamic, theme-based narratives for each move in the Connect Four game. It leverages a Large Language Model (LLM) API to generate contextually appropriate and engaging battle commentary based on the current game state and selected theme.

## Features

- **Theme-Based Narration**: Choose from multiple themes (fantasy, sci-fi, western) for diverse narration styles.
- **Context-Aware Commentary**: Narratives adapt to the current game state, recognizing threats, opportunities, and game-winning moves.
- **Dynamic Storytelling**: Each game tells a unique story, making every session different and engaging.
- **Fallback Mechanisms**: If LLM API is unavailable, falls back to local narrative generation.

## Setup

### Environment Variables

Set the following environment variables to configure the LLM battle narrator:

```bash
# Required: Your LLM API key
export LLM_API_KEY="your_api_key_here"

# Optional: Set to "true" to enable LLM narratives (default: "false")
export USE_LLM="true"
```

### Integration Points

The LLM battle narrator is integrated into the game through:

1. **ModelController**: Detects if LLM should be used and initializes the appropriate narrator.
2. **GameStateHandler**: Generates narratives based on the current game state.
3. **UI**: Displays the generated narrative in the game interface.

## Themes

The following themes are available for narrative generation:

### Fantasy Theme
- **Setting**: Medieval kingdom with magical elements
- **Player 1**: Knights of the Crystal Realm
- **Player 2**: Shadow Warlocks
- **Style**: Epic fantasy with magical terminology

### Sci-Fi Theme
- **Setting**: Futuristic space battle
- **Player 1**: Galactic Federation
- **Player 2**: Quantum Armada
- **Style**: High-tech terminology with space warfare elements

### Western Theme
- **Setting**: Wild West showdown
- **Player 1**: Sheriff's Posse
- **Player 2**: Outlaw Gang
- **Style**: Old West slang and cowboy terminology

## Technical Details

### LLMBattleNarrator Class

The `LLMBattleNarrator` class in `ai/llm_battle_narrator.py` handles:

- Theme selection and context initialization
- Game state analysis for narrative generation
- API communication with the LLM service
- Fallback narrative generation when needed

### LLMModelLoader Class

The `LLMModelLoader` class in `ai/llm_model_loader.py` manages:

- Loading the appropriate narrator based on environment configuration
- Caching responses for efficiency
- Handling theme changes
- Generating narratives through the appropriate mechanism

## Testing

A test script is provided to verify the LLM battle narrator:

```bash
# Set environment variables and run the test
export LLM_API_KEY="your_api_key_here"
export USE_LLM="true"
python test_llm_narrator.py
```

This will test the narrator with different themes and game scenarios, including regular moves, threats, and winning scenarios.

## Extending the Feature

To add new themes or enhance existing ones:

1. Add new theme definitions in the `LLMBattleNarrator._initialize_theme_context` method
2. Update the theme selection logic in the UI as needed
3. Test the new theme with various game scenarios

## Troubleshooting

- **No Narrative Generated**: Check if LLM_API_KEY is set correctly and USE_LLM is set to "true"
- **Generic Narratives**: The API might be rate-limited or unavailable; the system will fall back to local generation
- **Theme Not Applied**: Ensure the theme is properly selected in the UI and passed to the narrator

## Performance Considerations

The LLM API calls introduce a slight delay in narrative generation. For optimal performance:

- Response caching is implemented to avoid redundant API calls
- Thermal monitoring reduces AI complexity during high system temperatures
- Fallback to local generation ensures responsiveness even when API is unavailable 