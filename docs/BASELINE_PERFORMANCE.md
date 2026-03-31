# Performance Baseline - Ollama Implementation

**Date**: 2026-03-31  
**Hardware**: Apple M3 Pro (18GB RAM)  
**Model**: Mistral-7B via Ollama  
**Test Method**: Manual gameplay - time from move to narrative response  

## Baseline Performance Metrics

### Response Latency (seconds per narrative generation)

**Session 1 (Initial Testing):**
```
Sample 1:   6.77s
Sample 2:   5.64s
Sample 3:   4.45s
Sample 4:   4.21s
Sample 5:   5.25s
Sample 6:   4.71s
Sample 7:   6.42s
```

**Session 2 (Validation Testing):**
```
Sample 8:   6.43s
Sample 9:   5.70s
Sample 10:  5.85s
Sample 11:  5.83s
Sample 12:  5.52s
Sample 13:  5.91s
Sample 14:  5.78s
Sample 15:  4.79s
```

### Final Statistical Summary (n=15) ✅

| Metric | Value |
|--------|-------|
| **Mean** | **5.52 seconds** |
| **Median** | 5.70 seconds |
| **Std Dev** | 0.67 seconds |
| **Min** | 4.21 seconds |
| **Max** | 6.77 seconds |
| **Range** | 2.56 seconds |
| **CV** | 12.2% |
| **95% CI** | 5.52 ± 0.34s |
| **CI Range** | [5.18s, 5.86s] |

### Sample Size Validation
✅ **n = 15 samples collected**
- Provides 95% confidence interval with ±0.34s margin
- Coefficient of variation: 12.2% (acceptable, <15%)
- Sample size meets engineering benchmark standards

## Implementation Details

### Current Architecture
```
Game Move → LLMBot → Ollama API → Mistral-7B → CPU Inference → Response
```

### Key Characteristics
- **Execution**: CPU-only (no GPU/NPU acceleration)
- **Model Format**: Ollama native format (not ONNX)
- **Quantization**: Ollama's default (likely 4-bit)
- **Memory**: ~4.4 GB model size on disk

## User Experience Assessment
- **Perceived Delay**: ~5 seconds is noticeable but acceptable for single-player
- **Multiplayer**: Would feel sluggish for real-time multiplayer gameplay
- **UI Responsiveness**: Need to verify if UI freezes during inference

## Optimization Goals

### Target Performance (ONNX + Neural Engine)
Based on **baseline mean = 5.52s**, our targets are:

| Goal Level | Target Latency | Improvement % | Status |
|-----------|---------------|---------------|---------|
| **Aggressive** | < 2.21s | 60% reduction | Resume claim target ✨ |
| **Realistic** | < 3.31s | 40% reduction | Industry standard |
| **Minimum** | < 4.14s | 25% reduction | Acceptable gain |

### Statistical Validation Required
- **T-test**: p < 0.05 to confirm improvement is not random
- **Effect size**: Cohen's d > 0.8 for "large" improvement
- **Consistency**: ONNX std dev ≤ baseline std dev (0.67s)

### Why These Numbers Matter
According to UX research:
- **< 1s**: Feels instant, no interruption
- **1-3s**: Slight pause, still feels responsive
- **3-5s**: Noticeable delay, user expects progress indicator
- **> 5s**: Feels slow, user may lose engagement

**Current State**: We're in the "noticeable delay" zone at ~5s  
**Optimization Goal**: Move to "slight pause" zone at ~2-3s

## Next Steps
1. ✅ Baseline documented
2. ⏳ Implement ONNX Runtime with CoreML Execution Provider
3. ⏳ Integrate Apple Neural Engine acceleration
4. ⏳ Re-test with identical gameplay scenarios
5. ⏳ Compare results and validate improvements

---
*This document will be updated with post-optimization results for comparison.*
