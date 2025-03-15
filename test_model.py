#!/usr/bin/env python3
"""
Simple test script for verifying the Mistral model works.
This uses minimal settings to just make sure the model can load and generate text.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

def load_and_test_model(model_path):
    """Try to load the model and generate a simple response"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch
        
        logging.info(f"Testing model at: {model_path}")
        logging.info("Loading tokenizer...")
        
        # Load tokenizer with minimal settings
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            use_fast=True,
            model_max_length=256
        )
        
        logging.info(f"Tokenizer loaded successfully")
        logging.info("Creating text generation pipeline...")
        
        # Create text generation pipeline with minimal settings
        generator = pipeline(
            "text-generation",
            model=model_path,
            tokenizer=tokenizer,
            torch_dtype=torch.float32,  # Use float32 for CPU
            device_map="auto"
        )
        
        logging.info("Pipeline created successfully! Testing generation...")
        
        # Try a simple generation
        prompt = "Write a very short narrative for a fantasy battle:"
        generation_params = {
            "max_new_tokens": 20,
            "temperature": 0.7,
            "top_p": 0.95,
            "do_sample": True,
            "num_return_sequences": 1,
            "no_repeat_ngram_size": 2,
            "early_stopping": True
        }
        
        # Generate text with a timeout
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Generation timed out")
        
        # Set timeout to 10 seconds
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)
        
        try:
            response = generator(prompt, **generation_params)
            signal.alarm(0)  # Cancel alarm
            
            if response:
                generated_text = response[0]['generated_text'][len(prompt):].strip()
                logging.info(f"Generated text: {generated_text}")
                return True
            else:
                logging.error("No response generated")
                return False
                
        except TimeoutError:
            logging.error("Generation timed out after 10 seconds")
            return False
        except Exception as e:
            logging.error(f"Error during generation: {e}")
            return False
            
    except ImportError as e:
        logging.error(f"Missing required libraries: {e}")
        return False
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return False

if __name__ == "__main__":
    # Get model path from command line or environment
    model_path = None
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        model_path = os.environ.get("LOCAL_LLM_PATH", "~/models/mistral-7b")
    
    # Expand user path if it contains ~
    model_path = os.path.expanduser(model_path)
    
    if not os.path.exists(model_path):
        logging.error(f"Model path does not exist: {model_path}")
        sys.exit(1)
    
    # Test the model
    logging.info("Starting model test...")
    success = load_and_test_model(model_path)
    
    if success:
        logging.info("Model test completed successfully!")
        sys.exit(0)
    else:
        logging.error("Model test failed!")
        sys.exit(1) 