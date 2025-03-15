#!/usr/bin/env python3
"""
Test Local LLM Integration for Connect Four

This script tests the local LLM integration for generating themed battle narratives
in the Connect Four game.
"""
import os
import time
import logging
from game.connect_four import ConnectFourGame, Player
from ai.local_llm_loader import LocalLLMNarrator, LocalLLMLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_model_loading():
    """Test loading a local LLM model"""
    logging.info("Testing local LLM model loading...")
    
    # Get model path from environment or use a default test path
    model_path = os.environ.get(
        "LOCAL_LLM_PATH", 
        os.path.expanduser("~/models/mistral-7b")
    )
    
    logging.info(f"Using model path: {model_path}")
    
    # Check if model directory exists
    if not os.path.exists(model_path):
        logging.warning(f"Model path does not exist: {model_path}")
        logging.warning("This is expected if you haven't downloaded a model yet.")
        logging.info("Continuing with test in fallback mode...")
    
    # Create narrator directly
    narrator = LocalLLMNarrator(model_path)
    
    # Try to load the model
    load_success = narrator.load()
    logging.info(f"Model load {'succeeded' if load_success else 'failed'}")
    
    return narrator if load_success else None


def test_narrative_generation(narrator=None):
    """Test generating narratives with a local LLM"""
    logging.info("Testing narrative generation...")
    
    # Create a game and make some moves for an interesting board state
    game = ConnectFourGame()
    
    # Make some moves to create an interesting board
    # We'll make alternating moves by changing the current_player after each move
    test_moves = [3, 4, 2, 5, 1, 3]
    
    for col in test_moves:
        # Make move and let the game handle player switching
        game.make_move(col)
    
    # Print the board
    logging.info("Current board state:")
    print(game)
    
    if narrator:
        # Try generation with different themes
        for theme in ["fantasy", "sci-fi", "western"]:
            logging.info(f"Generating narrative with {theme.upper()} theme...")
            
            # Set the theme
            narrator.set_theme(theme)
            
            # Generate a narrative - use last player which is the opposite of current
            current_player = 1 if game.current_player == Player.TWO else 2
            
            start_time = time.time()
            narrative = narrator.generate_narrative(
                game, 
                current_player,
                move_column=2,
                game_phase="midgame"
            )
            elapsed = time.time() - start_time
            
            # Print results
            logging.info(f"Generation took {elapsed:.2f} seconds")
            print(f"\nTheme: {theme}")
            print(f"Narrative: {narrative}\n")
            print("-" * 60)
    else:
        # Use fallback
        logging.info("Using fallback narrative generation (no model loaded)")
        
        # Create a new narrator without loading a model for fallback testing
        fallback_narrator = LocalLLMNarrator("dummy_path")
        
        # Initialize theme context manually since we didn't load a model
        fallback_narrator._initialize_theme_context("fantasy")
        
        # Generate a fallback narrative
        narrative = fallback_narrator._generate_fallback_narrative(
            Player.ONE.value, 
            move_column=2
        )
        
        print("\nFallback Narrative (Fantasy theme):")
        print(f"Narrative: {narrative}\n")


def main():
    """Main test function"""
    logging.info("Starting local LLM integration test...")
    
    # Test transformers availability
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
    
    try:
        from transformers import __version__ as transformers_version
        logging.info(f"Transformers library is available (version: {transformers_version})")
    except ImportError:
        logging.warning("Transformers library not found")
        logging.warning("Install with: pip install transformers")
    
    # Test model loading
    narrator = test_model_loading()
    
    # Test narrative generation
    test_narrative_generation(narrator)
    
    logging.info("Local LLM integration test completed")


if __name__ == "__main__":
    main() 