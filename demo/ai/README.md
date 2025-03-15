# AI Module for Conquest Four

This module provides AI capabilities for the Conquest Four game, including narrative generation, model loading, and text generation.

## Directory Structure

```
ai/
├── __init__.py           # Module initialization
├── context_prompter.py   # Context generation for prompts
├── model_loader.py       # Original model loader (to be refactored)  
├── thermal_monitor.py    # System temperature monitoring
├── loaders/              # Model loaders for different LLM implementations
│   ├── __init__.py
│   └── ... (model-specific loaders)
├── narrators/            # Narrative generators
│   ├── __init__.py
│   ├── base_narrator.py  # Abstract base class for narrators
│   └── fallback_narrator.py # Simple template-based narrator
└── utils/                # Utility functions and helper classes
    └── __init__.py
```

## Components

### Narrators

The `narrators` package contains classes for generating game narratives:

- `BaseNarrator`: Abstract base class that defines the interface for all narrators
- `FallbackNarrator`: Simple template-based narrator that works without external models

### Loaders

The `loaders` package contains classes for loading different language models:

- These will be implemented as part of the ongoing refactoring effort
- Will include loaders for Mistral, Phi-2, and other models

### Utils

The `utils` package contains utility functions and helper classes:

- Will include common functions used across multiple components
- Performance monitoring, resource management, etc.

## Usage

To use the AI module in the game:

```python
from ai import UnifiedModelInterface

# Initialize the model interface
model = UnifiedModelInterface(model_path="/path/to/model")

# Generate a narrative
narrative = model.generate_narrative(
    current_player=1,
    move_column=3,
    game_phase="midgame"
)

# Clean up resources when done
model.cleanup_resources()
```

## Refactoring Status

The AI module is currently being refactored to improve:

1. **Modularity**: Breaking down the large `model_loader.py` into smaller, focused components
2. **Error Handling**: Better timeout protection and fallback mechanisms
3. **Resource Management**: Improved cleanup of resources
4. **Documentation**: Clear documentation and examples for each component

## Future Improvements

- Add more narrative themes and templates
- Implement additional model loaders for new LLM architectures
- Create a model benchmarking system
- Add more sophisticated text generation utilities 