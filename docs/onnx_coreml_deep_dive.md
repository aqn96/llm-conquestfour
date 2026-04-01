# ONNX/CoreML Deep Dive for ConquestFour

**Date**: 2026-03-31  
**Hardware focus**: Apple Silicon M3 Pro  
**Audience**: Project maintainers and collaborators

---

## Executive Summary

For this project, the stable and performant runtime path is:

- **GGUF model + Ollama + llama.cpp + Metal GPU**

The ONNX/CoreML path remains **experimental/research-only** for LLM inference because transformer execution patterns do not map cleanly to CoreML EP in this setup.

---

## Team Learnings Recap (Plain English)

This captures the practical understanding from our investigation:

1. ONNX is an interchange format:
   - ONNX means **Open Neural Network Exchange**.
   - It helps export models from one framework and run them in another runtime.
   - Performance still depends on the target execution provider and hardware backend.

2. The Apple hardware split matters:
   - **GPU + Metal**: best fit for transformer LLM matrix-heavy inference.
   - **Neural Engine (NPU)**: best for small, fixed-shape, low-power ML workloads.

3. Our stable runtime path:
   - We do **not** use CoreML/NPU in the stable path.
   - We use **Ollama + llama.cpp + Metal GPU**.

4. Important correction:
   - This is **not** "CPU bare-metal inference."
   - Heavy compute is offloaded to the **GPU** through Metal; CPU orchestrates control flow.

5. eBPF is unrelated:
   - llama.cpp does not use eBPF.
   - eBPF is a Linux kernel observability/networking technology, not a macOS GPU inference path.

---

## What "Ops" Means

"Ops" means model graph operations (nodes), such as:

- `MatMul`
- `Add`
- `LayerNorm`
- `Softmax`
- `Split`
- `Reshape`

When exporting a model to ONNX, the model becomes a graph of many ops. Execution providers (EPs) only accelerate the ops they support. Unsupported ops fall back to CPU.

---

## Why ONNX + CoreML Struggles for LLMs Here

### 1. Low effective operator coverage

Project POC notes report approximately:

- `99 / 2616` nodes supported by CoreML EP for TinyLlama ONNX graph

That means most of the graph still executes on CPU, with partition boundaries and data movement overhead.

### 2. Dynamic-shape and autoregressive decode pressure

LLMs generate token-by-token and rely on dynamic sequence behavior during decoding. This is more complex than fixed-shape vision inference workloads.

### 3. KV-cache execution pattern

Efficient LLM decoding depends on maintaining and updating KV-cache over many decode steps. This stateful pattern is handled naturally by llama.cpp runtime design.

### 4. CoreML constraints surfaced in project docs

Project notes also observed warnings around CoreML tensor/dimension constraints (for example, input-dimension limits), which further reduce compatibility for large transformer paths.

---

## Why Ollama + llama.cpp + Metal Works Better

### 1. Purpose-built runtime for transformer LLMs

llama.cpp is designed around transformer inference and autoregressive decoding, including cache-aware generation loops.

### 2. Metal GPU path on Apple Silicon

On Apple Silicon, llama.cpp uses Metal backend for GPU acceleration, avoiding many of the ONNX/CoreML partitioning limitations observed in this project.

### 3. Practical stack alignment

Current app code already uses Ollama models in the format/runtime ecosystem intended for llama.cpp, so it avoids conversion complexity and runtime mismatches.

---

## Hardware Note: Apple M3 Optimization

ConquestFour is now documented and configured with:

- **Stable default backend**: Ollama + llama.cpp + Metal
- **Experimental backend option**: ONNX/CoreML NPU mode, gated and fallback-protected

If experimental mode is selected but unavailable/failing, the app automatically falls back to stable Ollama/Metal.

---

## CNN vs Transformer (Why This Matters)

CoreML has historically strong fit for fixed-shape vision pipelines (CNN-heavy workloads).  
LLMs are transformer-heavy and involve significantly more complex attention-centric decode behavior, which is why this project's CoreML EP path was not successful as a primary runtime.

---

## Implementation Guidance

1. Use `Auto (Recommended)` backend in UI for production usage.
2. Use experimental NPU mode only for testing/research.
3. Prioritize model-size/runtime tuning on stable path (for example `phi3:mini`) for latency improvements.
