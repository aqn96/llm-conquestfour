# Local LLM Battle Narrator for Connect Four

This document explains how to use the locally-hosted LLM for battle narration in the Connect Four game.

## Overview

The Local LLM Battle Narrator enhances the Connect Four game by providing dynamic, themed battle narratives using a locally-hosted large language model (such as Mistral 7B). This approach doesn't require API calls to external services, giving you complete control over the narrative generation.

## Features

- **Completely Local**: Uses locally-hosted LLMs (like Mistral 7B) with no API calls or internet dependency
- **Theme-Based Narration**: Multiple themes (fantasy, sci-fi, western) for diverse narration styles
- **Context-Aware Commentary**: Narratives adapt to the current game state and board position
- **Thermal-Aware Processing**: Adapts to high system temperatures to prevent overheating

## Requirements

To use the Local LLM feature, you'll need:

1. **Python 3.8+**
2. **PyTorch**: For running the language model
3. **Transformers**: Hugging Face library for loading and running the model
4. **A compatible LLM model**: Such as Mistral 7B or similar downloaded to your local machine
5. **Sufficient hardware**: Running LLMs locally requires significant resources:
   - 8GB+ RAM (16GB+ recommended)
   - GPU with 8GB+ VRAM for faster inference (optional but recommended)
   - 10GB+ free disk space for model storage

## Setup

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Download a Model

Download a compatible model like Mistral 7B from Hugging Face:

```bash
# Create a directory for models
mkdir -p ~/models

# Download Mistral 7B using the Hugging Face CLI
huggingface-cli download mistralai/Mistral-7B-v0.1 --local-dir ~/models/mistral-7b
```

Or manually download from [Hugging Face](https://huggingface.co/mistralai/Mistral-7B-v0.1) and extract to your models directory.

### 3. Configure Environment Variables

Set the following environment variables to configure the Local LLM:

```bash
# Required: Path to your downloaded model
export LOCAL_LLM_PATH="~/models/mistral-7b"

# Optional: Set to "true" to enable local LLM (default: "false")
export USE_LOCAL_LLM="true"
```

## Running with Local LLM

Use the provided script to run the game with Local LLM enabled:

```bash
# Start the game with Local LLM narrator
python run_with_llm.py
```

## Performance Optimization

### CUDA Acceleration

If you have a compatible NVIDIA GPU, the system will automatically use CUDA to accelerate model inference. The first loading will be slightly slower as the model is optimized for your GPU.

### Lower Precision

The system automatically uses half-precision (FP16) if running on a GPU, which:
- Reduces memory usage by almost 50%
- Improves inference speed
- Maintains narrative quality

### Model Alternatives

For lower-resource systems, consider using smaller models:

- **Mistral 7B**: Good balance of quality and performance
- **Phi-2 (2.7B)**: Excellent performance on lower-end hardware
- **TinyLlama (1.1B)**: Works on systems with limited resources

To use an alternative model, simply download it and update the `LOCAL_LLM_PATH` environment variable.

## Troubleshooting

### Model Loading Issues

- **Error: "CUDA out of memory"**: Your GPU doesn't have enough VRAM. Try:
  - Using a smaller model
  - Setting `device_map="auto"` to allow CPU offloading (already configured)
  - Reducing batch size or sequence length

- **Error: "Cannot load tokenizer"**: Ensure your model directory contains the tokenizer files

### Slow Inference

If narrative generation is too slow:
- Try using a GPU if available
- Use a smaller model
- Consider quantized models (4-bit or 8-bit) for faster inference

### No Narratives Generated

- Check if the model is loaded successfully (see startup logs)
- Ensure the model path is correct
- Verify that the transformers library is installed

## Extending

### Adding New Models

To add support for a new model:

1. Download the model to your local machine
2. Update the `LOCAL_LLM_PATH` environment variable
3. The system will automatically adapt to the new model

### Custom Prompt Templates

You can modify the prompt templates in `LocalLLMNarrator._create_themed_prompt()` to get different styles of narration.

### New Themes

To add new themes:
1. Edit the `_initialize_theme_context` method in `LocalLLMNarrator`
2. Add your new theme with appropriate vocabulary and context
3. Update the UI theme selector to include your new theme 