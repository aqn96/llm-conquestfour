"""
Controller for managing application themes
"""
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QObject, pyqtSignal


class ThemeController(QObject):
    """
    Controller for managing and switching between application themes
    """
    
    # Signal for theme changes
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = "fantasy"  # Default theme
        self.app = None
        
    def register_app(self, app):
        """
        Register the main application instance with the theme controller
        
        Args:
            app: The main GameMasterApp instance
        """
        self.app = app
    
    def set_theme(self, theme_name):
        """
        Set the application theme
        
        Args:
            theme_name: The name of the theme to set (e.g., 'fantasy', 'scifi')
        """
        self.current_theme = theme_name
        
        if theme_name == "fantasy":
            self._apply_fantasy_theme()
        elif theme_name == "scifi":
            self._apply_scifi_theme()
        else:
            # Default to fantasy if theme not recognized
            self._apply_fantasy_theme()
            
        # Emit signal that theme has changed
        self.theme_changed.emit(theme_name)
            
    def switch_theme(self):
        """Switch to the next theme in the rotation"""
        if self.current_theme == "fantasy":
            self.set_theme("scifi")
        else:
            self.set_theme("fantasy")
            
    def get_theme_name(self):
        """
        Get the current theme name
        
        Returns:
            str: The name of the current theme
        """
        return self.current_theme
        
    def get_player_name(self, player_number):
        """Get the themed name for a player"""
        if self.current_theme == "fantasy":
            return "Crystal Lords" if player_number == 1 else "Shadow Keepers"
        else:  # sci-fi
            return "Quantum Collective" if player_number == 1 else "Void Syndicate"
    
    def _apply_fantasy_theme(self):
        """Apply the fantasy theme to the application"""
        if not self.app:
            return
            
        # Set application palette
        palette = QPalette()
        
        # Set colors appropriate for fantasy theme
        # Background
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 52, 75))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        
        # Buttons
        palette.setColor(QPalette.ColorRole.Button, QColor(90, 75, 140))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        
        # Highlights
        palette.setColor(QPalette.ColorRole.Highlight, QColor(140, 90, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Apply the palette
        self.app.setPalette(palette)
        
    def _apply_scifi_theme(self):
        """Apply the sci-fi theme to the application"""
        if not self.app:
            return
            
        # Set application palette
        palette = QPalette()
        
        # Set colors appropriate for sci-fi theme
        # Background
        palette.setColor(QPalette.ColorRole.Window, QColor(25, 35, 45))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 240, 255))
        
        # Buttons
        palette.setColor(QPalette.ColorRole.Button, QColor(40, 90, 120))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 240, 255))
        
        # Highlights
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 160, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Apply the palette
        self.app.setPalette(palette) 