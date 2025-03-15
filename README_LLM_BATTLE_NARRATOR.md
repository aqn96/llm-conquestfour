# LLM Battle Narrator for Connect Four

This document provides information about the LLM-powered battle narrator feature for the Connect Four game.

## Overview

The battle narrator uses a local LLM to generate thematic battle narratives as players make moves in the Connect Four game. It creates an immersive, story-driven experience by describing the game in terms of a thematic battle.

## Enhanced Storytelling Features

The battle narrator now includes advanced storytelling capabilities:

1. **Dynamic Faction Names**: Each new game generates unique, thematic faction names for both players, creating a consistent story identity.

2. **Story Context Generation**: At the start of each game, a 4-5 sentence narrative is generated that establishes:
   - Why the factions are in conflict
   - The setting of the battle
   - What's at stake in the conflict
   - A dramatic tone for the strategic battle

3. **Coherent Narrative Arc**: The system maintains a coherent story throughout the game by:
   - Tracking previous narrative elements to avoid repetition
   - Adjusting the story based on move quality (good, bad, neutral)
   - Building tension as the game progresses
   - Creating dramatic conclusions for winning moves

4. **Strategic Move Analysis**: The narrator evaluates moves as:
   - **Good moves**: Create winning threats, block opponent's potential wins, or win the game
   - **Bad moves**: Edge placements when better options exist, missed opportunities
   - **Neutral moves**: Standard development moves, center placements

## Supported Themes

The battle narrator supports multiple themes:
- Fantasy (magical realms, mystical powers)
- Sci-Fi (futuristic technology, space conflicts)
- Western (frontier battles, old west showdowns)

## Using the Local LLM

The battle narrator can use a local Mistral 7B model for generating narratives:

1. Make sure you have downloaded the model (see download_model.py)
2. Set environment variables:
   ```bash
   export USE_LOCAL_LLM=true
   export LOCAL_LLM_PATH="~/models/mistral-7b"
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Testing the Enhanced Narrator

To test the enhanced battle narrator:

```bash
USE_LOCAL_LLM=true LOCAL_LLM_PATH=~/models/mistral-7b python tests/test_dynamic_battle_narrator.py
```

This will demonstrate how the narrative evolves based on move quality and maintains a coherent story throughout the game. 