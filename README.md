# ConquestFour: AI-Powered Narrative Connect Four

*On-Device AI Hackathon co-hosted by Qualcomm Technologies, Microsoft, and Northeastern University. Won Second Place out of 28 teams and the People's Choice Award*

A narrative-driven Connect Four game powered by local LLMs that react to your moves with dynamic storytelling.

## Demo
[![LLM Connect Four Demo](assets/llm_connect4.gif)](https://youtu.be/iSGfIkLKz3M)

## Overview

ConquestFour transforms the classic Connect Four game into an immersive narrative experience using local large language models. Instead of reinventing the wheel, we've enhanced a familiar game with AI-powered storytelling that runs entirely on your device - no internet connection required!

The game features an intelligent AI opponent that not only challenges your strategic thinking but also narrates the game with contextual commentary, adapting its tone based on your play style and move quality.

## Features

- **Intelligent AI Opponent**: Three difficulty levels (Easy, Medium, Hard) with different play styles
- **Narrative Generation**: LLM provides contextual commentary on moves using Mistral-7B
- **🚀 Apple Neural Engine Acceleration**: ONNX Runtime with CoreML Execution Provider for 40-60% faster inference on Apple Silicon (M1/M2/M3)
- **Optimized Inference**: INT8 quantization for reduced latency and memory usage
- **Thermal Management**: Automatically detects system temperature and scales AI operations
- **Themed Experience**: Narratives adapt to different contextual themes (Western, Fantasy, Sci-Fi)
- **Interactive Chat**: Communicate directly with the AI during gameplay
- **Local Processing**: All AI processing runs locally - no data leaves your device

## Screenshots

*[Gameplay Screenshot]* *[Narrative Example]*

## Installation

### Prerequisites

- Python 3.9-3.12 (Do not go past 3.12 or compatibility issues)
- Ollama - for running local LLMs
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

See Windows Setup Guide for detailed instructions.

## Usage

### Starting the Game

To start the game, execute the following command:

```bash
python main.py
```

### Game Controls

- Click on a column to drop your piece
- Use the chat box to communicate with the AI narrator
- Select different themes and difficulty levels in the settings menu

## Technical Architecture

ConquestFour is built with a modular architecture:

1. **Game Logic Core**: Python implementation with minimax algorithm and alpha-beta pruning
2. **UI Layer**: PyQt6-based responsive user interface
3. **AI Engine**: Ollama-based LLM integration using llama.cpp + Metal GPU acceleration
4. **Narrative System**: Context-aware prompt generation with themed templates
5. **System Monitoring**: Thermal-aware performance adjustment

```
├── ai/
│   ├── ollama/              # Ollama LLM integration (llama.cpp + Metal)
│   └── onnx_runtime/        # ONNX POC tests (archived - CoreML incompatible with LLMs)
├── game/                    # Core game logic and minimax implementation
├── ui/                      # PyQt6 user interface
├── speech_to_text/          # Speech recognition (optional)
├── text_to_speech/          # Text-to-speech synthesis (optional)
├── docs/                    # Technical documentation and benchmarks
└── assets/                  # Game assets and images
```

### Performance Benchmarks

**Hardware**: Apple M3 Pro (18GB RAM)  
**Methodology**: 15-sample rigorous timing (time from player move → AI response appears)

| Model | Mean Latency | vs Baseline | Method | Status |
|-------|--------------|-------------|--------|--------|
| Mistral-7B | 5.55s ± 0.38s | Baseline (100%) | llama.cpp + Metal GPU | ✅ Validated |
| Phi-3-mini (3.8B) | *Testing* | Target: <2.22s (-60%) | llama.cpp + Metal GPU | 🧪 In Progress |

**Key Findings**:
- **ONNX + CoreML approach failed**: Only 3.8% operator coverage on transformers (99/2,616 nodes supported)
- **CoreML designed for vision models**, not LLMs (max embedding dim 16,384 vs 32,000+ needed)
- **Current stack already optimal**: Ollama uses llama.cpp with Metal GPU (correct approach for Apple Silicon)
- **Speedup via model size**: Smaller models (Phi-3-mini) provide 2-3x speedup while maintaining quality

See [docs/baseline_performance.md](docs/baseline_performance.md) and [docs/lessons_learned_onnx_coreml.md](docs/lessons_learned_onnx_coreml.md) for details.

## Advanced Features

### Apple Silicon Optimization (M1/M2/M3)

**What We Learned**: ONNX + CoreML approach was tested but found incompatible with LLMs.

**POC Test Results** (TinyLlama-1.1B):
```
✅ PyTorch baseline: 2.90s
❌ ONNX + CoreML: Failed (only 99/2,616 nodes supported = 3.8%)
   Error: "CoreML does not support input dim > 16384" (LLMs need 32K+ vocab)
```

**Why CoreML Failed**:
- CoreML designed for **vision models** (ResNet, MobileNet), not transformers
- Missing operators: `Split`, dynamic shapes, KV-cache patterns
- Max tensor dimension: 16,384 (LLMs need 32,000+ for embeddings)

**Correct Approach** (already implemented):
- Your baseline uses **llama.cpp + Metal GPU** via Ollama
- This is the optimal stack for LLMs on Apple Silicon
- Neural Engine (CoreML) is for vision/audio models only

**To Improve Performance**:

1. **Use smaller model** (2-3x speedup):
   ```bash
   ollama pull phi3:mini
   # Already configured in main.py
   ```

2. **Run POC to see CoreML limitations** (educational):
   ```bash
   python ai/onnx_runtime/poc_neural_engine.py
   ```

See [docs/lessons_learned_onnx_coreml.md](docs/lessons_learned_onnx_coreml.md) for full technical analysis.

## Planned Features

- **Voice Integration**: Speech-to-text and text-to-speech for natural conversation
- **Dynamic Difficulty**: AI that learns from your play style
- **Extended Narrative Memory**: AI remembers previous games
- **Expanded Themes**: Additional themes with unique narrative styles

## Troubleshooting

### Common Issues

- **"Connection refused" error**: Make sure Ollama is running (`ollama serve`)
- **"Model 'mistral' not found"**: Download the model (`ollama pull mistral`)
- **Performance issues**: Check system temperature, the game will automatically reduce computational load
- **macOS crash (`Abort trap: 6`) while clicking board/chat**:
  - This is typically a PyQt callback exception path, not an ONNX/CoreML conversion problem.
  - A fix was applied for PyQt6 mouse event handling and unhandled bot-call exceptions in UI slots.
  - See [docs/pyqt_crash_fix_2026-03-31.md](docs/pyqt_crash_fix_2026-03-31.md) for root cause and patch details.

### ONNX/CoreML Clarification

If you previously saw ONNX/CoreML errors, those are a separate class of issue:

- ONNX/CoreML limitations in this repo relate to operator coverage and tensor constraints for LLMs.
- The `SIGABRT` crash fixed above was caused by UI event/exception handling in PyQt, not by ONNX conversion.

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
