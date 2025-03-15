"""
Fallback Narrator Module - Provides simple, non-AI narrative generation
"""
import logging
import random
from typing import List, Optional
import time

from ai.narrators.base_narrator import BaseNarrator


class FallbackNarrator(BaseNarrator):
    """
    A fallback narrator to use when AI-based narration is unavailable.
    Provides simple template-based narrative generation.
    """
    
    def __init__(self, theme="fantasy"):
        """Initialize the fallback narrator with default theme and templates."""
        super().__init__()
        self.current_theme = theme
        self._initialize_theme_context()
        self._set_default_faction_names()
        
        # Set up story context
        self.story_context = "In a world divided by ancient rivalries..."
        self.story_generated = False
        self.battle_history = []
        self.last_narrative = ""
        
        logging.info(f"Theme set to {self.current_theme}")
    
    def _initialize_theme_context(self):
        """Set up the theme-specific context for narrative generation."""
        # Theme-based templates for different game phases
        self.templates = {
            "opening": {
                "fantasy": [
                    "The {player} makes a bold opening move.",
                    "The ancient contest begins as {player} places their first piece.",
                ],
                "sci-fi": [
                    "The {player} initializes their strategy protocol.",
                    "First quantum piece deployed by the {player}.",
                ],
                "western": [
                    "The {player} draws first in this frontier showdown.",
                    "This dusty battleground sees its first move from {player}.",
                ]
            },
            "midgame": {
                "fantasy": [
                    "The {player} continues their mystical strategy.",
                    "A tactical maneuver from the {player} shifts the magical balance.",
                ],
                "sci-fi": [
                    "The {player} executes subroutine alpha-seven.",
                    "Tactical algorithms guide the {player}'s decisive move.",
                ],
                "western": [
                    "The {player} ain't backing down in this saloon standoff.",
                    "A strategic play from {player} as the tension rises.",
                ]
            },
            "endgame": {
                "fantasy": [
                    "The final enchantments are cast as {player} nears victory.",
                    "The mystical conflict reaches its climax with {player}'s move.",
                ],
                "sci-fi": [
                    "Endgame protocols activated by the {player}.",
                    "The {player} calculates final victory parameters.",
                ],
                "western": [
                    "The showdown intensifies as {player} makes their final stand.",
                    "High noon approaches as {player} prepares for the final shot.",
                ]
            }
        }
    
    def _set_default_faction_names(self):
        """Set faction names based on the current theme."""
        themes = {
            "fantasy": ("Crystal Lords", "Shadow Keepers"),
            "sci-fi": ("Quantum Collective", "Void Syndicate"),
            "western": ("Desperados", "Lawmen")
        }
        
        default = ("Team Alpha", "Team Omega")
        self.player_faction, self.computer_faction = themes.get(
            self.current_theme, default)
    
    def set_theme(self, theme: str) -> None:
        """
        Set the narrative theme.
        
        Args:
            theme: The theme to use (fantasy, sci-fi, western)
        """
        if theme not in ["fantasy", "sci-fi", "western"]:
            theme = "fantasy"  # Default to fantasy if theme not supported
        
        self.current_theme = theme
        self._initialize_theme_context()
        self._set_default_faction_names()
        logging.info(f"Theme set to {self.current_theme}")
    
    def generate_narrative(self, current_player=None, move_column=None, 
                           game_phase=None) -> str:
        """
        Generate a narrative based on the current game state.
        
        Args:
            current_player: The player who made the last move
            move_column: The column where the piece was placed
            game_phase: The current phase of the game
            
        Returns:
            A string containing the generated narrative
        """
        try:
            # Determine game phase if not provided
            if game_phase is None:
                if len(self.battle_history) < 6:
                    game_phase = "opening"
                elif len(self.battle_history) < 20:
                    game_phase = "midgame"
                else:
                    game_phase = "endgame"
            
            print(f"Current theme: {self.current_theme}")
            print(f"Determined game phase: {game_phase}")
            logging.info(f"Fallback narrator generating narrative for phase: {game_phase}")
            
            # Get templates for current theme and phase
            theme_templates = self.templates.get(game_phase, {}).get(
                self.current_theme, ["The game continues..."])
            
            # Select a random template
            template = random.choice(theme_templates)
            
            # Determine the player name
            player_name = "Unknown player"
            if current_player == 1:
                player_name = self.player_faction
            elif current_player == 2:
                player_name = self.computer_faction
            
            # Fill in the template
            narrative = template.format(player=player_name)
            
            # Add to history
            self.add_to_history(narrative)
            self.last_narrative = narrative
            
            return narrative
        except Exception as e:
            logging.error(f"Error generating narrative: {e}")
            return self._generate_fallback_text()
    
    def add_to_history(self, narrative):
        """Add a narrative to the battle history."""
        self.battle_history.append(narrative)
        # Keep history at a reasonable size
        if len(self.battle_history) > 30:
            self.battle_history = self.battle_history[-30:]
    
    def _generate_fallback_text(self) -> str:
        """Generate basic fallback text if narrative generation fails."""
        fallback_texts = [
            "The battle continues...",
            "Strategy unfolds on the battlefield...",
            "Tactical moves and countermoves...",
            "The conflict progresses..."
        ]
        return random.choice(fallback_texts)
    
    def cleanup_resources(self) -> None:
        """
        Clean up resources used by the narrator.
        
        This method should be called when the narrator is no longer needed.
        """
        # Default implementation - subclasses should override if needed
        self.battle_history = []
        logging.info("Fallback narrator cleanup complete") 