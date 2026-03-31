#!/usr/bin/env python3
"""
Optimize Ollama for Metal GPU Acceleration

This script tests and optimizes the existing Ollama setup to ensure
Metal GPU acceleration is being used effectively.

Usage:
    python optimize_ollama_metal.py
"""

import sys
import time
import os

print("\n" + "="*70)
print("OLLAMA METAL GPU OPTIMIZATION")
print("="*70 + "\n")

# Test 1: Check if Ollama is using GPU
print("🔍 TEST 1: Checking Ollama GPU Status")
print("="*70 + "\n")

try:
    import ollama
    print("✅ Ollama Python client installed\n")
    
    # Check if server is running
    try:
        models = ollama.list()
        print("✅ Ollama server is running\n")
        print(f"Available models: {len(models.get('models', []))}")
        for model in models.get('models', []):
            print(f"   - {model['name']}")
        print()
    except Exception as e:
        print(f"❌ Ollama server not running: {e}")
        print("\nStart with: ollama serve")
        sys.exit(1)
        
except ImportError:
    print("❌ Ollama Python client not installed")
    print("\nInstall with: pip install ollama")
    sys.exit(1)

# Test 2: Baseline inference test
print("\n" + "="*70)
print("🧪 TEST 2: Baseline Inference Performance")
print("="*70 + "\n")

test_prompts = [
    "Player makes a strategic move.",
    "The game intensifies!",
    "An unexpected turn of events.",
]

print("Testing current Ollama performance...\n")

baseline_times = []

for i, prompt in enumerate(test_prompts, 1):
    print(f"Test {i}/3: {prompt}")
    
    start = time.perf_counter()
    try:
        response = ollama.generate(
            model='mistral',
            prompt=prompt,
            options={
                'num_predict': 30,  # Generate ~30 tokens
                'temperature': 0.7,
            }
        )
        elapsed = time.perf_counter() - start
        baseline_times.append(elapsed)
        
        output = response['response'][:80]
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Output: {output}...\n")
        
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

if baseline_times:
    mean_time = sum(baseline_times) / len(baseline_times)
    print(f"📊 Current Mean: {mean_time:.3f}s")
    print(f"📊 Baseline Target: 5.55s")
    print(f"📊 Comparison: {'✅ Faster!' if mean_time < 5.55 else '⚠️ Similar or slower'}\n")

# Test 3: Check GPU utilization
print("\n" + "="*70)
print("🔧 TEST 3: Optimizing Ollama Configuration")
print("="*70 + "\n")

print("Recommended optimizations:\n")

print("1. **Verify Metal GPU is active**:")
print("   • Open Activity Monitor")
print("   • Window → GPU History")
print("   • Run a test prompt (next section)")
print("   • GPU usage should spike to 60-90%")
print()

print("2. **Reduce context window** (less memory = faster):")
print("   In your LLMBot code:")
print("   ```python")
print("   self._model = OllamaLLM(")
print("       model='mistral',")
print("       num_ctx=2048,  # Reduce from 4096")
print("       num_gpu=99,    # Use all GPU layers")
print("   )")
print("   ```")
print()

print("3. **Try explicit 4-bit model**:")
print("   ```bash")
print("   ollama pull mistral:7b-instruct-q4_0")
print("   ```")
print()

print("4. **Consider smaller model for speed**:")
print("   ```bash")
print("   ollama pull phi3:mini  # 3.8B params, 2x faster")
print("   ```")
print()

# Test 4: Real-time GPU monitoring
print("\n" + "="*70)
print("🎯 TEST 4: Real-Time GPU Monitoring")
print("="*70 + "\n")

print("I'll generate a longer response. Watch your GPU usage in Activity Monitor!\n")
print("Opening Activity Monitor automatically (if possible)...")

try:
    import subprocess
    # Try to open Activity Monitor
    subprocess.Popen(["open", "-a", "Activity Monitor"])
    print("✅ Activity Monitor opened")
    print("\nIn Activity Monitor:")
    print("   1. Click 'Window' → 'GPU History'")
    print("   2. Watch for spikes during generation\n")
except:
    print("⚠️  Please open Activity Monitor manually\n")

time.sleep(3)

print("Generating longer prompt to stress GPU...\n")

long_prompt = """You are a game narrator for Connect Four. 
The player just made an incredible strategic move, blocking the AI's winning attempt 
while simultaneously setting up their own winning position. 
Describe this dramatic moment in an exciting Western theme."""

print("🔄 Generating (watch Activity Monitor GPU History)...")
start = time.perf_counter()

try:
    response = ollama.generate(
        model='mistral',
        prompt=long_prompt,
        options={
            'num_predict': 100,
            'temperature': 0.8,
        }
    )
    elapsed = time.perf_counter() - start
    
    print(f"\n✅ Generated in {elapsed:.3f}s\n")
    print(f"Response preview:")
    print(f"{response['response'][:200]}...\n")
    
    print(f"Did you see GPU usage spike in Activity Monitor?")
    print(f"   YES → Metal is working! ✅")
    print(f"   NO  → Metal might not be active ⚠️")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

# Summary
print("\n" + "="*70)
print("SUMMARY & NEXT STEPS")
print("="*70 + "\n")

if baseline_times:
    mean = sum(baseline_times) / len(baseline_times)
    
    print(f"Current Performance: {mean:.3f}s")
    print(f"Baseline Target:     5.55s")
    print(f"Goal Target:         2.22s (60% reduction)")
    print()
    
    if mean < 4.0:
        print("✅ Already faster than baseline!")
        print("   • Ollama is likely using Metal GPU effectively")
        print("   • Try smaller model (phi3) for even better performance")
    elif mean < 5.5:
        print("⚠️  Similar to baseline")
        print("   • Verify Metal GPU is active (Activity Monitor)")
        print("   • Try optimizations listed above")
    else:
        print("❌ Slower than baseline")
        print("   • Metal GPU might not be active")
        print("   • Check Ollama installation")
        print("   • Try: brew reinstall ollama")

print("\n📝 Next Steps:")
print("   1. Verify GPU usage in Activity Monitor")
print("   2. Apply num_ctx=2048 in LLMBot code")
print("   3. Test with your actual game (15 samples)")
print("   4. Compare with 5.55s baseline")
print()

print("="*70)
print("OPTIMIZATION CHECK COMPLETE")
print("="*70)
print()
