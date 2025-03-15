"""
ConnectFour Game Logic Module

This module contains the core Connect Four game logic. It provides a clean,
modular implementation that can be used by various frontends and is designed
to work with AI components.
"""

import numpy as np
from enum import Enum


class Player(Enum):
    """
    Enum representing the players in the game.
    
    EMPTY: No player (empty cell)
    ONE: Player 1 (typically human)
    TWO: Player 2 (typically AI)
    """
    EMPTY = 0
    ONE = 1
    TWO = 2


class ConnectFourGame:
    """
    Represents a Connect Four game with all the core game logic.
    
    The board is represented as a 2D array, where:
    - 0 represents an empty cell
    - 1 represents a player 1 piece
    - 2 represents a player 2 piece
    
    The board is indexed as board[row][col], where (0,0) is the top-left.
    """
    
    def __init__(self, rows=6, cols=7):
        """
        Initialize a new Connect Four game.
        
        Args:
            rows (int): Number of rows in the board (default: 6)
            cols (int): Number of columns in the board (default: 7)
        """
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        self.current_player = Player.ONE
        self.last_move = None
        self.move_count = 0
    
    def get_valid_columns(self):
        """
        Get a list of columns where a piece can be dropped.
        
        Returns:
            list: Indices of columns that are not full
        """
        return [col for col in range(self.cols) if self.is_valid_move(col)]
    
    def is_valid_move(self, col):
        """
        Check if a move is valid (column exists and is not full).
        
        Args:
            col (int): Column index to check
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        return 0 <= col < self.cols and self.board[0][col] == Player.EMPTY.value
    
    def get_next_open_row(self, col):
        """
        Find the lowest open row in the given column.
        
        Args:
            col (int): Column index to check
            
        Returns:
            int: Row index for the next piece, or -1 if the column is full
        """
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == Player.EMPTY.value:
                return row
        return -1
    
    def make_move(self, col):
        """
        Make a move by dropping a piece in the specified column.
        
        Args:
            col (int): Column index where the current player's piece will be dropped
            
        Returns:
            bool: True if the move was successful, False otherwise
        """
        if not self.is_valid_move(col):
            return False
        
        # Find the lowest empty row in the specified column
        row = self.get_next_open_row(col)
        if row == -1:  # This should never happen if is_valid_move is True
            return False
        
        # Place the piece and update game state
        self.board[row][col] = self.current_player.value
        self.last_move = (row, col)
        self.move_count += 1
        
        # Switch to the other player
        self.current_player = Player.TWO if self.current_player == Player.ONE else Player.ONE
        
        return True
    
    def check_win(self):
        """
        Check if the game has been won.
        
        Returns:
            Player: The winning player (Player.ONE or Player.TWO), or None if no winner yet
        """
        # Check horizontal locations
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if (self.board[row][col] != Player.EMPTY.value and
                        self.board[row][col] == self.board[row][col + 1] ==
                        self.board[row][col + 2] == self.board[row][col + 3]):
                    return Player(self.board[row][col])
        
        # Check vertical locations
        for col in range(self.cols):
            for row in range(self.rows - 3):
                if (self.board[row][col] != Player.EMPTY.value and
                        self.board[row][col] == self.board[row + 1][col] ==
                        self.board[row + 2][col] == self.board[row + 3][col]):
                    return Player(self.board[row][col])
        
        # Check positively sloped diagonals (/)
        for row in range(self.rows - 3):
            for col in range(self.cols - 3):
                if (self.board[row][col] != Player.EMPTY.value and
                        self.board[row][col] == self.board[row + 1][col + 1] ==
                        self.board[row + 2][col + 2] == self.board[row + 3][col + 3]):
                    return Player(self.board[row][col])
        
        # Check negatively sloped diagonals (\)
        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                if (self.board[row][col] != Player.EMPTY.value and
                        self.board[row][col] == self.board[row - 1][col + 1] ==
                        self.board[row - 2][col + 2] == self.board[row - 3][col + 3]):
                    return Player(self.board[row][col])
        
        return None
    
    def is_draw(self):
        """
        Check if the game is a draw (board is full with no winner).
        
        Returns:
            bool: True if the game is a draw, False otherwise
        """
        return self.move_count == self.rows * self.cols
    
    def is_game_over(self):
        """
        Check if the game is over (either a win or a draw).
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        return self.check_win() is not None or self.is_draw()
    
    def get_winner(self):
        """
        Get the winner of the game.
        
        Returns:
            Player: The winning player, or None if the game is not over or is a draw
        """
        return self.check_win()
    
    def copy(self):
        """
        Create a deep copy of the current game state.
        This is useful for AI algorithms that need to simulate moves.
        
        Returns:
            ConnectFourGame: A copy of the current game
        """
        game_copy = ConnectFourGame(self.rows, self.cols)
        game_copy.board = self.board.copy()
        game_copy.current_player = self.current_player
        game_copy.last_move = self.last_move
        game_copy.move_count = self.move_count
        return game_copy
    
    def reset(self):
        """
        Reset the game to its initial state.
        """
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.current_player = Player.ONE
        self.last_move = None
        self.move_count = 0
    
    def print_board(self):
        """
        Print a text representation of the board (for debugging).
        """
        for row in range(self.rows):
            row_str = []
            for col in range(self.cols):
                cell = self.board[row][col]
                if cell == Player.EMPTY.value:
                    row_str.append('.')
                elif cell == Player.ONE.value:
                    row_str.append('X')
                else:
                    row_str.append('O')
            print(' '.join(row_str))
        print(' '.join([str(i) for i in range(self.cols)])) 