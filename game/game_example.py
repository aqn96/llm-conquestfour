"""
Connect Four Game Example

This script demonstrates how to use the Connect Four game logic and AI 
components. It runs a game where a human player plays against the AI.
"""

# Import approach that works whether the file is imported or run directly
import os
import sys

# Handle imports differently based on how the file is being executed
if __name__ == "__main__":
    # When running the file directly, use direct imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    from connect_four import Player, ConnectFourGame
    from state_validator import StateValidator
    from thermal_aware_ai import ThermalAwareAI
else:
    # When imported as a module, use relative imports
    from .connect_four import Player, ConnectFourGame
    from .state_validator import StateValidator
    from .thermal_aware_ai import ThermalAwareAI


def print_board(game):
    """
    Print the game board in a user-friendly format.
    
    Args:
        game (ConnectFourGame): The game to display
    """
    print("\n")
    for row in range(game.rows):
        row_str = "| "
        for col in range(game.cols):
            cell = game.board[row][col]
            if cell == Player.EMPTY.value:
                row_str += "· "
            elif cell == Player.ONE.value:
                row_str += "X "
            else:
                row_str += "O "
        row_str += "|"
        print(row_str)
    
    # Print column numbers
    footer = "  "
    for col in range(game.cols):
        footer += str(col) + " "
    print(footer)
    print("\n")


def get_player_move(game):
    """
    Get a move from the human player.
    
    Args:
        game (ConnectFourGame): The current game state
        
    Returns:
        int: The column where the player wants to place a piece
    """
    valid_columns = game.get_valid_columns()
    
    while True:
        try:
            col = int(input(f"Your move (columns 0-{game.cols-1}): "))
            if col in valid_columns:
                return col
            print(f"Column {col} is not valid. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    """
    Run a simple Connect Four game between a human player and an AI.
    """
    print("=== Connect Four Game ===")
    print("You are X, the AI is O.")
    print("Enter a column number (0-6) to place your piece.")
    
    # Initialize game components
    game = ConnectFourGame()
    
    # Create a validator (not actively used in the example, but would be
    # used in a full implementation to verify game states)
    _ = StateValidator()
    
    # Use the thermal-aware AI that adjusts based on system temperature
    ai = ThermalAwareAI()
    
    # Main game loop
    while not game.is_game_over():
        print_board(game)
        
        if game.current_player == Player.ONE:
            # Human player's turn
            print("Your turn (Player X)")
            col = get_player_move(game)
            game.make_move(col)
        else:
            # AI's turn
            print("AI is thinking...")
            
            # Get the AI's move using the thermal-aware strategy
            col = ai.find_best_move(game)
            
            # Display the current temperature if available
            temp = ai.get_current_temperature()
            if temp > 0:
                print(f"System temperature: {temp:.1f}°C")
            
            print(f"AI places piece in column {col}")
            game.make_move(col)
    
    # Game over - display final state and result
    print_board(game)
    
    winner = game.get_winner()
    if winner == Player.ONE:
        print("You win! Congratulations!")
    elif winner == Player.TWO:
        print("AI wins! Better luck next time.")
    else:
        print("It's a draw!")


if __name__ == "__main__":
    main() 