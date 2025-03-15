"""
Main application window for LLM GameMaster
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import QTimer, Qt
import os
import logging
import atexit

from app.ui.window_setup import configure_window_appearance
from app.ui.layout_builder import build_main_layout
from app.controllers.game_controller import GameController
from app.controllers.model_controller import ModelController
from app.controllers.theme_controller import ThemeController
from app.controllers.temperature_controller import TemperatureController
from app.controllers.intro_controller import IntroController
from app.handlers.user_input_handler import UserInputHandler
from app.handlers.game_state_handler import GameStateHandler


class GameMasterApp(QMainWindow):
    """Main window for the LLM GameMaster application"""
    
    def __init__(self):
        super().__init__()
        
        # Set up window appearance
        configure_window_appearance(self)
        
        # Set minimum size for the main window
        self.setMinimumSize(1000, 700)
        
        # Create stacked widget to hold different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize controllers
        self.theme_controller = ThemeController()
        self.game_controller = GameController()
        # Initialize model controller with our refactored version
        self.model_controller = ModelController()
        self.temp_controller = TemperatureController()
        
        # Register app with theme controller
        self.theme_controller.register_app(self)
        
        # Create intro screen
        self.intro_controller = IntroController()
        self.stacked_widget.addWidget(self.intro_controller)
        
        # Create game container
        self.game_container = QWidget()
        self.game_container.setLayout(QVBoxLayout())
        self.stacked_widget.addWidget(self.game_container)
        
        # Create loading screen container
        self.loading_container = QWidget()
        self.loading_container.setLayout(QVBoxLayout())
        self.loading_container.layout().setContentsMargins(50, 50, 50, 50)
        self.loading_container.layout().setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        
        # Add loading message
        self.loading_label = QLabel(
            "Loading AI Storyteller...\nThis may take a moment."
        )
        self.loading_label.setStyleSheet(
            "font-size: 24px; color: #3498db; font-weight: bold;"
        )
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_container.layout().addWidget(self.loading_label)
        
        # Add to stacked widget
        self.stacked_widget.addWidget(self.loading_container)
        
        # Set up handlers
        self.player_name = "Player"
        self.input_handler = UserInputHandler(self)
        self.state_handler = GameStateHandler(self)
        
        # Connect intro controller signals
        self.intro_controller.start_game_signal.connect(self.start_game)
        
        # Show intro screen by default
        self.show_intro_screen()
        
        # Connect controller signals
        self._connect_signals()
        
        # Start temperature monitoring
        self._setup_monitoring()
        
        # Initialize model controller and start loading the model
        self.model_controller.load_model()
        
        # Register cleanup handler
        atexit.register(self.cleanup)
        
    def show_intro_screen(self):
        """Show the intro/title screen"""
        self.stacked_widget.setCurrentWidget(self.intro_controller)
        
    def show_loading_screen(self):
        """Show the loading screen"""
        self.stacked_widget.setCurrentWidget(self.loading_container)
        
    def start_game(self, settings):
        """
        Start a new game with the given settings
        
        Args:
            settings: Dictionary containing game settings
        """
        # First show loading screen while model loads
        self.show_loading_screen()
        
        # Store settings for when model is ready
        self.pending_game_settings = settings
        
        # If model is already loaded, proceed directly
        # Otherwise wait for model_loaded signal
        if self.model_controller.is_model_ready():
            self._initialize_game_with_settings(settings)
        
    def _initialize_game_with_settings(self, settings):
        """Initialize the game with settings after model is loaded"""
        # Update player name
        if 'player_name' in settings:
            self.player_name = settings['player_name']
            self.setWindowTitle(
                f"LLM GameMaster: Connect Four - {self.player_name}"
            )
        
        # Apply difficulty
        if 'difficulty' in settings:
            self.input_handler.current_difficulty = settings['difficulty']
            self.input_handler.initial_difficulty = settings['difficulty']
            self.input_handler._apply_difficulty(settings['difficulty'])
        
        # Apply theme
        theme = 'fantasy'  # Default
        if 'themes' in settings and settings['themes']:
            theme = settings['themes'][0]
        self.input_handler.current_theme = (
            'Sci-Fi' if theme == 'sci-fi' else 'Fantasy'
        )
        self.input_handler.initial_theme = self.input_handler.current_theme
        self.input_handler._apply_theme(
            self.input_handler.current_theme
        )
        
        # Reset the settings_changed flag
        self.input_handler.settings_changed = False
        self.input_handler._validate_settings()
        
        # Switch to game screen
        self.stacked_widget.setCurrentWidget(self.game_container)
        
        # Clear any existing contents from the game layout
        layout = self.game_container.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # Build UI for the game
        print("Building game UI")
        build_main_layout(self)
        
        # Reset the game
        self.game_controller.new_game()
        
        # Ensure board is updated with initial state
        print("Updating initial board state")
        self.state_handler.update_board()
        
        # Add debugging to verify the board state
        print("Initial board state after starting new game:")
        self.game_controller.game.print_board()
        
    def _connect_signals(self):
        """Connect controller signals to handlers"""
        # Our refactored ModelController doesn't have the model_loaded signal
        # Instead, we'll check the model status directly
        pass
        
    def _on_model_loaded(self, success):
        """Handle model loaded event"""
        # With our refactored controller, we need to use the is_model_ready method
        # If we have pending game settings, initialize the game
        if hasattr(self, 'pending_game_settings'):
            self._initialize_game_with_settings(self.pending_game_settings)
            delattr(self, 'pending_game_settings')
            
    def _setup_monitoring(self):
        """Set up temperature monitoring"""
        self.temp_timer = QTimer()
        self.temp_timer.timeout.connect(self.temp_controller.update_display)
        self.temp_timer.start(1000)
        
    def cleanup(self):
        """Cleanup resources before exit"""
        logging.info("Application cleaning up resources before exit")
        try:
            # Clean up model resources
            if hasattr(self, 'model_controller') and self.model_controller is not None:
                if hasattr(self.model_controller, 'cleanup_resources'):
                    self.model_controller.cleanup_resources()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}") 