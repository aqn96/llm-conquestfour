"""
Handler for game state updates and UI synchronization
"""
from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer
import numpy as np
import logging

from game.connect_four import Player
from ai.context_prompter import ContextAwarePrompter


class GameStateHandler:
    """Handles updates to the game state and keeps UI in sync"""
    
    def __init__(self, app):
        """
        Initialize the game state handler
        
        Args:
            app: Reference to the main application
        """
        self.app = app
        print("Initializing GameStateHandler - loading player pieces")
        
        # Always reload pieces to ensure they're fresh
        self.player_images = {
            0: None,  # Empty cell
            1: self._load_player_piece("red"),  # Player 1
            2: self._load_player_piece("yellow")  # Player 2
        }
        
        # Store fallback colors for when images aren't available
        self.player_colors = {
            1: "#e74c3c",  # Red for Player 1
            2: "#f1c40f"   # Yellow for Player 2
        }
        
        # Initialize context prompter for narrative generation
        self.context_prompter = ContextAwarePrompter()
        
        # Track if model is loaded
        self.model_loaded = False
        
        # Log whether images were loaded successfully
        print(f"Player 1 image loaded: {self.player_images[1] is not None}")
        print(f"Player 2 image loaded: {self.player_images[2] is not None}")
        
        # Force initial update to ensure correct initial state
        QTimer.singleShot(100, self.force_update_all_cells)
        
    def update_board(self):
        """Update the UI board based on current game state"""
        # Get current board state
        board = self.app.game_controller.get_board()
        print("Updating board display with current game state")
        
        # Debug: Print the raw board data
        if isinstance(board, np.ndarray):
            print(f"Board shape: {board.shape}, dtype: {board.dtype}")
            print(board)
        else:
            print(f"Board type: {type(board)}")
        
        # Force every cell to clear first to ensure clean state
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app.game_container.findChild(QLabel, cell_key)
                if cell:
                    # Start with clean state
                    cell.clear()
                    cell.setStyleSheet("""
                        background-color: #34495e;
                        border-radius: 30px;
                        border: 2px solid #2c3e50;
                    """)
        
        # Now update with current state
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app.game_container.findChild(QLabel, cell_key)
                if cell:
                    try:
                        player = board[row][col]
                        # Debug: Print the player value being used to update this cell
                        print(f"Cell {row},{col}: player={player}, "
                              f"type={type(player)}")
                        self._update_cell(cell, player)
                    except (IndexError, TypeError) as e:
                        print(f"Error updating cell {row},{col}: {e}")
                        # Reset the cell if there's an error
                        cell.clear()
                        cell.setStyleSheet("""
                            background-color: #34495e;
                            border-radius: 30px;
                            border: 2px solid #2c3e50;
                        """)
        
        # Check if game is over
        if self.app.game_controller.is_game_over():
            self._handle_game_over()
        
        # When board is empty, trigger a new narrative with opening phase
        is_empty_board = True
        for row in range(6):
            for col in range(7):
                if board[row][col] != 0:
                    is_empty_board = False
                    break
            if not is_empty_board:
                break
        
        if is_empty_board:
            # This is a new game, generate story context
            print("Empty board detected - generating new story and faction names")
            # First clear any previous narratives to avoid confusion
            if hasattr(self.app, 'narrative_display'):
                self.app.narrative_display.clear_narrative()
                theme_name = self.app.theme_controller.get_theme_name()
                self.app.narrative_display.set_message(
                    f"New game started with {self.app.input_handler.current_difficulty} "
                    f"difficulty and {theme_name.capitalize()} theme! Your turn to move.",
                    color="#2ecc71",
                    bold=True
                )
            
            # Reset any narrative history
            if (hasattr(self.app, 'model_controller') and 
                self.app.model_controller is not None and
                hasattr(self.app.model_controller, 'battle_narrator') and
                self.app.model_controller.battle_narrator is not None):
                
                self.app.model_controller.battle_narrator.battle_history = []
                self.app.model_controller.battle_narrator.story_generated = False
                self.app.model_controller.battle_narrator.player_faction = ""
                self.app.model_controller.battle_narrator.computer_faction = ""
                
                # Log successful battle narrator reset
                print("Successfully reset battle narrator history")
            else:
                print("Battle narrator not yet available - will be initialized later")
            
            # Now generate the new narrative with opening context
            QTimer.singleShot(500, lambda: self.generate_narrative(game_phase="opening"))
            
        # Schedule a forced update to ensure visuals are correct
        QTimer.singleShot(50, self.force_update_all_cells)
            
    def on_model_loaded(self, success):
        """Handler for when the AI model is loaded"""
        self.model_loaded = success
        
        if hasattr(self.app, 'narrative_display'):
            if success:
                self.app.narrative_display.set_message(
                    "AI model loaded. Your turn to make a move!",
                    color="#2ecc71",
                    bold=True
                )
            else:
                self.app.narrative_display.set_message(
                    "Using simplified AI model. Your turn to make a move!",
                    color="#f39c12",
                    bold=True
                )
    
    def generate_narrative(self, column=None, game_phase=None):
        """Generate narrative for the current game state"""
        # Add more diagnostic information
        print(f"Generate narrative called with column={column}, game_phase={game_phase}")
        
        try:
            # Get current theme from theme controller 
            current_theme = "fantasy"  # Default
            if hasattr(self.app, 'theme_controller'):
                current_theme = self.app.theme_controller.get_theme_name()
            print(f"Current theme: {current_theme}")
            
            # Use our refactored model controller to generate narratives
            
            # If we have a game controller with a game state
            if hasattr(self.app, 'game_controller') and hasattr(self.app.game_controller, 'game'):
                # Store the last move column for reference
                if column is not None:
                    self.app.game_controller.last_move_column = column
                
                # Get game phase if not specified
                if game_phase is None:
                    # Calculate phase based on move count
                    board = self.app.game_controller.get_board()
                    filled_cells = sum(1 for row in board for cell in row if cell != 0)
                    if filled_cells == 0:
                        game_phase = "opening"
                    elif filled_cells < 12:
                        game_phase = "midgame"
                    else:
                        game_phase = "endgame"
                    
                    print(f"Determined game phase: {game_phase}")
                    
                # Prepare the game state dictionary
                game_state = {
                    "board": self.app.game_controller.get_board(),
                    "current_player": "player" if self.app.game_controller.game.current_player == 1 else "computer",
                    "last_move_column": column,
                    "game_phase": game_phase,
                    "move_count": filled_cells,
                    "game_over": self.app.game_controller.is_game_over()
                }
                
                # Generate narrative using our refactored model controller
                try:
                    # Set the theme first
                    if hasattr(self.app.model_controller, 'set_theme'):
                        self.app.model_controller.set_theme(current_theme)
                    
                    # Extract current player for the narrative generation
                    current_player = game_state["current_player"]
                    
                    # Generate the narrative
                    narrative = self.app.model_controller.generate_narrative(game_state)
                    
                    # Display the narrative
                    if hasattr(self.app, 'narrative_display'):
                        if game_phase == "opening":
                            # For the opening, clear everything first
                            self.app.narrative_display.clear_narrative()
                            color = "#3498db"  # Blue for story opening
                            bold = True
                        else:
                            color = None  # Default
                            bold = False
                            
                        self.app.narrative_display.set_message(narrative, color=color, bold=bold)
                    
                    # Store the narrative for context
                    self.app.game_controller.last_narrative = narrative
                    
                    return narrative
                    
                except Exception as e:
                    print(f"Error generating narrative: {e}")
                    # Fall back to a default message on error
                    if hasattr(self.app, 'narrative_display'):
                        self.app.narrative_display.set_message(
                            f"Error generating narrative: {e}",
                            color="#e74c3c"  # Red for error
                        )
                    return "The strategic contest continues as players analyze the board."
                
            else:
                # No game controller available
                print("No game controller available for narrative generation")
                return "The game is initializing..."
            
        except Exception as e:
            print(f"Error in generate_narrative: {e}")
            import traceback
            traceback.print_exc()
            return "The battle continues while the strategic systems initialize..."
        
    def force_update_all_cells(self):
        """Force update all cells to ensure visuals match the state"""
        print("Forcing update of all cells to ensure visuals match state")
            
        # Get current board state
        board = self.app.game_controller.get_board()
        
        # First pass: clear all cells completely
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app.game_container.findChild(QLabel, cell_key)
                if cell:
                    # Complete cell reset
                    cell.clear()
                    cell.setStyleSheet("")  # Clear any existing styling
                    cell.repaint()  # Force immediate update
        
        # Second pass: apply correct styling to all cells
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app.game_container.findChild(QLabel, cell_key)
                if cell:
                    try:
                        player = board[row][col]
                        # Apply proper styling with force
                        if player == 0:
                            # Empty cell style
                            cell.setStyleSheet("""
                                background-color: #34495e;
                                border-radius: 30px;
                                border: 2px solid #2c3e50;
                            """)
                        else:
                            # Player piece style - always use direct styling
                            color = self.player_colors[player]
                            border_color = "#c0392b" if player == 1 else "#f39c12"
                            cell.setStyleSheet(f"""
                                background-color: {color};
                                border-radius: 30px;
                                border: 3px solid {border_color};
                            """)
                        
                        # Force immediate repaint
                        cell.update()
                        cell.repaint()
                        
                        # Report if a cell contains a piece
                        if player != 0:
                            print(f"Force updated cell {row},{col} with player "
                                  f"{player}")
                    except (IndexError, TypeError) as e:
                        print(f"Error in force update for cell {row},{col}: {e}")
        
    def _update_cell(self, cell, player):
        """
        Update a cell with the appropriate player piece
        
        Args:
            cell: The QLabel cell to update
            player: The player value (0, 1, or 2)
        """
        # Convert numpy integers to Python integers
        if isinstance(player, np.integer):
            player = int(player)
            
        if player == 0:
            # Clear the cell
            cell.clear()
            cell.setStyleSheet("""
                background-color: #34495e;
                border-radius: 30px;
                border: 2px solid #2c3e50;
            """)
        else:
            # ALWAYS use direct color styling - most reliable approach
            # This guarantees visual representation regardless of pixmap status
            color = self.player_colors[player]
            border_color = "#c0392b" if player == 1 else "#f39c12"
            
            cell.clear()
            cell.setStyleSheet(f"""
                background-color: {color};
                border-radius: 30px;
                border: 3px solid {border_color};
            """)
            
            # Force immediate repaint
            cell.update()
            cell.repaint()
        
    def _handle_game_over(self):
        """Handle game over logic"""
        try:
            # Get the winner from the game controller 
            winner = self.app.game_controller.game.winner if hasattr(self.app.game_controller.game, 'winner') else None
            
            # Log the game over event
            logging.info(f"Game over! Winner: {winner}")
            
            # Generate a narrative for the game end
            self._generate_narrative(None, "endgame")
            
            # Update UI elements for game over
            if hasattr(self.app, 'status_bar') and self.app.status_bar:
                self.app.status_bar.set_message(f"Game Over! {'Player 1 Wins!' if winner == Player.ONE else 'Player 2 Wins!'}")
            
            # Additional game over logic can be added here
        except AttributeError as e:
            logging.error(f"Error handling game over: {e}")
        except Exception as e:
            logging.error(f"Unexpected error handling game over: {e}")
    
    def _load_player_piece(self, color):
        """
        Load player piece image or create a colored circle
        
        Args:
            color: The color name for the piece
            
        Returns:
            QPixmap: The player piece image or None if not found
        """
        # Try to load image from assets
        image_path = f"assets/images/{color}_piece.png"
        print(f"Attempting to load player piece image: {image_path}")
        
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull() and pixmap.width() > 0:
            # Scale to cell size
            print(f"Successfully loaded player piece image: {image_path}")
            return pixmap.scaled(56, 56)
        else:
            # Debug message about image not being found
            print(f"Could not load player piece image: {image_path}. "
                  f"Using color fallback.")
            
        # Return None if image couldn't be loaded
        # UI will fall back to colored cells
        return None 