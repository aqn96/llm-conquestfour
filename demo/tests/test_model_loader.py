#!/usr/bin/env python3
"""
Unified Model Loader Tests

This script tests the unified model loader which can handle both:
1. Local LLM models like Mistral 7B
2. NPU models and fallbacks

It can be run with different arguments to test specific model types.
"""
import os
import sys
import time
import logging
import argparse
from game.connect_four import ConnectFourGame, Player
from ai.model_loader import UnifiedModelLoader, LocalLLMNarrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_arguments():
    """Parse command line arguments for test configuration"""
    parser = argparse.ArgumentParser(description='Test the unified model loader')
    parser.add_argument('--model-type', type=str, default='auto',
                      choices=['auto', 'local_llm', 'npu'],
                      help='Type of model to test')
    parser.add_argument('--model-path', type=str,
                      help='Path to local LLM model')
    return parser.parse_args()

def check_environment():
    """Check for necessary libraries and hardware acceleration"""
    # Check for PyTorch and transformers
    try:
        import torch
        logging.info("PyTorch library is available")
        logging.info(f"PyTorch version: {torch.__version__}")
        logging.info(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logging.info(f"CUDA version: {torch.version.cuda}")
            device_count = torch.cuda.device_count()
            logging.info(f"Available GPU(s): {device_count}")
            for i in range(device_count):
                logging.info(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    except ImportError:
        logging.warning("PyTorch not found")
        logging.warning("Install with: pip install torch")
    
    # Check for transformers
    try:
        from transformers import __version__ as transformers_version
        logging.info(f"Transformers library is available (version: {transformers_version})")
    except ImportError:
        logging.warning("Transformers library not found")
        logging.warning("Install with: pip install transformers")

def test_model_loading(model_type='auto', model_path=None):
    """Test loading a model using the unified loader"""
    logging.info(f"Testing {model_type} model loading...")
    
    # Create loader
    loader = UnifiedModelLoader(model_type=model_type, model_path=model_path)
    
    # Start loading the model (this happens in a background thread)
    loader.load_model()
    
    # Wait for model to load (in real app, we'd use signals)
    timeout = 60  # Maximum time to wait in seconds
    start_time = time.time()
    
    while not loader.is_loaded and time.time() - start_time < timeout:
        time.sleep(1)
        logging.info("Waiting for model to load...")
    
    if not loader.is_loaded:
        logging.warning(f"Model failed to load within {timeout} seconds")
        return None
    
    logging.info(f"Model loaded successfully: {type(loader.model).__name__}")
    return loader

def test_narrative_generation(loader):
    """Test generating narratives with the loaded model"""
    if not loader or not loader.is_loaded:
        logging.warning("No model loaded, skipping narrative generation test")
        return
    
    logging.info("Testing narrative generation...")
    
    # Create a game and make some moves for an interesting board state
    game = ConnectFourGame()
    
    # Make alternating moves
    test_moves = [3, 4, 2, 5, 1, 3]
    for col in test_moves:
        game.make_move(col)
    
    # Print the board
    logging.info("Current board state:")
    print(game)
    
    # Test different themes
    themes = ["fantasy", "sci-fi", "western"]
    for theme in themes:
        logging.info(f"Generating narrative with {theme.upper()} theme...")
        
        # Set the theme
        loader.set_theme(theme)
        
        # Generate a narrative based on game state
        start_time = time.time()
        narrative = loader.generate_narrative(game)
        elapsed = time.time() - start_time
        
        # Print results
        logging.info(f"Generation took {elapsed:.2f} seconds")
        print(f"\nTheme: {theme}")
        print(f"Narrative: {narrative}\n")
        print("-" * 60)
    
    # Also test string-based prompts
    logging.info("Testing string-based prompts...")
    
    prompts = [
        "Generate a narrative for a threatening move in the opening phase",
        "Describe a strategic defensive move in a tight situation",
        "Narrate a potentially winning move as the game nears its end"
    ]
    
    for prompt in prompts:
        logging.info(f"Using prompt: '{prompt}'")
        
        # Generate narrative from prompt
        narrative = loader.generate_narrative(prompt)
        
        print(f"\nPrompt: {prompt}")
        print(f"Narrative: {narrative}\n")
        print("-" * 60)

def main():
    """Main test function"""
    logging.info("Starting unified model loader test...")
    
    # Parse arguments
    args = parse_arguments()
    
    # Check environment
    check_environment()
    
    # Determine model path if not provided
    model_path = args.model_path
    if not model_path and args.model_type == 'local_llm':
        model_path = os.environ.get(
            "LOCAL_LLM_PATH", 
            os.path.expanduser("~/models/mistral-7b")
        )
        logging.info(f"Using model path from environment: {model_path}")
    
    # Test model loading
    loader = test_model_loading(args.model_type, model_path)
    
    # Test narrative generation
    test_narrative_generation(loader)
    
    logging.info("Unified model loader test completed")

if __name__ == "__main__":
    main() 