"""
Theme manager for Connect Four application
"""
from PyQt6.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    """Manages themes for the Connect Four application"""
    
    # Signal when theme changes
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the theme manager with default themes"""
        super().__init__()
        self.current_theme = "fantasy"
        self.themes = {
            "fantasy": {
                # UI Colors
                "board_color": "#8B4513",  # Brown
                "cell_color": "#F5DEB3",   # Wheat
                "p1_color": "#4169E1",     # Royal Blue
                "p2_color": "#DC143C",     # Crimson
                "background": "#F5F5DC",   # Beige
                
                # Narrative Elements
                "player1_name": "Crystal Lords",
                "player2_name": "Shadow Keepers",
                "piece_name": "crystal",
                "board_name": "Crystal Grid",
                
                # UI Text
                "title": "Crystal Conquest: Connect Four",
                "win_message": "The {player} have achieved crystal alignment!",
                "draw_message": "The Crystal Grid is full - a balance of powers!",
                
                # Sound Effects (file paths)
                "drop_sound": "assets/sounds/crystal_drop.wav",
                "win_sound": "assets/sounds/victory_chime.wav"
            },
            "scifi": {
                # UI Colors
                "board_color": "#2F4F4F",  # Dark Slate Gray
                "cell_color": "#000000",   # Black
                "p1_color": "#00FF00",     # Neon Green
                "p2_color": "#FF00FF",     # Magenta
                "background": "#0A0A2A",   # Dark blue
                
                # Narrative Elements
                "player1_name": "Quantum Collective",
                "player2_name": "Void Syndicate",
                "piece_name": "quantum token",
                "board_name": "Probability Matrix",
                
                # UI Text
                "title": "Quantum Nexus: Connect Four",
                "win_message": "The {player} have achieved quantum alignment!",
                "draw_message": "The Probability Matrix is saturated - dimensional stalemate!",
                
                # Sound Effects (file paths)
                "drop_sound": "assets/sounds/quantum_deploy.wav",
                "win_sound": "assets/sounds/victory_synth.wav"
            }
        }
    
    def switch_theme(self):
        """Toggle between fantasy and sci-fi themes"""
        self.current_theme = "scifi" if self.current_theme == "fantasy" else "fantasy"
        self.theme_changed.emit(self.current_theme)
        return self.get_current_theme()
    
    def get_current_theme(self):
        """Get the current theme settings"""
        return self.themes[self.current_theme]
    
    def get_theme_name(self):
        """Get the current theme name"""
        return self.current_theme
    
    def get_player_name(self, player_number):
        """Get the themed name for a player"""
        theme = self.get_current_theme()
        if player_number == 1:
            return theme["player1_name"]
        else:
            return theme["player2_name"]
    
    def format_message(self, message_key, **kwargs):
        """Format a themed message with variables"""
        theme = self.get_current_theme()
        if message_key in theme:
            return theme[message_key].format(**kwargs)
        return "" 