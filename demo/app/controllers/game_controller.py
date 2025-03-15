"""
Game Controller - Manages game state and logic
"""
import copy
import numpy as np
from game.connect_four import ConnectFourGame, Player
from game.minimax import MinimaxEngine, DepthLimitedMinimax
from app.controllers.temperature_controller import TemperatureController

class GameController:
    """Controls game state and game logic"""
    
    def __init__(self):
        """Initialize the game controller"""
        self.game = ConnectFourGame()
        # Create two AI engines - regular and thermal-optimized
        # Default to medium difficulty (level 4-7)
        self.ai = MinimaxEngine(depth=3)
        # Simplified AI for hot systems (slightly easier than regular AI)
        self.thermal_ai = DepthLimitedMinimax(max_depth=2)
        self.temp_controller = TemperatureController()
        self.game_over = False
        self.winner = Player.EMPTY
        self.last_move_column = None
        self.last_narrative = None
    
    def new_game(self):
        """Start a new game"""
        # Create a completely new game instance
        self.game = ConnectFourGame()
        
        # Reset game state flags
        self.game_over = False
        self.winner = Player.EMPTY
        self.last_move_column = None
        self.last_narrative = None
        
        # Print debug info to verify reset
        print("Game has been reset. Board state:")
        self.game.print_board()
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.game_over
    
    def get_winner(self):
        """Get the winner of the game"""
        return self.winner
    
    def get_board(self):
        """Get the current board state"""
        return self.game.board
    
    def get_game_status(self):
        """Get the current game status"""
        return {
            'is_over': self.game_over,
            'winner': self.winner,
            'current_player': self.game.current_player,
            'is_full': self.is_board_full(),
            'last_move_column': self.last_move_column
        }
    
    def make_player_move(self, column):
        """Make a move for the player"""
        if self.game_over:
            return False
            
        # Try to make the move
        success = self.game.make_move(column)
        
        if success:
            # Store the last move column
            self.last_move_column = column
            
            # Check for win or draw
            self._check_end_conditions()
            
        return success
    
    def make_ai_move(self):
        """Make a move for the AI with thermal awareness"""
        if self.game_over:
            return None
        
        # Get system temperature to select AI strategy
        is_hot = self.temp_controller.is_overheating()
        
        # Choose the appropriate AI based on temperature
        if is_hot:
            print("System running hot, using simplified AI")
            ai_engine = self.thermal_ai
        else:
            ai_engine = self.ai
        
        # Find best move using minimax - convert board if necessary
        board = self.game.board
        
        # Check if we need to transpose the board for the AI
        # ConnectFourGame uses [row][col] but MinimaxEngine expects [col][row]
        if isinstance(board, np.ndarray) and board.shape[0] == 6 and board.shape[1] == 7:
            # Convert numpy array to list of lists for compatibility
            board = board.T.tolist()  # Transpose and convert to list
            
        column = ai_engine.find_best_move(board, 2)  # AI is always player 2
        
        # Make the move in the game
        success = self.game.make_move(column)
        
        if success:
            # Store the last move column
            self.last_move_column = column
            
            # Check for win or draw
            self._check_end_conditions()
            
        return column
    
    def _check_end_conditions(self):
        """Check if the game has ended"""
        # Check for win
        winner = self.game.check_win()
        print(f"Checking win condition: winner = {winner}")
        if winner is not None:
            self.game_over = True
            self.winner = winner
            print(f"Game over! Winner: {winner}")
            return
        
        # Check for draw
        is_full = self.is_board_full()
        print(f"Checking board full: is_full = {is_full}")
        if is_full:
            self.game_over = True
            print("Game over! Draw!")
            return
    
    def is_board_full(self):
        """Check if the board is full (draw)"""
        try:
            # Try to use the game's is_draw method if available
            return self.game.is_draw()
        except AttributeError:
            # Fallback: Check if all columns are full by directly examining valid moves
            for col in range(self.game.cols):
                if self.game.is_valid_move(col):
                    return False
            return True
    
    def get_board_data(self):
        """Get the board data in a UI-friendly format"""
        board_data = [[0 for _ in range(7)] for _ in range(6)]
        
        # First determine the board format
        board_height = len(self.game.board) if isinstance(self.game.board, list) else 6
        board_width = len(self.game.board[0]) if (isinstance(self.game.board, list) and len(self.game.board) > 0) else 7
        
        is_col_major = board_height > board_width  # If cols are the outer dimension
        
        # Fill the UI board data
        for row in range(6):
            for col in range(7):
                try:
                    if is_col_major:
                        # Board is [col][row]
                        board_data[row][col] = self.game.board[col][row]
                    else:
                        # Board is [row][col]
                        board_data[row][col] = self.game.board[row][col]
                except (IndexError, TypeError):
                    # If we can't access this cell, leave it as 0
                    pass
        
        return board_data
    
    def set_last_narrative(self, narrative):
        """Store the last narrative for context"""
        self.last_narrative = narrative
        
    def get_last_narrative(self):
        """Get the last narrative description"""
        return self.last_narrative
        
    def _generate_narrative(self, column, theme="fantasy"):
        """Generate a narrative description of the AI's move"""
        player = self.game.current_player
        
        # Get the other player - properly handling the Player enum
        if player == Player.ONE:
            other_player = Player.TWO
        else:
            other_player = Player.ONE
        
        # Get player names based on theme
        if theme == "fantasy":
            player_name = "Crystal Lords" if player == Player.ONE else "Shadow Keepers"
        else:  # sci-fi
            player_name = "Quantum Collective" if player == Player.ONE else "Void Syndicate"
        
        # Generate appropriate narrative
        if theme == "fantasy":
            return f"The {player_name} place their crystal in column {column + 1}."
        else:
            return f"The {player_name} deploy in sector {column + 1}." 