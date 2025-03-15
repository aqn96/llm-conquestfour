"""
Minimax AI Module for Connect Four

This module implements the minimax algorithm with alpha-beta pruning for the
Connect Four game. It provides an AI that can play optimally against a human
player or other AIs.
"""

import random
from .connect_four import Player


class MinimaxEngine:
    """
    AI engine that uses the minimax algorithm with alpha-beta pruning.
    """
    
    def __init__(self, max_depth=4):
        """
        Initialize the minimax engine.
        
        Args:
            max_depth (int): Maximum depth for the minimax search (default: 4)
        """
        self.max_depth = max_depth
        # Center columns are often strategically better in Connect Four
        self.column_order = self._get_center_prioritized_columns(7)
    
    def _get_center_prioritized_columns(self, cols):
        """
        Create a list of column indices prioritizing the center columns.
        This is a heuristic that helps the AI focus on strategically better
        moves first, which improves alpha-beta pruning efficiency.
        
        Args:
            cols (int): Number of columns in the board
            
        Returns:
            list: Column indices ordered by strategic priority
        """
        # Start with the center column, then alternate left and right
        center = cols // 2
        result = [center]
        for i in range(1, cols // 2 + 1):
            if center - i >= 0:
                result.append(center - i)
            if center + i < cols:
                result.append(center + i)
        return result
    
    def find_best_move(self, game):
        """
        Find the best move for the current player using minimax with
        alpha-beta pruning.
        
        Args:
            game (ConnectFourGame): The current game state
            
        Returns:
            int: The column index of the best move, or -1 if no valid moves
        """
        valid_moves = game.get_valid_columns()
        if not valid_moves:
            return -1
        
        # Randomize the order of equally good moves
        random.shuffle(valid_moves)
        
        best_score = float('-inf')
        best_move = valid_moves[0]  # Default to first valid move
        
        # Try each valid move and find the one with the highest score
        for col in self.column_order:
            if col not in valid_moves:
                continue
                
            game_copy = game.copy()
            game_copy.make_move(col)
            
            # If AI made a winning move, return it immediately
            if game_copy.check_win() == Player(3 - game.current_player.value):
                return col
                
            # Evaluate this move with minimax
            score = self._minimax(
                game_copy, 
                self.max_depth - 1, 
                False, 
                float('-inf'), 
                float('inf')
            )
            
            if score > best_score:
                best_score = score
                best_move = col
        
        return best_move
    
    def _evaluate_window(self, window, player):
        """
        Score a window of 4 cells based on its contents.
        
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
            return -80  # Block opponent's three in a row
        
        return 0
    
    def _score_position(self, board, player):
        """
        Score the entire board position for the given player.
        
        Args:
            board (numpy.ndarray): The game board
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the position
        """
        score = 0
        rows, cols = board.shape
        
        # Score center column (strategically valuable)
        center_col = cols // 2
        center_count = 0
        for row in range(rows):
            if board[row][center_col] == player.value:
                center_count += 1
        score += center_count * 3
        
        # Score horizontal windows
        for row in range(rows):
            for col in range(cols - 3):
                window = board[row, col:col+4].tolist()
                score += self._evaluate_window(window, player)
        
        # Score vertical windows
        for col in range(cols):
            for row in range(rows - 3):
                window = [board[row+i][col] for i in range(4)]
                score += self._evaluate_window(window, player)
        
        # Score positively sloped diagonals
        for row in range(rows - 3):
            for col in range(cols - 3):
                window = [board[row+i][col+i] for i in range(4)]
                score += self._evaluate_window(window, player)
        
        # Score negatively sloped diagonals
        for row in range(3, rows):
            for col in range(cols - 3):
                window = [board[row-i][col+i] for i in range(4)]
                score += self._evaluate_window(window, player)
        
        return score
    
    def _minimax(self, game, depth, is_maximizing, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            game (ConnectFourGame): The game state to evaluate
            depth (int): Current depth in the search tree
            is_maximizing (bool): True if maximizing player's turn
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            
        Returns:
            float: Best score for the current position
        """
        # Terminal conditions: win, loss, draw, or max depth reached
        winner = game.check_win()
        if winner is not None:
            if winner.value == 3 - game.current_player.value:  # Opponent won
                return 1000000  # Large positive score for a win
            else:  # Current player won
                return -1000000  # Large negative score for a loss
        
        if game.is_draw():
            return 0
        
        if depth == 0:
            # Evaluate the board from maximizing player's perspective
            maximizing_player = Player.TWO if is_maximizing else Player.ONE
            return self._score_position(game.board, maximizing_player)
        
        valid_moves = game.get_valid_columns()
        
        if is_maximizing:
            max_score = float('-inf')
            for col in self.column_order:
                if col not in valid_moves:
                    continue
                    
                game_copy = game.copy()
                game_copy.make_move(col)
                
                score = self._minimax(game_copy, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                
                # Alpha-beta pruning
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
                    
            return max_score
        else:
            min_score = float('inf')
            for col in self.column_order:
                if col not in valid_moves:
                    continue
                    
                game_copy = game.copy()
                game_copy.make_move(col)
                
                score = self._minimax(game_copy, depth - 1, True, alpha, beta)
                min_score = min(min_score, score)
                
                # Alpha-beta pruning
                beta = min(beta, score)
                if beta <= alpha:
                    break
                    
            return min_score


class DepthLimitedMinimax(MinimaxEngine):
    """
    A simplified version of the minimax engine with a reduced search depth.
    Used for thermal management - when the system is running hot, we can use
    this simpler version to reduce computational load.
    """
    
    def __init__(self, max_depth=2):
        """
        Initialize with a smaller search depth to reduce computational demands.
        
        Args:
            max_depth (int): Maximum depth for the minimax search (default: 2)
        """
        super().__init__(max_depth)
        
    def _score_position(self, board, player):
        """
        A simplified scoring function for faster computation.
        
        Args:
            board (numpy.ndarray): The game board
            player (Player): The player to evaluate for
            
        Returns:
            int: A score for the position
        """
        # Simplified scoring that only checks for immediate threats and opportunities
        score = 0
        rows, cols = board.shape
        
        # Just check for three-in-a-row opportunities and threats
        for row in range(rows):
            for col in range(cols - 3):
                window = board[row, col:col+4].tolist()
                if window.count(player.value) == 3 and window.count(Player.EMPTY.value) == 1:
                    score += 5
                    
        for col in range(cols):
            for row in range(rows - 3):
                window = [board[row+i][col] for i in range(4)]
                if window.count(player.value) == 3 and window.count(Player.EMPTY.value) == 1:
                    score += 5
        
        return score 