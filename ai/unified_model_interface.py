"""
Unified Model Interface - Central interface for all AI functionality
"""
import logging
import os
from typing import Dict, List, Optional, Tuple, Union

from ai.loaders.base_model_loader import BaseModelLoader
from ai.loaders.mistral_loader import MistralLoader
from ai.narrators.base_narrator import BaseNarrator
from ai.narrators.fallback_narrator import FallbackNarrator
from ai.utils.text_generation import select_themed_response


class UnifiedModelInterface:
    """
    Central interface for all AI model interactions in the application.
    
    This class provides a unified interface to access all AI functionality,
    including model loading, text generation, and narrative generation.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the unified model interface.
        
        Args:
            model_path: Path to the model files
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_path = model_path or os.environ.get("LOCAL_LLM_PATH")
        self.model_loader = None
        self.narrator = None
        self.model_type = "mistral"  # Default model type
        self.model_ready = False
        self.use_fallback = False
        
        # Theme settings
        self.current_theme = "fantasy"  # Default theme
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """
        Initialize the necessary components based on configuration.
        """
        # Determine model type from environment or default
        env_model_type = os.environ.get("MODEL_TYPE", "").lower()
        if env_model_type:
            self.model_type = env_model_type
        
        # Initialize the appropriate model loader
        if self.model_type == "mistral":
            self.model_loader = MistralLoader(
                model_path=self.model_path,
                device="auto",
                use_float16=True,
                context_length=128,
                generation_timeout=5
            )
        else:
            self.logger.warning(f"Unknown model type: {self.model_type}, defaulting to Mistral")
            self.model_loader = MistralLoader(model_path=self.model_path)
        
        # Initialize the narrator
        self._initialize_narrator()
    
    def _initialize_narrator(self) -> None:
        """
        Initialize the appropriate narrator based on configuration.
        """
        # For now, we only have the fallback narrator
        # In the future, more narrator types can be added
        self.narrator = FallbackNarrator(theme=self.current_theme)
        
        # Set the theme
        if self.current_theme:
            self.narrator.set_theme(self.current_theme)
    
    def load_model(self) -> bool:
        """
        Load the AI model.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        if not self.model_loader:
            self.logger.error("No model loader initialized")
            return False
        
        try:
            # Attempt to load the model
            result = self.model_loader.load_model()
            
            if result:
                self.model_ready = True
                self.use_fallback = False
                self.logger.info(f"Model {self.model_type} loaded successfully")
            else:
                self.model_ready = False
                self.use_fallback = True
                self.logger.warning("Model loading failed, using fallback mode")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            self.model_ready = False
            self.use_fallback = True
            return False
    
    def check_model_status(self) -> bool:
        """
        Check if the model is loaded and ready.
        
        Returns:
            bool: True if the model is loaded and ready
        """
        if self.model_loader:
            return self.model_loader.check_model_status()
        return False
    
    def set_theme(self, theme: str) -> None:
        """
        Set the theme for narrative generation.
        
        Args:
            theme: The theme to use (e.g., "fantasy", "sci-fi", "western")
        """
        self.current_theme = theme
        if self.narrator:
            self.narrator.set_theme(theme)
        self.logger.info(f"Theme set to {theme}")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the loaded model.
        
        Args:
            prompt: The prompt to generate from
            **kwargs: Additional generation parameters
            
        Returns:
            str: The generated text
        """
        if self.use_fallback or not self.model_ready:
            self.logger.info("Using fallback text generation")
            return select_themed_response(self.current_theme)
        
        try:
            result = self.model_loader.generate_text(prompt, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Error in text generation: {e}")
            return select_themed_response(self.current_theme)
    
    def generate_narrative(
        self,
        game_state: Dict,
        current_player: str,
        move_column: Optional[int] = None,
        game_phase: str = "midgame"
    ) -> str:
        """
        Generate a narrative description for the game state.
        
        Args:
            game_state: The current game state
            current_player: The current player ("player" or "computer")
            move_column: The column where the last move was made (if any)
            game_phase: The current phase of the game (opening, midgame, endgame)
            
        Returns:
            str: A narrative description of the game state
        """
        if self.narrator:
            try:
                return self.narrator.generate_narrative(
                    game_state, current_player, move_column, game_phase
                )
            except Exception as e:
                self.logger.error(f"Error in narrative generation: {e}")
                return select_themed_response(self.current_theme)
        else:
            self.logger.warning("No narrator available, using themed response")
            return select_themed_response(self.current_theme)
    
    def cleanup_resources(self) -> None:
        """
        Clean up any resources used by the models.
        """
        try:
            # Clean up model loader resources
            if self.model_loader:
                self.model_loader.cleanup_resources()
                self.model_ready = False
            
            # Clean up narrator resources
            if self.narrator:
                self.narrator.cleanup_resources()
            
            self.logger.info("Resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dict: Dictionary with model information
        """
        info = {
            "model_type": self.model_type,
            "model_ready": self.model_ready,
            "use_fallback": self.use_fallback,
            "theme": self.current_theme,
        }
        
        if self.model_loader:
            info.update(self.model_loader.get_model_info())
            
        return info 