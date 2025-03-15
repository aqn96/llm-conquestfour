"""
Base Model Loader - Foundation for all model loaders
"""
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseModelLoader(ABC):
    """
    Abstract base class for all model loaders.
    
    This class defines the interface that all model loaders must implement
    and provides common functionality for model management.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize the model loader.
        
        Args:
            model_path: Path to the model files
            device: Device to load the model on ("cpu", "cuda", "auto")
        """
        self.model_path = model_path or os.environ.get("LOCAL_LLM_PATH")
        self.device = device
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        self.is_ready = False
        self.load_attempt_count = 0
        
        # For memory tracking
        self.initial_memory = None
        self.last_check_memory = None
        
        # Configure logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def load_model(self) -> bool:
        """
        Load the model into memory.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the loaded model.
        
        Args:
            prompt: The prompt to generate from
            **kwargs: Additional generation parameters
            
        Returns:
            str: The generated text
        """
        pass
    
    def cleanup_resources(self) -> None:
        """
        Clean up any resources used by the model.
        """
        try:
            # Generic cleanup operations
            if hasattr(self, 'pipeline') and self.pipeline is not None:
                del self.pipeline
                self.pipeline = None
                
            if hasattr(self, 'model') and self.model is not None:
                del self.model
                self.model = None
                
            if hasattr(self, 'tokenizer') and self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
                
            self.is_loaded = False
            self.is_ready = False
            
            # Force garbage collection
            import gc
            gc.collect()
            
            if hasattr(self, 'logger'):
                self.logger.info("Resources cleaned up successfully")
                
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error during cleanup: {e}")
            else:
                print(f"Error during cleanup: {e}")
    
    def check_model_status(self) -> bool:
        """
        Check if the model is loaded and ready.
        
        Returns:
            bool: True if the model is loaded and ready
        """
        return self.is_loaded and self.is_ready
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dict: Dictionary with model information
        """
        return {
            "model_path": self.model_path,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "is_ready": self.is_ready,
            "load_attempts": self.load_attempt_count
        } 