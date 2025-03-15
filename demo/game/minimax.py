"""
Minimax AI Module for Connect Four

This module implements the minimax algorithm with alpha-beta pruning for the
Connect Four game. It provides an AI that can play optimally against a human
player or other AIs.
"""

import random
from .connect_four import Player


class MinimaxEngine:
    def __init__(self, depth=4):
        self.max_depth = depth
    
    def find_best_move(self, board, player):
        """Find best move using minimax with alpha-beta pruning"""
        best_score = float('-inf')
        best_move = 3  # Default to middle column
        
        # Try each column
        for col in range(7):
            # Skip full columns
            if col < len(board) and board[col][0] != 0:
                continue
                
            # Make a copy of the board and try this move
            board_copy = [col.copy() for col in board]
            if self._make_move(board_copy, col, player):
                score = self._minimax(board_copy, self.max_depth, False, float('-inf'), float('inf'), player)
                
                if score > best_score:
                    best_score = score
                    best_move = col
        
        return best_move
    
    def _make_move(self, board, column, player):
        """Make a move on the copied board"""
        if column < 0 or column >= len(board):
            return False
            
        for row in range(5, -1, -1):
            if row < len(board[column]) and board[column][row] == 0:
                board[column][row] = player
                return True
        return False
    
    def _minimax(self, board, depth, is_maximizing, alpha, beta, player):
        """Minimax algorithm with alpha-beta pruning"""
        # Fix opponent calculation to handle Player enums
        if player == 1:
            opponent = 2
        else:
            opponent = 1
        
        # Check for terminal conditions
        winner = self._check_win(board)
        if winner == player:
            return 1000 + depth  # Prefer winning sooner
        elif winner == opponent:
            return -1000 - depth  # Avoid losing, especially soon
        elif self._is_board_full(board) or depth == 0:
            return self._evaluate_board(board, player)
        
        if is_maximizing:
            # Maximizing player
            max_eval = float('-inf')
            for col in range(7):
                if col >= len(board) or board[col][0] != 0:  # Skip full columns
                    continue
                    
                # Make a copy of the board and try this move
                board_copy = [col.copy() for col in board]
                if self._make_move(board_copy, col, player):
                    # Recurse
                    eval = self._minimax(board_copy, depth - 1, False, alpha, beta, player)
                    max_eval = max(max_eval, eval)
                    
                    # Alpha-beta pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                    
            return max_eval
        else:
            # Minimizing player
            min_eval = float('inf')
            for col in range(7):
                if col >= len(board) or board[col][0] != 0:  # Skip full columns
                    continue
                    
                # Make a copy of the board and try this move
                board_copy = [col.copy() for col in board]
                if self._make_move(board_copy, col, opponent):
                    # Recurse
                    eval = self._minimax(board_copy, depth - 1, True, alpha, beta, player)
                    min_eval = min(min_eval, eval)
                    
                    # Alpha-beta pruning
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                    
            return min_eval
    
    def _check_win(self, board):
        """Check if the board has a winner"""
        # Safe board access
        def safe_get(col, row):
            if 0 <= col < len(board) and 0 <= row < len(board[col]):
                return board[col][row]
            return 0
        
        # Check horizontal
        for row in range(6):
            for col in range(4):
                if (safe_get(col, row) != 0 and
                    safe_get(col, row) == safe_get(col+1, row) == 
                    safe_get(col+2, row) == safe_get(col+3, row)):
                    return safe_get(col, row)
        
        # Check vertical
        for col in range(7):
            for row in range(3):
                if (safe_get(col, row) != 0 and
                    safe_get(col, row) == safe_get(col, row+1) == 
                    safe_get(col, row+2) == safe_get(col, row+3)):
                    return safe_get(col, row)
        
        # Check diagonal (down-right)
        for col in range(4):
            for row in range(3):
                if (safe_get(col, row) != 0 and
                    safe_get(col, row) == safe_get(col+1, row+1) == 
                    safe_get(col+2, row+2) == safe_get(col+3, row+3)):
                    return safe_get(col, row)
        
        # Check diagonal (up-right)
        for col in range(4):
            for row in range(3, 6):
                if (safe_get(col, row) != 0 and
                    safe_get(col, row) == safe_get(col+1, row-1) == 
                    safe_get(col+2, row-2) == safe_get(col+3, row-3)):
                    return safe_get(col, row)
        
        # No winner yet
        return 0
    
    def _is_board_full(self, board):
        """Check if the board is full"""
        return all(col < len(board) and board[col][0] != 0 for col in range(7))
    
    def _evaluate_board(self, board, player):
        """Evaluate board position for heuristic value"""
        opponent = 3 - player
        score = 0
        
        # Safe board access
        def safe_get(col, row):
            if 0 <= col < len(board) and 0 <= row < len(board[col]):
                return board[col][row]
            return 0
        
        # Evaluate center column control (strategic advantage)
        center_col = 3
        center_count = sum(1 for row in range(6) if safe_get(center_col, row) == player)
        score += center_count * 3
        
        # Check for potential connections in windows
        for col in range(7):
            for row in range(6):
                # Check windows in all directions
                directions = [
                    [(1, 0), (2, 0), (3, 0)],  # Horizontal
                    [(0, 1), (0, 2), (0, 3)],  # Vertical
                    [(1, 1), (2, 2), (3, 3)],  # Diagonal down-right
                    [(1, -1), (2, -2), (3, -3)]  # Diagonal up-right
                ]
                
                # Skip if current position is empty
                if safe_get(col, row) == 0:
                    continue
                
                for direction in directions:
                    window = [safe_get(col, row)]
                    valid_window = True
                    
                    for dx, dy in direction:
                        new_col, new_row = col + dx, row + dy
                        window.append(safe_get(new_col, new_row))
                    
                    # Count player and opponent pieces in window
                    player_count = window.count(player)
                    opponent_count = window.count(opponent)
                    empty_count = window.count(0)
                    
                    # Score the window
                    if player_count == 4:
                        score += 100
                    elif player_count == 3 and empty_count == 1:
                        score += 5
                    elif player_count == 2 and empty_count == 2:
                        score += 2
                    
                    if opponent_count == 3 and empty_count == 1:
                        score -= 4  # Block opponent's potential win
        
        return score


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

MinimaxAI = MinimaxEngine  # Alias for backwards compatibility 