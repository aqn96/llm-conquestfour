"""
Difficulty Levels for Connect Four AI

This module provides different difficulty levels for the Connect Four AI,
ranging from easy (beginner-friendly) to hard (challenging).
"""

from game.connect_four import Player
from game.minimax import MinimaxEngine


class EasyAI(MinimaxEngine):
    """
    Easy difficulty AI for beginners.
    
    This AI:
    1. Uses a very shallow search depth (1-2)
    2. Sometimes makes random moves instead of optimal ones
    3. Primarily focuses on its own winning opportunities, less on blocking
    """
    
    def __init__(self):
        """Initialize the easy AI with minimal search depth."""
        super().__init__(max_depth=2)
        self.random_move_probability = 0.3  # 30% chance of random move
    
    def _evaluate_window(self, window, player):
        """
        A simplified scoring function that doesn't prioritize blocking.
        
        Args:
            window (list): A sequence of 4 cell values
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the window
        """
        opponent = Player.ONE if player == Player.TWO else Player.TWO
        
        # Count pieces in the window
        player_count = window.count(player.value)
        empty_count = window.count(Player.EMPTY.value)
        
        # Score only focuses on the AI's opportunities, not blocking
        if player_count == 4:
            return 100  # Winning window
        elif player_count == 3 and empty_count == 1:
            return 5  # Three in a row with an open space
        elif player_count == 2 and empty_count == 2:
            return 2  # Two in a row with two open spaces
        
        # Minimal consideration for blocking (only blocks obvious wins)
        opponent_count = window.count(opponent.value)
        if opponent_count == 3 and empty_count == 1:
            # Block opponent's three in a row, but with lower priority
            return -10
        
        return 0
    
    def find_best_move(self, game):
        """
        Find a move for the easy AI, sometimes choosing randomly.
        
        Args:
            game (ConnectFourGame): The current game state
            
        Returns:
            int: The column index for the AI's move
        """
        import random
        
        valid_moves = game.get_valid_columns()
        if not valid_moves:
            return -1
        
        # Check if there's an immediate winning move (always take it)
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            if game_copy.check_win() == Player(3 - game.current_player.value):
                return col
        
        # Sometimes make a random move instead of the best one
        if random.random() < self.random_move_probability:
            return random.choice(valid_moves)
        
        # Otherwise use minimax but with reduced depth
        return super().find_best_move(game)


class MediumAI(MinimaxEngine):
    """
    Medium difficulty AI that provides a balanced challenge.
    
    This AI:
    1. Uses a moderate search depth (3)
    2. Balances between offensive and defensive play
    3. Makes occasional non-optimal moves
    """
    
    def __init__(self):
        """Initialize the medium AI with moderate search depth."""
        super().__init__(max_depth=3)
        self.suboptimal_move_probability = 0.15  # 15% chance of suboptimal move
    
    def _evaluate_window(self, window, player):
        """
        Balanced scoring function that considers both offense and defense.
        
        Args:
            window (list): A sequence of 4 cell values
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the window
        """
        opponent = Player.ONE if player == Player.TWO else Player.TWO
        
        # Count pieces in the window
        player_count = window.count(player.value)
        empty_count = window.count(Player.EMPTY.value)
        opponent_count = window.count(opponent.value)
        
        # Score the window based on its contents
        if player_count == 4:
            return 100  # Winning window
        elif player_count == 3 and empty_count == 1:
            return 5  # Three in a row with an open space
        elif player_count == 2 and empty_count == 2:
            return 2  # Two in a row with two open spaces
        elif opponent_count == 3 and empty_count == 1:
            # Block opponent's three in a row (medium priority)
            return -20
        
        return 0
    
    def find_best_move(self, game):
        """
        Find a move for the medium AI, occasionally choosing suboptimal moves.
        
        Args:
            game (ConnectFourGame): The current game state
            
        Returns:
            int: The column index for the AI's move
        """
        import random
        
        valid_moves = game.get_valid_columns()
        if not valid_moves:
            return -1
            
        # Always block an immediate threat or take a winning move
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            if game_copy.check_win() == Player(3 - game.current_player.value):
                return col
                
        # Check for blocking moves (opponent has 3 in a row)
        for col in valid_moves:
            game_copy = game.copy()
            
            # Simulate opponent's move in this column
            # We need to make two moves to see the effect
            game_copy.make_move(col)  # AI move
            if game_copy.is_game_over():
                continue
                
            # Get the opponent's perspective
            opponent_moves = game_copy.get_valid_columns()
            for opp_col in opponent_moves:
                game_copy2 = game_copy.copy()
                game_copy2.make_move(opp_col)  # Opponent move
                if game_copy2.check_win() == Player(game.current_player.value):
                    # If opponent can win after our move, this is a bad move
                    valid_moves = [m for m in valid_moves if m != col]
                    break
        
        # Sometimes choose a suboptimal move
        if (random.random() < self.suboptimal_move_probability and 
                len(valid_moves) > 1):
            # Get the top 2 moves
            move_scores = []
            for col in valid_moves:
                game_copy = game.copy()
                game_copy.make_move(col)
                score = self._minimax(
                    game_copy, self.max_depth - 1, False, 
                    float('-inf'), float('inf')
                )
                move_scores.append((col, score))
            
            # Sort by score (descending)
            move_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return the second-best move instead of the best
            if len(move_scores) >= 2:
                return move_scores[1][0]
        
        # Otherwise use standard minimax
        return super().find_best_move(game)


class HardAI(MinimaxEngine):
    """
    Hard difficulty AI that provides a significant challenge.
    
    This AI:
    1. Uses a deep search depth (5-6)
    2. Aggressively blocks player's winning opportunities
    3. Prioritizes creating multiple winning threats
    4. Makes optimal strategic moves
    """
    
    def __init__(self):
        """Initialize the hard AI with deep search depth."""
        super().__init__(max_depth=5)
    
    def _evaluate_window(self, window, player):
        """
        Advanced scoring function with strong offensive and defensive weight.
        
        Args:
            window (list): A sequence of 4 cell values
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the window
        """
        opponent = Player.ONE if player == Player.TWO else Player.TWO
        
        # Count pieces in the window
        player_count = window.count(player.value)
        empty_count = window.count(Player.EMPTY.value)
        opponent_count = window.count(opponent.value)
        
        # Score the window based on its contents
        if player_count == 4:
            return 100  # Winning window
        elif player_count == 3 and empty_count == 1:
            return 10  # Three in a row with an open space (higher priority)
        elif player_count == 2 and empty_count == 2:
            return 3  # Two in a row with two open spaces (higher priority)
        elif opponent_count == 3 and empty_count == 1:
            return -80  # Block opponent's three in a row (high priority)
        elif opponent_count == 2 and empty_count == 2:
            return -3  # Block opponent's potential two in a row
        
        return 0
    
    def _score_position(self, board, player):
        """
        Enhanced position scoring with additional strategic considerations.
        
        Args:
            board (numpy.ndarray): The game board
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the position
        """
        score = super()._score_position(board, player)
        
        # Add additional strategic scoring elements
        rows, cols = board.shape
        
        # Check for "trap" setups (two threats in different directions)
        for row in range(1, rows - 3):  # Skip top and bottom rows
            for col in range(1, cols - 3):  # Skip leftmost and rightmost columns
                # If an empty space enables two winning paths simultaneously
                if board[row][col] == Player.EMPTY.value:
                    threats = 0
                    
                    # Check if placing a piece here creates multiple threats
                    # Horizontal threats
                    window1 = board[row, max(0, col-3):min(cols, col+4)].tolist()
                    # Vertical threats
                    window2 = [
                        board[r][col] for r in range(
                            max(0, row-3), min(rows, row+4)
                        )
                    ]
                    # Diagonal threats (positive slope)
                    window3 = [
                        board[row+i][col+i] for i in range(-3, 4)
                        if 0 <= row+i < rows and 0 <= col+i < cols
                    ]
                    # Diagonal threats (negative slope)
                    window4 = [
                        board[row-i][col+i] for i in range(-3, 4)
                        if 0 <= row-i < rows and 0 <= col+i < cols
                    ]
                    
                    # Check for potential threats
                    for window in [window1, window2, window3, window4]:
                        if len(window) >= 4:
                            for i in range(len(window) - 3):
                                sub_window = window[i:i+4]
                                if (sub_window.count(player.value) == 2 and
                                    sub_window.count(Player.EMPTY.value) == 2):
                                    threats += 1
                    
                    # Reward positions that create multiple threats
                    if threats >= 2:
                        score += 10
        
        return score
    
    def find_best_move(self, game):
        """
        Find the optimal move with a strong emphasis on blocking.
        
        Args:
            game (ConnectFourGame): The current game state
            
        Returns:
            int: The column index for the AI's move
        """
        valid_moves = game.get_valid_columns()
        if not valid_moves:
            return -1
            
        # First priority: Check for immediate win
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            if game_copy.check_win() == Player(3 - game.current_player.value):
                return col
        
        # Second priority: Block opponent's immediate win
        opponent = Player.ONE if game.current_player == Player.TWO else Player.TWO
        for col in valid_moves:
            game_copy = game.copy()
            
            # Simulate as if opponent plays in this column
            game_copy.current_player = opponent  # Temporarily switch to opponent
            game_copy.make_move(col)  # Opponent's hypothetical move
            
            # Check if that would be a win for opponent
            if game_copy.check_win() == opponent:
                # If so, we need to block this column
                return col
            
            # Reset game copy
            game_copy = game.copy()
        
        # Use enhanced minimax for strategic play
        return super().find_best_move(game)


def get_ai_by_difficulty(difficulty):
    """
    Factory function to get an AI instance for the specified difficulty level.
    
    Args:
        difficulty (str): Difficulty level ('easy', 'medium', or 'hard')
        
    Returns:
        MinimaxEngine: An AI instance for the specified difficulty
    """
    difficulty = difficulty.lower()
    if difficulty == 'easy':
        return EasyAI()
    elif difficulty == 'medium':
        return MediumAI()
    elif difficulty == 'hard':
        return HardAI()
    else:
        # Default to medium if invalid difficulty specified
        return MediumAI()


def computer_move(game, difficulty="medium"):
    """
    Helper function to determine which column the computer will choose.
    
    This function is designed for easy integration with the UI portion
    of the project. It takes the current game state and a difficulty level,
    and returns the column where the computer wants to place its piece.
    
    Args:
        game (ConnectFourGame): The current game state
        difficulty (str): Difficulty level ('easy', 'medium', or 'hard')
            (default: 'medium')
            
    Returns:
        int: The column index (0-6) where the computer will drop its piece,
             or -1 if no valid moves are available
             
    Example:
        # In the UI code:
        from difficulty_levels import computer_move
        
        # When it's the computer's turn:
        chosen_column = computer_move(game_state, "hard")
        # Then use chosen_column to update the UI and the game state
    """
    # Check if the game is already over
    if game.is_game_over():
        return -1
        
    # Check if it's the computer's turn (should be Player.TWO)
    if game.current_player != Player.TWO:
        # If called when it's not the computer's turn, consider
        # making a copy and switching turns
        game_copy = game.copy()
        game_copy.current_player = Player.TWO
        game = game_copy
        
    # Get the appropriate AI based on difficulty
    ai = get_ai_by_difficulty(difficulty)
    
    # Use the AI to determine the best move
    return ai.find_best_move(game) 