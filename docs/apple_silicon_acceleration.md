# Apple Silicon Acceleration Guide for LLMs

## Quick Reference

**❌ Wrong Approach**: ONNX Runtime + CoreML Execution Provider  
**✅ Correct Approach**: llama.cpp + Metal GPU Backend  

---

## Understanding Apple's ML Stack

```
┌─────────────────────────────────────────┐
│          Application Layer              │
│  (Your Python Code, Ollama, etc.)      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Inference Framework             │
│  ┌─────────────┐    ┌────────────────┐ │
│  │   CoreML    │    │  llama.cpp     │ │
│  │  (Vision)   │    │  (LLMs) ✓     │ │
│  └─────────────┘    └────────────────┘ │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Hardware Acceleration           │
│  ┌─────────────┐    ┌────────────────┐ │
│  │  Neural     │    │   GPU (Metal)  │ │
│  │  Engine     │    │   ✓ For LLMs   │ │
│  │  (ANE)      │    │                │ │
│  └─────────────┘    └────────────────┘ │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Apple Silicon (M3 Pro)          │
│  - 11 CPU cores                         │
│  - 14 GPU cores                         │
│  - 16 Neural Engine cores               │
│  - 150 GB/s memory bandwidth            │
└─────────────────────────────────────────┘
```

### Which Hardware for What Task?

| Task | Best Hardware | Framework | Example |
|------|--------------|-----------|---------|
| **Image Classification** | Neural Engine | CoreML | ResNet, MobileNet |
| **Object Detection** | Neural Engine | CoreML | YOLO, SSD |
| **Audio Processing** | Neural Engine | CoreML | Speech recognition |
| **Small LSTM** | Neural Engine | CoreML | Sentiment analysis |
| **Large Language Models** | **GPU (Metal)** | **llama.cpp** | **Mistral, Llama** |
| **Video Processing** | GPU | Metal | Rendering, effects |
| **Scientific Computing** | GPU | Metal | Matrix ops |

---

## Why LLMs Need GPU (Not Neural Engine)

### Neural Engine Limitations

```python
# What Neural Engine CAN'T handle (but LLMs need):

1. Large Vocabularies
   - LLM vocab: 32,000 tokens
   - ANE limit: 16,384 dimensions ❌

2. Dynamic Shapes
   - LLM: Generate 1-4096 tokens (variable)
   - ANE: Fixed shapes only ❌

3. KV-Cache
   - LLM: Cache previous tokens for efficiency
   - ANE: No dynamic memory ❌

4. Complex Attention
   - LLM: Multi-head attention with softmax
   - ANE: Limited operator set ❌
```

### GPU Metal Advantages

```python
# What GPU Metal CAN handle (perfect for LLMs):

1. Large Matrix Multiplications ✅
   - Transformer = mostly matrix ops
   - Metal: Highly optimized GEMM kernels

2. Dynamic Memory ✅
   - Allocate KV-cache on the fly
   - Grow/shrink based on sequence length

3. Custom Kernels ✅
   - Flash Attention
   - Fused operations
   - Quantized GEMM (INT4/INT8)

4. Full GPU Utilization ✅
   - All 14 GPU cores active
   - ~2.0 TFLOPS compute power
```

---

## llama.cpp Architecture

### What Makes llama.cpp Special

```
1. Purpose-Built for Transformers
   - Not adapted from vision models
   - Designed for autoregressive generation
   - Optimized for memory bandwidth

2. Multi-Backend Support
   ┌──────────────┬─────────────────┬──────────────┐
   │   Backend    │    Hardware     │   Platform   │
   ├──────────────┼─────────────────┼──────────────┤
   │ Metal        │ Apple GPU       │ macOS ✓      │
   │ CUDA         │ NVIDIA GPU      │ Linux/Windows│
   │ ROCm         │ AMD GPU         │ Linux        │
   │ Vulkan       │ Any GPU         │ All          │
   │ OpenCL       │ Any GPU         │ All          │
   │ CPU          │ Fallback        │ All          │
   └──────────────┴─────────────────┴──────────────┘

3. Quantization Support
   - INT4 (GGUF Q4 formats)
   - INT8 (Q8 formats)
   - Mixed precision (some layers FP16)
   - Per-channel quantization
```

### Performance Optimizations

```cpp
// llama.cpp's Metal backend includes:

1. Optimized Matrix Multiplication
   - Uses Metal Performance Shaders (MPS)
   - Tiled operations for cache efficiency
   - Asynchronous execution

2. Flash Attention
   - Memory-efficient attention mechanism
   - Reduces memory bandwidth by ~4x
   - Critical for long context windows

3. KV-Cache Management
   - Efficient reuse of computed attention
   - Avoids recomputing past tokens
   - Enables fast autoregressive generation

4. Batching
   - Process multiple tokens per GPU call
   - Amortize kernel launch overhead
   - Better GPU utilization
```

---

## Ollama + llama.cpp Integration

### How Ollama Uses llama.cpp

```
User Request → Ollama Server → llama.cpp (Metal) → GPU → Response
```

**Ollama's Role**:
- Model management (download, storage)
- API endpoint (REST API)
- Context management
- Multi-model handling

**llama.cpp's Role**:
- Actual inference
- Metal GPU acceleration
- Memory management
- Token generation

### Verifying Metal is Active

```bash
# Method 1: Ollama logs
ollama serve
# Look for: "metal" or "gpu" in initialization logs

# Method 2: Activity Monitor
# GPU History should spike during inference

# Method 3: powermetrics (requires sudo)
sudo powermetrics --samplers gpu_power -i 1000
# Look for non-zero "GPU active residency"
```

---

## Optimization Strategy for Your Project

### Current State
```
Game → LLMBot → Ollama API → llama.cpp (Metal) → M3 GPU
Baseline: 5.55s mean latency
```

### Optimization Opportunities

#### 1. **Ensure Metal is Active** (Most Important!)
```bash
# Check if Metal is enabled in Ollama
ollama ps  # Should show "GPU" or "Metal"

# If not, reinstall Ollama
brew reinstall ollama
```

#### 2. **Model Selection**
```bash
# Current: mistral:latest (likely 4-bit quantized)
# Try:
ollama pull mistral:7b-instruct-q4_0     # Explicit 4-bit
ollama pull mistral:7b-instruct-q8_0     # 8-bit (better quality, slower)
ollama pull phi3:mini                     # Smaller, faster (3.8B params)
```

#### 3. **Context Length Optimization**
```python
# In your LLMBot, add:
self._model = OllamaLLM(
    model=model_name,
    num_ctx=2048,  # Reduce from default 4096
    num_gpu=99,    # Use all GPU layers
)
```

#### 4. **Prompt Engineering**
```python
# Shorter prompts = faster inference
# Current: ~200 tokens of setup
# Optimized: ~100 tokens

# Before
"Your name is {name}. Your opponent is {opponent}. 
You are playing {game}. Setting: {long_description}..."

# After
"{name} narrates {game} in {setting} style. Brief responses."
```

#### 5. **Batch Inference** (Future)
```python
# If generating multiple narratives:
# Batch them into single request
# GPU processes batches efficiently
```

---

## Expected Performance Gains

### Realistic Targets

| Optimization | Expected Speedup | Cumulative |
|-------------|------------------|------------|
| Baseline (Ollama default) | 1.0x | 5.55s |
| **Verify Metal active** | 1.2-1.5x | 3.7-4.6s ✅ |
| Reduce context length | 1.1x | 3.4-4.2s |
| Shorter prompts | 1.1x | 3.1-3.8s |
| Smaller model (Phi-3) | 2.0x | 1.6-1.9s ✨ |

**Achievable Goal**: **3.0-4.0s** (27-46% improvement from 5.55s)  
**Aggressive Goal**: **<2.5s** with smaller model (55% improvement)

### Why Not 60%+ Improvement?

```
Bottlenecks (even with Metal GPU):

1. Memory Bandwidth (40% of time)
   - Moving 7B parameters from RAM to GPU
   - Limited by 150 GB/s bandwidth
   - Can't be optimized much

2. Sequential Generation (30% of time)
   - Token-by-token generation is sequential
   - Can't parallelize next token prediction
   - Inherent to autoregressive models

3. Tokenization (10% of time)
   - CPU-bound string processing
   - Not parallelizable

4. Actual Compute (20% of time)
   - THIS is what Metal GPU accelerates ✓
   - Already quite fast on M3 Pro
```

---

## Monitoring & Validation

### Tools for Checking GPU Usage

```bash
# 1. Activity Monitor
# Window → GPU History
# Should show spikes during inference

# 2. asitop (install: pip install asitop)
sudo asitop
# Shows real-time GPU/ANE/CPU usage

# 3. Check Ollama's GPU usage
ollama ps
# Should list GPU memory usage

# 4. Simple Python check
python -c "
import ollama
import time
start = time.time()
response = ollama.generate(model='mistral', prompt='Test')
print(f'Time: {time.time()-start:.2f}s')
"
```

---

## Summary: The Right Stack for LLMs on Apple Silicon

```
✅ CORRECT STACK:
┌─────────────────────────┐
│   Your Application      │
│   (Python, PyQt6)       │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   Ollama (optional)     │
│   or direct llama.cpp   │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   llama.cpp             │
│   (C++ inference core)  │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   Metal API             │
│   (GPU compute)         │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   M3 Pro GPU            │
│   (14 cores, ~2 TFLOPS) │
└─────────────────────────┘
```

```
❌ WRONG STACK (What we tried):
┌─────────────────────────┐
│   Your Application      │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   ONNX Runtime          │
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   CoreML EP             │  ← Only 3.8% of ops supported!
└─────────────────────────┘
           ↓
┌─────────────────────────┐
│   Neural Engine         │  ← Wrong hardware!
└─────────────────────────┘
```

---

**Key Takeaway**: For LLMs on Apple Silicon, use **llama.cpp + Metal GPU**, not ONNX + CoreML. The Neural Engine is for vision models, not transformers.
