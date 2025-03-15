"""
Handler for user input events in the game
"""
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import QTimer


class UserInputHandler:
    """Handles user input events like button clicks"""
    
    def __init__(self, app):
        """
        Initialize the user input handler
        
        Args:
            app: Reference to the main application
        """
        self.app = app
        
        # Track current and initial game settings
        self.current_difficulty = "Medium"
        self.current_theme = "Fantasy"
        self.initial_difficulty = self.current_difficulty
        self.initial_theme = self.current_theme
        self.settings_changed = False
        
        # Initialize with default settings
        if hasattr(self.app, 'game_controller'):
            self._apply_difficulty(self.current_difficulty)
        
        if hasattr(self.app, 'theme_controller'):
            self._apply_theme(self.current_theme)
        
        # Schedule a check to ensure UI state is consistent
        QTimer.singleShot(100, self._validate_settings)
        
    def on_column_selected(self, column):
        """
        Handle user selecting a column for their move
        
        Args:
            column: The column index (0-6) the user selected
        """
        print(f"Column selected: {column}, Game over: {self.app.game_controller.is_game_over()}")
        
        # Ignore if game is over
        if self.app.game_controller.is_game_over():
            return
            
        # Try to make the player's move
        success = self.app.game_controller.make_player_move(column)
        
        if success:
            # Update the board display
            self.app.state_handler.update_board()
            
            # Check if the game is over after player's move
            if self.app.game_controller.is_game_over():
                self.app.state_handler.generate_narrative(column)
                self._handle_game_over()
                return
                
            # Schedule AI's move
            self._schedule_ai_move()
        
    def on_difficulty_changed(self, difficulty):
        """Handle difficulty setting change"""
        self.current_difficulty = difficulty
        self._apply_difficulty(difficulty)
        self._check_settings_changed()
        
    def on_theme_changed(self, theme):
        """Handle theme setting change"""
        self.current_theme = theme
        self._apply_theme(theme)
        self._check_settings_changed()
        
        # Generate a new narrative with the new theme
        if hasattr(self.app, 'state_handler'):
            self.app.state_handler.generate_narrative()
        
    def _check_settings_changed(self):
        """Check if settings have changed from initial values"""
        self.settings_changed = (
            self.current_difficulty != self.initial_difficulty or
            self.current_theme != self.initial_theme
        )
        
    def _apply_difficulty(self, difficulty):
        """Apply difficulty setting to game"""
        if hasattr(self.app, 'game_controller'):
            if difficulty == "Easy":
                # Make Easy difficulty truly easy (level 1-3)
                self.app.game_controller.ai.max_depth = 1
                # Also update the thermal AI
                if hasattr(self.app.game_controller, 'thermal_ai'):
                    self.app.game_controller.thermal_ai.max_depth = 1
            elif difficulty == "Medium":
                # Medium difficulty (level 4-7)
                self.app.game_controller.ai.max_depth = 3
                # Also update the thermal AI
                if hasattr(self.app.game_controller, 'thermal_ai'):
                    self.app.game_controller.thermal_ai.max_depth = 2
            elif difficulty == "Hard":
                # Hard difficulty (level 8-10)
                self.app.game_controller.ai.max_depth = 5
                # Also update the thermal AI
                if hasattr(self.app.game_controller, 'thermal_ai'):
                    self.app.game_controller.thermal_ai.max_depth = 3
                
    def _apply_theme(self, theme):
        """Apply theme setting to game"""
        if hasattr(self.app, 'theme_controller'):
            theme_name = theme.lower()
            self.app.theme_controller.set_theme(theme_name)
            
    def _schedule_ai_move(self):
        """Schedule the AI's move after a short delay"""
        # Disable column buttons while AI is "thinking"
        self._set_buttons_enabled(False)
        
        # Show thinking message
        if hasattr(self.app, 'narrative_display'):
            self.app.narrative_display.set_message(
                "AI is thinking...",
                color="#3498db"
            )
            
        # Schedule AI move after a delay to simulate thinking
        QTimer.singleShot(1000, self._make_ai_move)
        
    def _make_ai_move(self):
        """Make the AI's move"""
        # Make the AI move
        column = self.app.game_controller.make_ai_move()
        
        if column is not None:
            # Update the board display
            self.app.state_handler.update_board()
            
            # Generate narrative for the AI's move
            self.app.state_handler.generate_narrative(column)
            
            # Check if the game is over after AI's move
            if self.app.game_controller.is_game_over():
                self._handle_game_over()
            else:
                # Re-enable column buttons for player's next move
                self._set_buttons_enabled(True)
        else:
            # Something went wrong with the AI move
            if hasattr(self.app, 'narrative_display'):
                self.app.narrative_display.set_message(
                    "AI couldn't make a move. Your turn.",
                    color="#e74c3c"
                )
            self._set_buttons_enabled(True)
            
    def _handle_game_over(self):
        """Handle game over state"""
        # Disable column buttons
        self._set_buttons_enabled(False)
        
        # Get game status
        status = self.app.game_controller.get_game_status()
        
        # Get winner and handle Player enum if needed
        winner = status['winner']
        if hasattr(winner, 'value'):  # Check if it's a Player enum
            winner = winner.value
        
        # Show appropriate message
        if hasattr(self.app, 'narrative_display'):
            if winner == 1:
                self.app.narrative_display.set_message(
                    "You win! Congratulations!",
                    color="#2ecc71",
                    bold=True
                )
            elif winner == 2:
                self.app.narrative_display.set_message(
                    "AI wins! Better luck next time.",
                    color="#e74c3c",
                    bold=True
                )
            else:
                self.app.narrative_display.set_message(
                    "It's a draw! The board is full.",
                    color="#f39c12",
                    bold=True
                )
    
    def _set_buttons_enabled(self, enabled):
        """
        Enable or disable all column selection buttons
        
        Args:
            enabled: Boolean indicating whether buttons should be enabled
        """
        for col in range(7):
            button_name = f"colButton_{col}"
            button = self.app.game_container.findChild(QPushButton, button_name)
            if button:
                button.setEnabled(enabled)
    
    def _validate_settings(self):
        """Validate settings and update UI state accordingly"""
        if hasattr(self.app, 'new_game_button'):
            # Always enable the new game button
            self.app.new_game_button.setEnabled(True)
                
    def new_game(self):
        """Start a new game with current settings"""
        # Apply current settings
        self._apply_difficulty(self.current_difficulty)
        self._apply_theme(self.current_theme)
        
        # Reset the game state
        self.app.game_controller.new_game()
        
        # Clear all board cells visually first
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app.game_container.findChild(QLabel, cell_key)
                if cell:
                    cell.clear()
                    cell.setStyleSheet("""
                        background-color: #34495e;
                        border-radius: 30px;
                        border: 2px solid #2c3e50;
                    """)
        
        # Update the board display
        self.app.state_handler.update_board()
        
        # Enable all buttons
        self._set_buttons_enabled(True)
        
        # Update initial settings to match current settings
        self.initial_difficulty = self.current_difficulty
        self.initial_theme = self.current_theme
        self.settings_changed = False
        self._validate_settings()
        
        # Update message
        if hasattr(self.app, 'narrative_display'):
            self.app.narrative_display.set_message(
                f"New game started with {self.current_difficulty} difficulty and {self.current_theme} theme! Your turn to move.",
                color="#2ecc71",  # Green message
                bold=True
            ) 