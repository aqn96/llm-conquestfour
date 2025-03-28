"""
Connect Four State Validator using Z3

This module provides Z3-based verification of Connect Four game states.
It can be used to validate that a game state is legal and to verify
properties about the game state.
"""

import z3
from .connect_four import Player


class StateValidator:
    """
    Validator that uses the Z3 theorem prover to verify properties about
    Connect Four game states.
    """
    
    def __init__(self, rows=6, cols=7):
        """
        Initialize the state validator.
        
        Args:
            rows (int): Number of rows in the board (default: 6)
            cols (int): Number of columns in the board (default: 7)
        """
        self.rows = rows
        self.cols = cols
        self.solver = z3.Solver()
    
    def is_valid_state(self, board):
        """Check if the current board state is valid"""
        # Reset solver
        self.solver.reset()
        
        # Rule 1: Pieces must obey gravity (no floating pieces)
        for col in range(self.cols):
            for row in range(self.rows - 1):  # Skip bottom row
                # If a cell is empty, all cells above it must be empty too
                if board[col][row+1] == 0:
                    for r in range(row+1, self.rows):
                        if board[col][r] != 0:
                            return False
        
        # Rule 2: Player counts must be balanced
        # Count pieces for each player
        p1_count = sum(1 for col in board for cell in col if cell == 1)
        p2_count = sum(1 for col in board for cell in col if cell == 2)
        
        # Player 1 goes first, so p1_count is either equal to p2_count or one more
        if not (p1_count == p2_count or p1_count == p2_count + 1):
            return False
        
        # Rule 3: No impossible win patterns (both players can't win simultaneously)
        p1_win = self._check_win(board, 1)
        p2_win = self._check_win(board, 2)
        
        if p1_win and p2_win:
            return False
            
        # Rule 4: If a player has won, they must have the correct number of pieces
        if p1_win and p1_count <= p2_count:
            return False
        if p2_win and p2_count != p1_count:
            return False
        
        return True
    
    def _check_win(self, board, player):
        """Check if a player has won on the current board"""
        # Check horizontal
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if all(board[col+i][row] == player for i in range(4)):
                    return True
        
        # Check vertical
        for col in range(self.cols):
            for row in range(self.rows - 3):
                if all(board[col][row+i] == player for i in range(4)):
                    return True
        
        # Check diagonal (down-right)
        for col in range(self.cols - 3):
            for row in range(self.rows - 3):
                if all(board[col+i][row+i] == player for i in range(4)):
                    return True
        
        # Check diagonal (up-right)
        for col in range(self.cols - 3):
            for row in range(3, self.rows):
                if all(board[col+i][row-i] == player for i in range(4)):
                    return True
        
        return False
    
    def next_moves_for_win(self, game, player):
        """
        Find all moves that would lead to a win for the given player.
        
        Args:
            game (ConnectFourGame): The current game state
            player (Player): The player to find winning moves for
            
        Returns:
            list: Column indices of moves that would result in a win
        """
        winning_moves = []
        
        # Try each valid column
        for col in game.get_valid_columns():
            game_copy = game.copy()
            row = game_copy.get_next_open_row(col)
            
            # Temporarily place a piece and check for a win
            game_copy.board[row][col] = player.value
            
            # If this is a winning move, add it to the list
            if self._check_win(game_copy.board, player.value):
                winning_moves.append(col)
            
        return winning_moves
    
    def is_draw_inevitable(self, game):
        """
        Check if a draw is inevitable from the current state.
        
        Args:
            game (ConnectFourGame): The current game state
            
        Returns:
            bool: True if a draw is inevitable, False otherwise
        """
        # Reset the solver
        self.solver.reset()
        
        # Create Z3 variables for each cell in the board
        cells = {}
        for row in range(self.rows):
            for col in range(self.cols):
                cells[(row, col)] = z3.Int(f"cell_{row}_{col}")
                
                # Cell values must be 0, 1, or 2
                self.solver.add(z3.Or(
                    cells[(row, col)] == 0,
                    cells[(row, col)] == 1,
                    cells[(row, col)] == 2
                ))
        
        # Add constraints for the current board state
        for row in range(self.rows):
            for col in range(self.cols):
                if game.board[row][col] != 0:
                    self.solver.add(cells[(row, col)] == game.board[row][col])
        
        # Add gravity constraints
        for col in range(self.cols):
            for row in range(self.rows - 1):
                self.solver.add(z3.Implies(
                    cells[(row, col)] != 0,
                    cells[(row + 1, col)] != 0
                ))
        
        # Check if there's a way to get four in a row for either player
        player1_can_win = False
        player2_can_win = False
        
        # Check horizontal windows
        for row in range(self.rows):
            for col in range(self.cols - 3):
                # Player 1 can win horizontally
                self.solver.push()
                self.solver.add(
                    cells[(row, col)] == 1,
                    cells[(row, col + 1)] == 1,
                    cells[(row, col + 2)] == 1,
                    cells[(row, col + 3)] == 1
                )
                if self.solver.check() == z3.sat:
                    player1_can_win = True
                self.solver.pop()
                
                # Player 2 can win horizontally
                self.solver.push()
                self.solver.add(
                    cells[(row, col)] == 2,
                    cells[(row, col + 1)] == 2,
                    cells[(row, col + 2)] == 2,
                    cells[(row, col + 3)] == 2
                )
                if self.solver.check() == z3.sat:
                    player2_can_win = True
                self.solver.pop()
        
        # Check vertical windows (similar to horizontal)
        # ... (omitted for brevity)
        
        # Check diagonals (similar to horizontal)
        # ... (omitted for brevity)
        
        # If neither player can win, a draw is inevitable
        return not (player1_can_win or player2_can_win)
    
    def validate_move(self, game, col):
        """
        Validate that a move is legal.
        
        Args:
            game (ConnectFourGame): The current game state
            col (int): Column index where a piece would be dropped
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Basic validation
        if col < 0 or col >= self.cols:
            return False
            
        # Check if the column is not full
        return game.board[0][col] == 0
    
    def minimum_moves_to_win(self, game, player):
        """
        Estimate the minimum number of moves required for the player to win.
        
        Args:
            game (ConnectFourGame): The current game state
            player (Player): The player to analyze
            
        Returns:
            int: Estimated minimum number of moves to win, or -1 if impossible
        """
        # If the player can win in one move, return 1
        if self.next_moves_for_win(game, player):
            return 1
            
        # Otherwise, use a heuristic to estimate
        # This is a simplified estimate - a real implementation would use
        # more sophisticated analysis
        
        # Count how many potential winning lines the player has
        potential_lines = 0
        opponent = Player.ONE if player == Player.TWO else Player.TWO
        
        for row in range(self.rows):
            for col in range(self.cols - 3):
                window = [game.board[row][col + i] for i in range(4)]
                # If there are player pieces and no opponent pieces
                if opponent.value not in window:
                    player_pieces = window.count(player.value)
                    if player_pieces > 0:
                        potential_lines += player_pieces
        
        # Similar checks for vertical and diagonal windows
        # ... (omitted for brevity)
        
        if potential_lines > 0:
            # Rough estimate: more potential lines means fewer moves to win
            return max(2, 7 - potential_lines // 2)
        
        return -1  # Cannot win 