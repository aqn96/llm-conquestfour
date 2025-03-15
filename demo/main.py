#!/usr/bin/env python3
"""
LLM GameMaster: Strategic Connect Four
Main application entry point with support for local LLM battle narration
"""
import os
import sys
import logging
import argparse
from PyQt6.QtWidgets import QApplication
from app.game_master import GameMasterApp
import atexit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Connect Four with AI Narration'
    )
    parser.add_argument(
        '--use-local-llm', 
        action='store_true',
        help='Use local LLM for battle narration'
    )
    parser.add_argument(
        '--model-path', 
        type=str,
        help='Path to local LLM model'
    )
    return parser.parse_args()


def main():
    """Main application entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Process local LLM settings
    if args.use_local_llm:
        os.environ["USE_LOCAL_LLM"] = "true"
    
    # Check if environment variable is already set or set by argument
    use_local_llm = os.environ.get("USE_LOCAL_LLM", "false").lower() == "true"
    
    if use_local_llm:
        # Configure LLM path if provided as argument
        if args.model_path:
            os.environ["LOCAL_LLM_PATH"] = args.model_path
        
        # Set default path if not already set
        if "LOCAL_LLM_PATH" not in os.environ:
            default_path = os.path.expanduser("~/models/mistral-7b")
            os.environ["LOCAL_LLM_PATH"] = default_path
            logging.info(f"Using default local LLM path: {default_path}")
        
        # Log LLM settings
        logging.info("Local LLM battle narrator enabled")
        logging.info(f"Model path: {os.environ.get('LOCAL_LLM_PATH')}")
        
        # Check for transformers library
        try:
            import torch
            # Import but don't use directly - just checking availability
            from transformers import AutoModelForCausalLM  # noqa: F401
            logging.info("Using transformers library: Found")
            logging.info(f"CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    logging.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        except ImportError:
            logging.warning("Transformers library not found. Please install with:")
            logging.warning("pip install torch transformers")
            logging.warning("Continuing with fallback model...")
    
    # Launch the application
    app = QApplication(sys.argv)
    window = GameMasterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
