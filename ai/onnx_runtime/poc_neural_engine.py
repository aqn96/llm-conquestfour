#!/usr/bin/env python3
"""
Quick Proof-of-Concept: ONNX + Neural Engine Acceleration

Tests Apple Neural Engine acceleration with TinyLlama-1B (1.1GB) to validate
the approach before converting the larger Mistral-7B model.

Usage:
    python poc_neural_engine.py
"""

import sys
import time
import os

print("\n" + "="*70)
print("PROOF OF CONCEPT: Apple Neural Engine Acceleration")
print("="*70 + "\n")

# Check dependencies
print("🔍 Checking dependencies...")
try:
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import onnxruntime as ort
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"✅ Transformers: {transformers.__version__}")
    print(f"✅ ONNX Runtime: {ort.__version__}")
    print(f"✅ Available providers: {ort.get_available_providers()}")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)

print()

# Check CoreML provider
if "CoreMLExecutionProvider" not in ort.get_available_providers():
    print("⚠️  CoreML Execution Provider not available!")
    print("   Neural Engine acceleration will not work.")
    response = input("Continue anyway? (y/N): ")
    if response.lower() != 'y':
        sys.exit(0)

print("="*70)
print("PHASE 1: Baseline - PyTorch CPU Inference")
print("="*70 + "\n")

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print(f"📦 Loading model: {model_name}")
print("   (This will download ~1.1GB if not cached...)\n")

try:
    # Load tokenizer
    print("🔧 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Load PyTorch model
    print("🔧 Loading PyTorch model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )
    model.eval()
    
    print("✅ Model loaded successfully\n")
    
    # Test prompts
    test_prompts = [
        "Player makes a strategic move in Connect Four.",
        "The game is getting intense!",
        "An unexpected play changes everything."
    ]
    
    print("🧪 Running PyTorch baseline tests...\n")
    
    pytorch_times = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"Test {i}/3: {prompt[:50]}...")
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Generate (time it)
        start = time.perf_counter()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=30,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        elapsed = time.perf_counter() - start
        
        # Decode
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        pytorch_times.append(elapsed)
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Output: {result[:80]}...\n")
    
    pytorch_mean = sum(pytorch_times) / len(pytorch_times)
    print(f"📊 PyTorch CPU Mean: {pytorch_mean:.3f}s\n")
    
except Exception as e:
    print(f"❌ PyTorch test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*70)
print("PHASE 2: Convert to ONNX")
print("="*70 + "\n")

onnx_path = "./models/tinyllama-onnx-poc"
os.makedirs(onnx_path, exist_ok=True)

try:
    print("🔄 Converting to ONNX format...")
    print("   (This may take 2-3 minutes...)\n")
    
    from optimum.onnxruntime import ORTModelForCausalLM
    
    # Export to ONNX
    onnx_model = ORTModelForCausalLM.from_pretrained(
        model_name,
        export=True,
        provider="CPUExecutionProvider"
    )
    
    # Save
    onnx_model.save_pretrained(onnx_path)
    tokenizer.save_pretrained(onnx_path)
    
    print("✅ ONNX conversion complete\n")
    
    # Show file sizes
    print("📋 Generated files:")
    from pathlib import Path
    for file in sorted(Path(onnx_path).glob("*")):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"   {file.name:40s} ({size_mb:7.2f} MB)")
    
except Exception as e:
    print(f"❌ ONNX conversion failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("PHASE 3: ONNX with CoreML (Neural Engine)")
print("="*70 + "\n")

try:
    print("🚀 Loading ONNX model with CoreML Execution Provider...")
    
    # Create session with CoreML
    from optimum.onnxruntime import ORTModelForCausalLM
    
    onnx_model_ane = ORTModelForCausalLM.from_pretrained(
        onnx_path,
        provider="CoreMLExecutionProvider"
    )
    
    tokenizer_onnx = AutoTokenizer.from_pretrained(onnx_path)
    
    # Check actual provider
    actual_provider = onnx_model_ane.model.get_providers()[0]
    if actual_provider == "CoreMLExecutionProvider":
        print("✅ Neural Engine is ACTIVE!\n")
    else:
        print(f"⚠️  Fell back to: {actual_provider}\n")
    
    print("🧪 Running ONNX + Neural Engine tests...\n")
    
    onnx_times = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"Test {i}/3: {prompt[:50]}...")
        
        # Tokenize
        inputs = tokenizer_onnx(prompt, return_tensors="pt")
        
        # Generate (time it)
        start = time.perf_counter()
        outputs = onnx_model_ane.generate(
            **inputs,
            max_new_tokens=30,
            do_sample=False,
            pad_token_id=tokenizer_onnx.eos_token_id
        )
        elapsed = time.perf_counter() - start
        
        # Decode
        result = tokenizer_onnx.decode(outputs[0], skip_special_tokens=True)
        
        onnx_times.append(elapsed)
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Output: {result[:80]}...\n")
    
    onnx_mean = sum(onnx_times) / len(onnx_times)
    print(f"📊 ONNX + ANE Mean: {onnx_mean:.3f}s\n")
    
except Exception as e:
    print(f"❌ ONNX + ANE test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*70)
print("RESULTS COMPARISON")
print("="*70 + "\n")

print(f"PyTorch CPU:    {pytorch_mean:.3f}s")
print(f"ONNX + ANE:     {onnx_mean:.3f}s")
print()

if onnx_mean < pytorch_mean:
    speedup = ((pytorch_mean - onnx_mean) / pytorch_mean) * 100
    print(f"🎉 Speedup: {speedup:.1f}% faster with Neural Engine!")
    print(f"   Absolute: {pytorch_mean - onnx_mean:.3f}s reduction")
else:
    slowdown = ((onnx_mean - pytorch_mean) / pytorch_mean) * 100
    print(f"⚠️  Slower by {slowdown:.1f}% (unexpected)")

print()
print("="*70)
print("EXTRAPOLATION TO MISTRAL-7B")
print("="*70 + "\n")

print(f"If we see similar {speedup:.1f}% speedup on Mistral-7B:")
print(f"   Baseline (Ollama):     5.55s")
print(f"   Projected (ONNX+ANE):  {5.55 * (1 - speedup/100):.2f}s")
print(f"   Would this meet goal? {'✅ YES' if 5.55 * (1 - speedup/100) < 2.22 else '⚠️  Close' if 5.55 * (1 - speedup/100) < 3.33 else '❌ No'}")
print()

print("📝 Note: This is just a rough estimate. Actual Mistral performance")
print("   may differ due to model size, architecture, and memory bandwidth.")
print()

print("="*70)
print("POC COMPLETE")
print("="*70)
print()

if speedup > 30:
    print("✅ Neural Engine acceleration is working well!")
    print("   Recommend proceeding with Mistral-7B conversion.")
elif speedup > 10:
    print("⚠️  Moderate speedup observed.")
    print("   May still be worth trying with Mistral-7B.")
else:
    print("❌ Limited or no speedup.")
    print("   May need to investigate CoreML provider setup.")

print()
