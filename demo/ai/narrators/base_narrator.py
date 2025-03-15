"""
Base Narrator Module - Abstract base class for all narrative generators
"""
import abc
import logging
from typing import Any, Dict, List, Optional, Union


class BaseNarrator(abc.ABC):
    """
    Abstract base class for all narrative generators.
    
    This class defines the interface that all narrators must implement.
    It provides common functionality and ensures consistency across
    different narrator implementations.
    """
    
    def __init__(self):
        """Initialize the base narrator."""
        self.current_theme = "fantasy"  # Default theme
        self.story_context = ""  # Story context for the current session
        self.player_faction = "Player"  # Player faction name
        self.computer_faction = "Computer"  # Computer faction name
        self.story_generated = False  # Whether a story has been generated
        self.battle_history = []  # History of battle narratives
        self.last_narrative = ""  # Last generated narrative
    
    @abc.abstractmethod
    def generate_narrative(self, 
                           game_state: Any, 
                           current_player: Union[int, Any],
                           move_column: Optional[int] = None, 
                           game_phase: str = "midgame") -> str:
        """
        Generate a narrative description for the current game state.
        
        Args:
            game_state: The current game state
            current_player: The current player (typically 1 or 2)
            move_column: The column of the last move, if applicable
            game_phase: The current phase of the game ("opening", "midgame", "endgame")
            
        Returns:
            str: The generated narrative
        """
        pass
    
    @abc.abstractmethod
    def set_theme(self, theme: str) -> None:
        """
        Set the theme for narrative generation.
        
        Args:
            theme: The theme to use (e.g., "fantasy", "sci-fi", "western")
        """
        self.current_theme = theme.lower()
    
    def cleanup(self) -> None:
        """
        Clean up resources used by the narrator.
        
        This method should be called when the narrator is no longer needed.
        """
        # Default implementation - subclasses should override if needed
        self.battle_history = []
        logging.info("Base narrator cleanup complete")
    
    def add_to_history(self, narrative_info: Dict[str, Any]) -> None:
        """
        Add a narrative to the battle history.
        
        Args:
            narrative_info: Dictionary containing narrative information
        """
        self.battle_history.append(narrative_info)
        
        # Keep history limited to last 5 moves for context
        if len(self.battle_history) > 5:
            self.battle_history = self.battle_history[-5:]
    
    def _generate_fallback_text(self) -> str:
        """
        Generate a fallback text when the main generation fails.
        
        Returns:
            str: A simple fallback narrative
        """
        return "The battle continues with strategic moves from both sides." 