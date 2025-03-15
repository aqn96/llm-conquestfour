"""
Model Controller - Manages the AI model interaction in the application
"""
import logging
import threading
from typing import Dict, Optional

from ai.unified_model_interface import UnifiedModelInterface


class ModelController:
    """
    Controller for managing AI model interactions.
    
    This class serves as an interface between the application and the AI model,
    handling loading, narrative generation, and resource management.
    """
    
    def __init__(self):
        """Initialize the model controller."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_interface = UnifiedModelInterface()
        self.load_lock = threading.Lock()
        self.is_loading = False
        self.theme = "fantasy"  # Default theme
    
    def load_model(self) -> bool:
        """
        Load the AI model in a separate thread.
        
        Returns:
            bool: True if loading started successfully
        """
        with self.load_lock:
            if self.is_loading:
                self.logger.info("Model loading already in progress")
                return False
            
            self.is_loading = True
        
        # Start loading in a separate thread
        loading_thread = threading.Thread(
            target=self._load_model_thread,
            daemon=True
        )
        loading_thread.start()
        
        return True
    
    def _load_model_thread(self) -> None:
        """Load the model in a separate thread."""
        try:
            self.logger.info("Starting model loading in thread")
            
            # Set the theme before loading
            self.model_interface.set_theme(self.theme)
            
            # Load the model
            result = self.model_interface.load_model()
            
            if result:
                self.logger.info("Model loading completed successfully")
            else:
                self.logger.warning("Model loading failed, using fallback mode")
                
        except Exception as e:
            self.logger.error(f"Error in model loading thread: {e}")
        finally:
            with self.load_lock:
                self.is_loading = False
    
    def is_model_ready(self) -> bool:
        """
        Check if the model is loaded and ready.
        
        Returns:
            bool: True if the model is loaded and ready
        """
        return self.model_interface.check_model_status()
    
    def set_theme(self, theme: str) -> None:
        """
        Set the theme for narrative generation.
        
        Args:
            theme: The theme to use (e.g., "fantasy", "sci-fi", "western")
        """
        self.theme = theme
        self.model_interface.set_theme(theme)
        self.logger.info(f"Theme set to {theme}")
    
    def generate_narrative(self, game_state: Dict) -> str:
        """
        Generate a narrative description for the game state.
        
        Args:
            game_state: The current game state
            
        Returns:
            str: A narrative description of the game state
        """
        # Check if model is ready
        if not self.is_model_ready() and not self.model_interface.use_fallback:
            self.logger.warning("Model not ready, using fallback narrator")
        
        # Extract game phase
        game_phase = "midgame"
        if game_state.get("move_count", 0) < 4:
            game_phase = "opening"
        elif game_state.get("game_over", False):
            game_phase = "endgame"
        
        # Extract current player and move column
        current_player = game_state.get("current_player", "player")
        move_column = game_state.get("last_move_column")
        
        # Generate narrative
        try:
            narrative = self.model_interface.generate_narrative(
                game_state, current_player, move_column, game_phase
            )
            return narrative
        except Exception as e:
            self.logger.error(f"Error generating narrative: {e}")
            return "The game continues with strategic moves from both sides."
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dict: Dictionary with model information
        """
        return self.model_interface.get_model_info()
    
    def cleanup_resources(self) -> None:
        """
        Clean up any resources used by the model.
        """
        try:
            self.model_interface.cleanup_resources()
            self.logger.info("Resources cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}") 