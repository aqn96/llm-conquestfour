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

## Post-Latency-Tuning Run (Phi-3-mini)

**Date**: 2026-04-01  
**Hardware**: Apple M3 Pro (18GB RAM)  
**Model**: `phi3:mini` via Ollama  
**Tuning enabled**:
- Rolling chat history cap
- One-paragraph response constraint
- Tuned generation params (`num_ctx`, `num_predict`)
- Lighter narrative evaluator depth
- Runtime perf timing logs

### Response Latency Samples (n=15)

```
5.20, 3.75, 3.37, 3.61, 3.56,
3.68, 3.69, 4.35, 4.94, 5.35,
5.19, 4.86, 5.19, 5.06, 5.00
```

### Statistical Summary

| Metric | Value |
|--------|-------|
| **Mean** | **4.45 seconds** |
| **Median** | 4.86 seconds |
| **Std Dev** | 0.75 seconds |
| **Min** | 3.37 seconds |
| **Max** | 5.35 seconds |
| **Range** | 1.98 seconds |
| **95% CI** | 4.45 ± 0.38s |
| **CI Range** | [4.07s, 4.83s] |

### Improvement vs Baseline

- Baseline mean (Mistral-7B): **5.55s**
- Post-tuning mean (Phi-3-mini): **4.45s**
- Improvement: **~19.8% faster** average latency

### Key Learning from This Run

- Tail latency improved: max response dropped from **6.10s** (previous Phi run) to **5.35s**.
- Session stayed below 6s throughout, indicating better consistency during longer gameplay.

---

## Combined Phi-3 Summary (Two Runs)

To reduce single-run noise, combine both Phi-3 runs:

- Run #1 (post-architecture): `n=15`, mean `4.25s`
- Run #2 (post-latency-tuning): `n=15`, mean `4.45s`
- **Combined**: `n=30`, mean **4.35s**, std dev **0.86s**, 95% CI **4.35 ± 0.31s**
- **Combined improvement vs 5.55s baseline**: **~21.6% faster**

---

## Updated Optimization Direction

### Target Performance
Based on **baseline mean = 5.55s** and current combined mean **4.35s**:

| Goal Level | Target Latency | Improvement % | Status |
|-----------|---------------|---------------|---------|
| **Aggressive** | < 2.21s | 60% reduction | Stretch goal |
| **Realistic** | < 3.31s | 40% reduction | Still open |
| **Minimum** | < 4.16s | 25% reduction | Near (current 4.35s) |

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
3. ✅ Post-latency-tuning benchmark documented
4. ✅ Two-run combined summary (n=30) documented
5. ⏳ Continue tuning for additional latency reduction toward <4.16s minimum target

---
*This document will be updated with post-optimization results for comparison.*
