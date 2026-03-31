# Benchmark Testing Methodology

## Statistical Rigor Guidelines

### Minimum Sample Sizes
- **Quick validation**: n = 5-7 samples (acceptable for directional findings)
- **Engineering benchmark**: n = 15-20 samples (recommended, ±10% margin of error)
- **Scientific publication**: n = 30+ samples (ideal for statistical significance)

### For This Project: **Recommended n = 15**
Why?
- Provides 95% confidence interval
- Reduces impact of outliers
- Captures system variability (thermal throttling, cache effects)
- Practical time investment (~15 minutes testing)

## Current Progress
- ✅ Baseline: 7/15 samples collected
- ⏳ Need: 8 more samples

## Testing Protocol

### What to Control (Keep Consistent)
1. **System State**
   - Close other apps (browser, Slack, etc.)
   - Let system cool down between tests (wait 30s)
   - Check Activity Monitor - CPU should be idle before test
   
2. **Game Settings**
   - Same difficulty level (pick one: Easy/Normal/Hard)
   - Same theme (pick one: Western/Fantasy/etc.)
   - Same AI personality

3. **Move Type**
   - Test similar move scenarios (early game moves, not endgame)
   - Avoid testing winning moves (different prompt patterns)

### What to Measure
- **Primary Metric**: Time from your move placement → AI narrator text appears
- **Method**: Manual stopwatch or screen recording with timestamps

### What to Record (Optional but Useful)
- Move number in game (1st, 2nd, 3rd, etc.)
- Ambient temperature (if Mac feels warm)
- Any lag spikes or unusual delays

## How to Collect Remaining 8 Samples

### Option A: Quick Method (5 minutes)
Play 2 more games, record moves 1-4 from each game
- Game 2: 4 samples
- Game 3: 4 samples
- Total: 8 samples ✓

### Option B: Thorough Method (10 minutes)
Play 4 games, record moves 2-3 from each game
- Captures more game state variety
- Avoids cold-start bias (move 1)
- Avoids endgame bias (final moves)

## Post-ONNX Testing
Use **identical methodology** for fair comparison:
- Same n=15 samples
- Same difficulty/theme/personality
- Same move scenarios
- Same system state protocol

## Statistical Analysis

### After ONNX Implementation
Calculate:
```
Improvement = ((Baseline_Mean - ONNX_Mean) / Baseline_Mean) × 100%
```

Validate with:
- **T-test**: Determine if improvement is statistically significant (p < 0.05)
- **Effect size**: Cohen's d to quantify magnitude of improvement

### Success Criteria
- **Mean improvement**: > 25% reduction (goal: 40-60%)
- **Consistency**: Lower standard deviation in ONNX
- **Reliability**: Max latency < 4.0s (vs current 6.77s)

---

## Quick Reference

**Current Baseline**: 5.35s ± 0.95s (n=7)  
**Samples Needed**: 8 more  
**Time Required**: ~5-10 minutes  
**Method**: Play 2-4 games, time each move response
