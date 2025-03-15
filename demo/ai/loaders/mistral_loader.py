"""
Mistral Model Loader - Implementation for Mistral 7B models
"""
import logging
import os
import time
from typing import Any, Dict, Optional, Union

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextGenerationPipeline,
    pipeline,
)

from ai.loaders.base_model_loader import BaseModelLoader
from ai.utils.text_generation import generate_with_timeout, truncate_prompt


class MistralLoader(BaseModelLoader):
    """
    Loader for Mistral 7B models.
    
    This class implements the BaseModelLoader interface for Mistral 7B models,
    providing optimized loading and generation capabilities.
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        device: str = "auto",
        use_float16: bool = True,
        context_length: int = 128,
        generation_timeout: int = 5
    ):
        """
        Initialize the Mistral loader.
        
        Args:
            model_path: Path to the model files
            device: Device to load the model on ("cpu", "cuda", "auto")
            use_float16: Whether to use float16 precision
            context_length: Context length for the model
            generation_timeout: Timeout for text generation in seconds
        """
        super().__init__(model_path, device)
        self.use_float16 = use_float16
        self.context_length = context_length
        self.generation_timeout = generation_timeout
        
        # Override generation timeout from environment if present
        env_timeout = os.environ.get("GENERATION_TIMEOUT")
        if env_timeout:
            try:
                self.generation_timeout = int(env_timeout)
                self.logger.info(f"Set generation timeout to {self.generation_timeout}s from env")
            except ValueError:
                self.logger.warning(f"Invalid GENERATION_TIMEOUT: {env_timeout}")
    
    def load_model(self) -> bool:
        """
        Load the Mistral model into memory.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        self.load_attempt_count += 1
        self.logger.info(f"Loading Mistral model from {self.model_path} (attempt {self.load_attempt_count})")
        
        try:
            start_time = time.time()
            
            # Set the appropriate torch dtype based on configuration
            torch_dtype = torch.float16 if self.use_float16 else torch.float32
            
            # Load tokenizer with minimal settings
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                use_fast=True,
                padding_side="left",
            )
            
            # Load model with optimized settings
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch_dtype,
                device_map=self.device,
                low_cpu_mem_usage=True,
            )
            
            # Create the generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map=self.device,
            )
            
            load_time = time.time() - start_time
            self.logger.info(f"Mistral model loaded in {load_time:.2f} seconds")
            
            self.is_loaded = True
            self.is_ready = True
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading Mistral model: {e}")
            self.cleanup_resources()  # Clean up any partially loaded resources
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Mistral model.
        
        Args:
            prompt: The prompt to generate from
            **kwargs: Additional generation parameters
            
        Returns:
            str: The generated text
        """
        if not self.check_model_status():
            self.logger.warning("Model not ready, returning default response")
            return "The strategic battle continues."
        
        # Truncate prompt if too long
        prompt = truncate_prompt(prompt, self.context_length * 2)
        
        # Default generation parameters
        default_params = {
            "max_new_tokens": 30,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "num_return_sequences": 1,
        }
        
        # Override defaults with any provided parameters
        generation_params = {**default_params, **kwargs}
        
        # Define a function that will be executed with timeout
        def _generate():
            generation_output = self.pipeline(
                prompt,
                **generation_params
            )
            if generation_output and len(generation_output) > 0:
                generated_text = generation_output[0].get("generated_text", "")
                # Extract only the newly generated part (after the prompt)
                if generated_text.startswith(prompt):
                    return generated_text[len(prompt):].strip()
                return generated_text.strip()
            return ""
        
        # Generate with timeout protection
        result = generate_with_timeout(
            lambda p, **kw: _generate(),
            prompt,
            timeout=self.generation_timeout
        )
        
        return result or "The tactical battle continues with careful positioning." 