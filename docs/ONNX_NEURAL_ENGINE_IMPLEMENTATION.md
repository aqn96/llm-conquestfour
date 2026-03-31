# ONNX Runtime + Apple Neural Engine Implementation

## Overview

This document explains the implementation of ONNX Runtime with Apple Neural Engine acceleration for ConquestFour's LLM inference.

## Architecture

### Before (Baseline)
```
Game Move
  ↓
LLMBot (Python wrapper)
  ↓
Ollama API (REST)
  ↓
Ollama Server
  ↓
Mistral-7B (Ollama format)
  ↓
CPU Inference (llama.cpp)
  ↓
Response (5.55s mean)
```

### After (ONNX + Neural Engine)
```
Game Move
  ↓
ONNXBot (Python class)
  ↓
ONNX Runtime (Python API)
  ↓
CoreML Execution Provider
  ↓
Apple Neural Engine (ANE)
  ↓
Mistral-7B (ONNX INT8 format)
  ↓
Response (Target: <2.22s)
```

## Key Components

### 1. ONNX Runtime with CoreML EP
- **What**: Microsoft's cross-platform inference engine
- **Why**: Provides CoreML Execution Provider for Apple Silicon
- **How**: `onnxruntime-silicon` package optimized for M-series chips

### 2. Apple Neural Engine (ANE)
- **What**: Dedicated AI accelerator in M-series chips
- **Specs**: 16-core ANE in M3 Pro, up to 18 TOPS (trillion ops/sec)
- **Access**: Via CoreML framework through ONNX Runtime
- **Advantage**: Parallel execution, power-efficient, offloads CPU

### 3. Model Conversion Pipeline
```
HuggingFace Model (PyTorch)
  ↓ [optimum library]
ONNX Format (graph representation)
  ↓ [dynamic quantization]
INT8 Quantized ONNX
  ↓ [CoreML EP optimization]
ANE-optimized model
```

### 4. Quantization Strategy
- **Type**: Dynamic INT8 quantization
- **Method**: Per-channel quantization for accuracy
- **Benefits**:
  - 4x smaller model size (~7GB → ~1.75GB)
  - 2-4x faster inference
  - Better ANE utilization (ANE optimized for INT8)
- **Trade-offs**: Minimal quality loss (<2% perplexity increase)

## Implementation Details

### File Structure
```
ai/onnx_runtime/
├── __init__.py                    # Module initialization
├── onnx_bot.py                    # ONNXBot class (drop-in LLMBot replacement)
├── convert_mistral_to_onnx.py    # Model conversion script
└── verify_ane.py                  # Neural Engine verification

models/
└── mistral-onnx/                  # Converted ONNX models
    ├── model.onnx                 # ONNX graph
    ├── model_quantized.onnx       # INT8 quantized version
    ├── tokenizer.json             # Tokenizer config
    └── config.json                # Model config
```

### ONNXBot Class

**Purpose**: Drop-in replacement for LLMBot with identical interface

**Key Methods**:
- `__init__()`: Initialize model with ANE support
- `get_response_to_event()`: Generate narrative for game events
- `get_response_to_speech()`: Handle player chat
- `_generate_text()`: Core inference with ONNX Runtime

**Interface Compatibility**:
```python
# Works with both LLMBot and ONNXBot
bot = ONNXBot(model_path, name, opponent_name, personality_key="Snarky")
response = bot.get_response_to_event("Player makes a great move!")
```

### Model Conversion Process

**Script**: `convert_mistral_to_onnx.py`

**Steps**:
1. Load HuggingFace Mistral model
2. Export to ONNX format using Optimum
3. Apply INT8 dynamic quantization
4. Validate output matches PyTorch
5. Save to `models/mistral-onnx/`

**Usage**:
```bash
# Small model (recommended for 18GB RAM)
python ai/onnx_runtime/convert_mistral_to_onnx.py --model-size small

# With quantization (default)
python ai/onnx_runtime/convert_mistral_to_onnx.py --model-size small

# Without quantization (for comparison)
python ai/onnx_runtime/convert_mistral_to_onnx.py --model-size small --no-quantization
```

## Performance Optimization Techniques

### 1. Graph Optimization
```python
sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
```
Enables:
- Constant folding
- Operator fusion
- Dead code elimination
- Layout optimization

### 2. Execution Provider Ordering
```python
providers = ["CoreMLExecutionProvider", "CPUExecutionProvider"]
```
- Try CoreML (ANE) first
- Fallback to CPU if op unsupported
- Hybrid execution for best performance

### 3. Memory Management
- Model loaded once at startup
- Reuse session across inferences
- Efficient tokenization (minimal copying)

### 4. Quantization Benefits
- **Memory bandwidth**: 4x reduction → faster data transfer
- **Cache efficiency**: More model fits in cache
- **ANE optimization**: ANE designed for INT8 ops

## Apple Neural Engine Details

### What is the ANE?
The Apple Neural Engine is a dedicated matrix multiplication and convolution accelerator in M-series chips.

### Specs (M3 Pro)
- **Cores**: 16-core ANE
- **Performance**: Up to 18 TOPS (trillion operations per second)
- **Power**: ~5W typical (vs 20W+ for CPU inference)
- **Data types**: INT8, INT16, FP16 (optimized for INT8)

### What Operations Run on ANE?
Via CoreML Execution Provider:
- ✅ Matrix multiplications (transformer attention)
- ✅ Convolutions
- ✅ Activations (ReLU, GELU, etc.)
- ✅ Normalization (LayerNorm, BatchNorm)
- ⚠️  Some ops fall back to CPU (complex control flow)

### Monitoring ANE Usage
```bash
# Option 1: Activity Monitor
# View → Columns → Enable "Neural Engine"

# Option 2: powermetrics (requires sudo)
sudo powermetrics --samplers cpu_power,gpu_power,ane_power -i 1000

# Look for "ane" metrics showing non-zero values
```

### Verifying ANE Activation
```python
# Check which provider is actually used
actual_provider = session.get_providers()[0]
print(f"Using: {actual_provider}")  # Should be CoreMLExecutionProvider
```

## Limitations & Workarounds

### Limitation 1: Large Model Size
- **Issue**: Mistral-7B is ~7GB, may exceed ANE memory
- **Workaround**: INT8 quantization reduces to ~1.75GB
- **Alternative**: Use smaller model (Mistral-3B) if issues persist

### Limitation 2: Unsupported Ops
- **Issue**: Some LLM ops not fully supported by CoreML EP
- **Workaround**: Hybrid execution (ANE + CPU)
- **Impact**: Some layers run on CPU (acceptable)

### Limitation 3: First Inference Latency
- **Issue**: First inference slower (CoreML compilation)
- **Workaround**: Warmup inference at startup
- **Note**: Only affects first call, subsequent calls fast

### Limitation 4: Quantization Quality
- **Issue**: INT8 may degrade narrative quality
- **Workaround**: Per-channel quantization (better accuracy)
- **Validation**: Compare outputs before/after quantization

## Expected Performance Improvements

### Theoretical Analysis
1. **Model Size**: 4x smaller (7GB → 1.75GB)
   - Faster loading from disk/RAM
   - Better cache utilization

2. **Compute**: ANE acceleration
   - Matrix ops: 3-5x faster than CPU
   - Lower power → less thermal throttling

3. **Memory Bandwidth**: Reduced by 4x
   - Critical bottleneck on Apple Silicon

### Realistic Expectations
- **Best Case**: 60-70% reduction (5.55s → 1.67-2.22s)
- **Likely Case**: 40-50% reduction (5.55s → 2.78-3.33s)
- **Worst Case**: 25-30% reduction (5.55s → 3.89-4.16s)

### Why Not 10x Faster?
- Not all ops run on ANE (hybrid execution)
- Tokenization/decoding still on CPU
- Model size (7B parameters) inherently slow
- Generation is sequential (can't parallelize across tokens)

## Troubleshooting

### Model Not Using ANE
**Symptom**: `get_providers()[0]` returns `CPUExecutionProvider`

**Causes**:
1. CoreML EP not installed → reinstall `onnxruntime-silicon`
2. Model has unsupported ops → check ONNX compatibility
3. macOS < 11.0 → update OS

**Debug**:
```python
import onnxruntime as ort
print(ort.get_available_providers())  # Should list CoreMLExecutionProvider
```

### Slow First Inference
**Symptom**: First call takes 10+ seconds

**Cause**: CoreML compiling model for ANE

**Solution**: Normal behavior, add warmup:
```python
# Warmup inference at startup
bot._generate_text("Hello", max_new_tokens=10)
```

### NumPy Version Conflict
**Symptom**: `ImportError: numpy.core.multiarray failed to import`

**Cause**: NumPy 2.x incompatible with ONNX Runtime

**Solution**:
```bash
pip install 'numpy>=1.26.0,<2.0.0' --force-reinstall
```

### Out of Memory
**Symptom**: `RuntimeError: Failed to allocate memory`

**Cause**: Model too large for 18GB RAM

**Solution**:
1. Close other apps
2. Use INT8 quantization (reduces size by 4x)
3. Use smaller model variant

## Testing & Validation

### Unit Tests
```bash
# Test ONNX model loads
python -c "from ai.onnx_runtime.onnx_bot import ONNXBot; bot = ONNXBot('models/mistral-onnx', 'Test', 'Player')"

# Test inference
python -c "from ai.onnx_runtime.onnx_bot import ONNXBot; bot = ONNXBot('models/mistral-onnx', 'GM', 'Player'); print(bot.get_response_to_event('Test event'))"
```

### Quality Validation
Compare Ollama vs ONNX outputs:
```python
prompt = "Player makes a strategic center move."
ollama_response = llm_bot.get_response_to_event(prompt)
onnx_response = onnx_bot.get_response_to_event(prompt)
# Manually compare narrative quality
```

### Performance Benchmark
Use same 15-sample methodology as baseline:
1. Play game with ONNX mode enabled
2. Time 15 move responses
3. Calculate mean, std dev, CI
4. Compare with baseline (5.55s)

## Next Steps

1. ✅ Dependencies installed
2. ✅ Baseline documented (5.55s)
3. ⏳ Convert Mistral to ONNX
4. ⏳ Test ONNXBot inference
5. ⏳ Integrate into UI
6. ⏳ Benchmark performance
7. ⏳ Document results

---

**Author**: GitHub Copilot CLI  
**Date**: 2026-03-31  
**Hardware**: Apple M3 Pro (18GB RAM)  
**Target**: < 2.22s inference (60% reduction from 5.55s baseline)
