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
- **Narrative Director**: Story premise + opening/mid/end arc control driven by move quality signals
- **🍎 Apple Silicon Optimized Path**: Stable inference via Ollama + llama.cpp + Metal GPU backend (tested on Apple M3 Pro)
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
**Methodology**: Interactive timing from player move to AI response.

| Model | Mean Latency | vs Baseline | Method | Status |
|-------|--------------|-------------|--------|--------|
| Mistral-7B | 5.55s ± 0.38s | Baseline (100%) | llama.cpp + Metal GPU | ✅ Validated |
| Phi-3-mini (3.8B), run #1 (n=15) | 4.25s ± 0.49s | -23.4% | llama.cpp + Metal GPU | ✅ Measured |
| Phi-3-mini (3.8B), run #2 after latency tuning (n=15) | 4.45s ± 0.38s | -19.8% | llama.cpp + Metal GPU | ✅ Measured |
| Phi-3-mini combined (n=30) | 4.35s ± 0.31s | -21.6% | llama.cpp + Metal GPU | ✅ Measured |

**Key Findings**:
- **ONNX + CoreML approach failed**: Only 3.8% operator coverage on transformers (99/2,616 nodes supported)
- **CoreML designed for vision models**, not LLMs (max embedding dim 16,384 vs 32,000+ needed)
- **Current stack already optimal**: Ollama uses llama.cpp with Metal GPU (correct approach for Apple Silicon)
- **Measured improvement**: Phi-3-mini + runtime tuning reduced mean latency from 5.55s to 4.35s across two runs (~21.6% faster, n=30)
- **Consistency gain**: latest run stayed below 6s (max 5.35s), removing prior long-tail spikes
- **Where time goes**: minimax move/eval is typically sub-150ms; LLM generation dominates end-to-end latency

### Instrumented Trace (Aggressive personality, n=15)

From `[perf]` logs:
- `llm_chat_ms`: mean `4011.8ms`, min `2965.8ms`, max `4933.8ms`, stdev `759.0ms`
- `minimax_ai_move_ms`: mostly `0.5ms` to `133.7ms`
- `minimax_eval_ms`: mostly `2.6ms` to `40.9ms`

Interpretation:
- The game logic path is fast and stable.
- Most variance comes from LLM output length/style and prompt complexity, not minimax.

### Narration Policy (Latency/Memory Tradeoff)

- The app uses **one LLM narrator voice** (`Gemma`) for move-by-move storytelling.
- If player reactions are added, prefer **rule-based templates** for `good`/`mediocre`/`bad` events.
- Avoid a second per-move LLM call for "Andrew replies" by default:
  - doubles token generation load,
  - increases latency variance,
  - grows history faster and can cause style drift.
- Reserve LLM player text for explicit user input (typed or spoken chat).

### Platform Guidance

- **macOS (Apple Silicon)**: Prefer `Ollama + llama.cpp + Metal` (default in this repo).
- **Windows/Linux**: ONNX can be a good deployment path when paired with a strong execution provider (for example TensorRT/CUDA/DirectML), but performance depends on provider coverage for transformer ops.
- **This repo's ONNX/CoreML path** remains experimental/research-only for LLMs on macOS.

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

### Runtime Backend Selection

The game now supports backend selection in the startup UI:

- `Auto (Recommended)`: Uses stable Ollama + llama.cpp + Metal
- `Ollama + Metal (Stable)`: Forces stable backend
- `Apple NPU / CoreML (Experimental)`: Attempts ONNX/CoreML only when Apple M3 is detected, otherwise falls back to stable backend

Notes:
- Experimental NPU mode is for research and may be slower or less stable for LLM inference.
- If ONNX/CoreML initialization fails, the app automatically falls back to stable Ollama/Metal.
- Optional env vars for experimental mode:
  - `CONQUEST4_ONNX_MODEL_PATH` (default: `models/mistral-onnx`)
  - `CONQUEST4_USE_NEURAL_ENGINE` (`1` by default)

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
For a deeper practical explanation, see [docs/onnx_coreml_deep_dive.md](docs/onnx_coreml_deep_dive.md).
For narrative quality controls, see [docs/narrative_coherence.md](docs/narrative_coherence.md).

### Quick Learning Recap

- ONNX is a model exchange format, not a guaranteed performance layer by itself.
- For this app's LLM inference on Apple Silicon, **GPU via Metal** is the stable path.
- The stable runtime here is **Ollama + llama.cpp + Metal** (not CoreML/NPU).
- This path is GPU-accelerated (not CPU-only "bare metal").
- eBPF is unrelated to this inference stack.

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
- **Experimental NPU mode selected but not used**:
  - This is expected unless Apple M3 is detected and ONNX/CoreML initializes successfully.
  - The app falls back automatically to stable Ollama + llama.cpp + Metal.
  - Check startup notice dialog and terminal logs for resolved backend.

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
