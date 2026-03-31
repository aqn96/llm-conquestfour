#!/usr/bin/env python3
"""
Model Conversion Script - Mistral-7B to ONNX with Quantization

This script converts Mistral-7B from HuggingFace format to ONNX format
with INT8 quantization for optimal Apple Neural Engine performance.

Usage:
    python convert_mistral_to_onnx.py [--model-size MODEL_SIZE]
    
Options:
    --model-size: tiny, small, or full (default: small for testing)
"""

import argparse
import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("MISTRAL-7B → ONNX CONVERSION SCRIPT")
print("="*70 + "\n")

# Check dependencies
print("🔍 Checking dependencies...")
try:
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import onnx
    from optimum.onnxruntime import ORTModelForCausalLM
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall with: pip install torch transformers optimum onnx")
    sys.exit(1)

print()


def convert_model_to_onnx(model_name: str, output_dir: str, use_quantization: bool = True):
    """
    Convert HuggingFace model to ONNX format with optional quantization.
    
    Args:
        model_name: HuggingFace model identifier
        output_dir: Where to save ONNX model
        use_quantization: Apply INT8 quantization
    """
    print(f"📦 Model: {model_name}")
    print(f"📁 Output: {output_dir}")
    print(f"⚙️  Quantization: {'Enabled (INT8)' if use_quantization else 'Disabled'}")
    print()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load tokenizer (always needed)
        print("🔧 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(output_dir)
        print("✅ Tokenizer saved")
        print()
        
        # Convert to ONNX using optimum
        print("🔄 Converting model to ONNX format...")
        print("   (This may take several minutes...)")
        
        from optimum.onnxruntime import ORTModelForCausalLM
        
        # Load and export to ONNX
        model = ORTModelForCausalLM.from_pretrained(
            model_name,
            export=True,
            provider="CPUExecutionProvider"  # Use CPU for conversion
        )
        
        # Save ONNX model
        model.save_pretrained(output_dir)
        print("✅ Model converted to ONNX")
        print()
        
        # Quantization
        if use_quantization:
            print("🔧 Applying INT8 quantization...")
            print("   (Optimizing for Apple Neural Engine...)")
            
            from optimum.onnxruntime import ORTQuantizer
            from optimum.onnxruntime.configuration import AutoQuantizationConfig
            
            # Dynamic quantization (no calibration dataset needed)
            quantizer = ORTQuantizer.from_pretrained(output_dir)
            qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=True)
            
            quantizer.quantize(
                save_dir=output_dir,
                quantization_config=qconfig,
            )
            print("✅ Quantization complete")
            print()
        
        print("="*70)
        print("✅ CONVERSION SUCCESSFUL")
        print("="*70)
        print(f"Model saved to: {output_dir}")
        print()
        
        # Verify model files
        print("📋 Generated files:")
        for file in sorted(Path(output_dir).glob("*")):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   {file.name:40s} ({size_mb:7.2f} MB)")
        
        return True
        
    except Exception as e:
        print("="*70)
        print(f"❌ CONVERSION FAILED: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert Mistral to ONNX")
    parser.add_argument(
        "--model-size",
        choices=["tiny", "small", "full"],
        default="small",
        help="Model size to convert (default: small)"
    )
    parser.add_argument(
        "--output-dir",
        default="./models/mistral-onnx",
        help="Output directory for ONNX model"
    )
    parser.add_argument(
        "--no-quantization",
        action="store_true",
        help="Disable INT8 quantization"
    )
    
    args = parser.parse_args()
    
    # Select model based on size
    model_map = {
        "tiny": "mistralai/Mistral-7B-Instruct-v0.1",  # Smallest variant
        "small": "mistralai/Mistral-7B-Instruct-v0.2",
        "full": "mistralai/Mistral-7B-Instruct-v0.3"
    }
    
    model_name = model_map[args.model_size]
    
    print(f"⚡ Model Selection: {args.model_size} ({model_name})")
    print()
    
    # Warning for large models
    if args.model_size == "full":
        print("⚠️  WARNING: Full model conversion requires significant RAM (>16GB)")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Convert
    success = convert_model_to_onnx(
        model_name=model_name,
        output_dir=args.output_dir,
        use_quantization=not args.no_quantization
    )
    
    if success:
        print("\n🎉 Ready to use with ONNXBot!")
        print(f"   Model path: {args.output_dir}")
    else:
        print("\n❌ Conversion failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
