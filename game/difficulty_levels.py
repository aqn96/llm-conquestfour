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
    1. Uses a shallow search depth (2)
    2. Sometimes makes random moves instead of optimal ones
    3. Has improved blocking but still focuses more on its own opportunities
    """
    
    def __init__(self):
        """Initialize the easy AI with minimal search depth."""
        super().__init__(max_depth=2)
        self.random_move_probability = 0.2  # Reduced from 0.3 to make it slightly harder
    
    def _evaluate_window(self, window, player):
        """
        A simplified scoring function with improved blocking.
        
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
        
        # Score primarily focuses on the AI's opportunities
        if player_count == 4:
            return 100  # Winning window
        elif player_count == 3 and empty_count == 1:
            return 7  # Increased from 5 - Three in a row with an open space
        elif player_count == 2 and empty_count == 2:
            return 3  # Increased from 2 - Two in a row with two open spaces
        
        # Improved blocking (but still less than medium difficulty)
        opponent_count = window.count(opponent.value)
        if opponent_count == 3 and empty_count == 1:
            # Block opponent's three in a row, increased priority from -10 to -15
            return -15
        elif opponent_count == 2 and empty_count == 2:
            # Added blocking for opponent's potential two in a row
            return -1
        
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
        
        # Now also check for blocking opponent's immediate win (added for slight improvement)
        opponent = Player.ONE if game.current_player == Player.TWO else Player.TWO
        for col in valid_moves:
            game_copy = game.copy()
            
            # Simulate as if opponent plays in this column
            game_copy.current_player = opponent  
            game_copy.make_move(col)  
            
            # Check if that would be a win for opponent
            if game_copy.check_win() == opponent:
                # 80% chance to block (still makes mistakes sometimes)
                if random.random() < 0.8:
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
    1. Uses a moderate search depth (4, increased from 3)
    2. Balances between offensive and defensive play
    3. Makes occasional non-optimal moves (but less often)
    4. Improves trap detection and center control
    """
    
    def __init__(self):
        """Initialize the medium AI with moderate search depth."""
        super().__init__(max_depth=4)  # Increased from 3
        self.suboptimal_move_probability = 0.08  # Reduced from 0.15
    
    def _evaluate_window(self, window, player):
        """
        Enhanced scoring function for balanced offensive and defensive play.
        
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
            return 7  # Increased from 5 - Three in a row with an open space
        elif player_count == 2 and empty_count == 2:
            return 3  # Increased from 2 - Two in a row with two open spaces
        elif opponent_count == 3 and empty_count == 1:
            # Block opponent's three in a row (medium-high priority)
            return -30  # Increased from -20
        elif opponent_count == 2 and empty_count == 2:
            # Added blocking for opponent's potential two in a row
            return -2
        
        return 0
    
    def _score_position(self, board, player):
        """
        Improved position scoring with center column preference.
        
        Args:
            board (numpy.ndarray): The game board
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the position
        """
        score = super()._score_position(board, player)
        
        # Add center column preference (strategic advantage)
        rows, cols = board.shape
        center_col = cols // 2
        
        # Count pieces in center column
        center_count = 0
        for row in range(rows):
            if board[row][center_col] == player.value:
                center_count += 1
        
        # Bonus for controlling center
        score += center_count * 3
        
        return score
    
    def find_best_move(self, game):
        """
        Find a move for the medium AI, with improved strategy.
        
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
                
        # Block opponent's immediate win
        opponent = Player.ONE if game.current_player == Player.TWO else Player.TWO
        for col in valid_moves:
            game_copy = game.copy()
            
            # Simulate as if opponent plays in this column
            game_copy.current_player = opponent
            game_copy.make_move(col)
            
            # Check if that would be a win for opponent
            if game_copy.check_win() == opponent:
                return col
                
        # Check for creating a trap (two potential winning moves)
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            
            # Now check if this creates two threats
            if self._creates_trap(game_copy, col, Player(3 - game.current_player.value)):
                return col
                
        # Check for blocking moves (opponent's potential trap)
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
        
        # Sometimes choose a suboptimal move (but less frequently)
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
        
    def _creates_trap(self, game, column, player):
        """Check if this move creates a 'trap' (multiple winning threats)."""
        # Count potential winning moves after this move
        winning_paths = 0
        opponent = Player.ONE if player == Player.TWO else Player.TWO
        
        # For each column, check if playing there would create a win
        for col in game.get_valid_columns():
            game_copy = game.copy()
            
            # Try this move
            game_copy.current_player = player
            if game_copy.make_move(col):
                # See if it's a win
                if game_copy.check_win() == player:
                    winning_paths += 1
        
        # If we have 2+ winning paths, it's a trap
        return winning_paths >= 2


class HardAI(MinimaxEngine):
    """
    Hard difficulty AI that provides a significant challenge.
    
    This AI:
    1. Uses a deeper search depth (6, increased from 5)
    2. Aggressively blocks player's winning opportunities
    3. Prioritizes creating multiple winning threats
    4. Makes optimal strategic moves
    5. Has enhanced positional evaluation
    """
    
    def __init__(self):
        """Initialize the hard AI with deep search depth."""
        super().__init__(max_depth=6)  # Increased from 5
    
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
        
        # Score the window based on its contents with increased values
        if player_count == 4:
            return 100  # Winning window
        elif player_count == 3 and empty_count == 1:
            return 15  # Increased from 10 - Three in a row with an open space
        elif player_count == 2 and empty_count == 2:
            return 5   # Increased from 3 - Two in a row with two open spaces
        elif opponent_count == 3 and empty_count == 1:
            return -90  # Increased from -80 - Block opponent's three in a row
        elif opponent_count == 2 and empty_count == 2:
            return -5   # Increased from -3 - Block opponent's potential two in a row
        
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
        score = 0  # Start from scratch with our enhanced evaluation
        rows, cols = board.shape
        
        # Score center column (strategically valuable)
        center_col = cols // 2
        center_count = 0
        for row in range(rows):
            if board[row][center_col] == player.value:
                center_count += 1
        score += center_count * 5  # Increased from the default 3
        
        # Evaluate horizontal windows
        for row in range(rows):
            for col in range(cols - 3):
                window = board[row, col:col+4].tolist()
                score += self._evaluate_window(window, player)
        
        # Evaluate vertical windows
        for col in range(cols):
            for row in range(rows - 3):
                window = [board[row+i][col] for i in range(4)]
                score += self._evaluate_window(window, player)
        
        # Evaluate positively sloped diagonals
        for row in range(rows - 3):
            for col in range(cols - 3):
                window = [board[row+i][col+i] for i in range(4)]
                score += self._evaluate_window(window, player)
        
        # Evaluate negatively sloped diagonals
        for row in range(3, rows):
            for col in range(cols - 3):
                window = [board[row-i][col+i] for i in range(4)]
                score += self._evaluate_window(window, player)
        
        # Check for "trap" setups (two threats in different directions)
        for row in range(rows):
            for col in range(cols):
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
                        score += 20  # Increased from 10
        
        return score
    
    def find_best_move(self, game):
        """
        Find the optimal move with an enhanced strategy.
        
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
            game_copy.current_player = opponent
            game_copy.make_move(col)
            
            # Check if that would be a win for opponent
            if game_copy.check_win() == opponent:
                return col
        
        # Third priority: Look for a move that creates a "fork" (two winning threats)
        # This makes the AI much harder to beat
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            
            # Check if this creates a fork (two ways to win)
            winning_moves = []
            for next_col in game.get_valid_columns():
                next_game = game_copy.copy()
                next_game.current_player = Player(3 - game.current_player.value)
                if next_game.make_move(next_col):
                    if next_game.check_win() == Player(3 - game.current_player.value):
                        winning_moves.append(next_col)
            
            # If we found a fork (2+ winning moves), use it!
            if len(winning_moves) >= 2:
                return col
        
        # Fourth priority: Block opponent's potential fork
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            
            # Check if opponent could create a fork in their next move
            for opp_col in game_copy.get_valid_columns():
                fork_game = game_copy.copy()
                fork_game.current_player = opponent
                if fork_game.make_move(opp_col):
                    # Check for multiple winning paths for opponent
                    opponent_winning_moves = []
                    for test_col in fork_game.get_valid_columns():
                        test_game = fork_game.copy()
                        test_game.current_player = opponent
                        if test_game.make_move(test_col):
                            if test_game.check_win() == opponent:
                                opponent_winning_moves.append(test_col)
                    
                    # If opponent could make a fork, block them by playing in this column
                    if len(opponent_winning_moves) >= 2:
                        # We should play in opp_col to block this fork
                        # Check if it's valid for us
                        if opp_col in valid_moves:
                            return opp_col
            
        # Use enhanced minimax for strategic play
        move_scores = []
        for col in valid_moves:
            game_copy = game.copy()
            game_copy.make_move(col)
            score = self._minimax(game_copy, self.max_depth - 1, False, float('-inf'), float('inf'))
            move_scores.append((col, score))
        
        # Sort by score (descending)
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best move
        if move_scores:
            return move_scores[0][0]
        
        # Fallback to standard minimax
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