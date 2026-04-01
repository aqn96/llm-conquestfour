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
Game Move → LLMBot → Ollama API → llama.cpp runtime (Ollama) → Response
```

### Key Characteristics
- **Execution**: Ollama runtime (processor depends on runtime state; Apple Silicon typically uses Metal GPU)
- **Model Format**: Ollama native format (not ONNX)
- **Quantization**: Ollama's default (likely 4-bit)
- **Memory**: ~4.4 GB model size on disk

## User Experience Assessment
- **Perceived Delay**: ~5 seconds is noticeable but acceptable for single-player
- **Multiplayer**: Would feel sluggish for real-time multiplayer gameplay
- **UI Responsiveness**: Need to verify if UI freezes during inference

## Post-Architecture Improvement Run (Phi-3-mini)

**Date**: 2026-04-01  
**Hardware**: Apple M3 Pro (18GB RAM)  
**Model**: `phi3:mini` via Ollama  
**Observed runtime**: `ollama ps` showed `PROCESSOR = 100% GPU`

### Response Latency Samples (n=15)

```
3.63, 3.61, 4.09, 3.81, 6.00,
4.80, 4.23, 4.88, 6.10, 3.82,
3.29, 3.09, 3.03, 4.03, 5.32
```

### Statistical Summary

| Metric | Value |
|--------|-------|
| **Mean** | **4.25 seconds** |
| **Median** | 4.03 seconds |
| **Std Dev** | 0.98 seconds |
| **Min** | 3.03 seconds |
| **Max** | 6.10 seconds |
| **Range** | 3.07 seconds |
| **95% CI** | 4.25 ± 0.49s |
| **CI Range** | [3.75s, 4.74s] |

### Improvement vs Baseline

- Baseline mean (Mistral-7B): **5.52–5.55s**
- Post-improvement mean (Phi-3-mini): **4.25s**
- Improvement: **~23% faster** average latency

---

## Updated Optimization Direction

### Target Performance
Based on **baseline mean = 5.52s** and current post-improvement mean **4.25s**:

| Goal Level | Target Latency | Improvement % | Status |
|-----------|---------------|---------------|---------|
| **Aggressive** | < 2.21s | 60% reduction | Stretch goal |
| **Realistic** | < 3.31s | 40% reduction | Still open |
| **Minimum** | < 4.14s | 25% reduction | Nearly reached (current 4.25s) |

### Statistical Validation Required
- **T-test**: p < 0.05 to confirm improvement is not random
- **Effect size**: Cohen's d > 0.8 for "large" improvement
- **Consistency**: Reduced variance in interactive gameplay runs

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
2. ✅ Post-architecture Phi-3-mini benchmark documented
3. ⏳ Collect another 15-sample run to confirm stability of the ~23% gain
4. ⏳ Tune prompt length / response length / context window for additional latency reduction
5. ⏳ Re-evaluate realistic target (<3.31s) after tuning

---
*This document will be updated with post-optimization results for comparison.*
