"""
Connect Four Game Example

This script demonstrates how to use the Connect Four game logic and AI 
components. It runs a game where a human player plays against the AI.
"""

# Import from the local package
from connect_four import Player
from connect_four import ConnectFourGame
from state_validator import StateValidator
from difficulty_levels import get_ai_by_difficulty


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


def get_difficulty_choice():
    """
    Ask the player to choose a difficulty level.
    
    Returns:
        str: The chosen difficulty ('easy', 'medium', or 'hard')
    """
    print("Choose a difficulty level:")
    print("1. Easy - Good for beginners")
    print("2. Medium - Balanced challenge")
    print("3. Hard - Significant challenge")
    
    while True:
        try:
            choice = int(input("Enter your choice (1-3): "))
            if choice == 1:
                return "easy"
            elif choice == 2:
                return "medium"
            elif choice == 3:
                return "hard"
            else:
                print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    """
    Run a simple Connect Four game between a human player and an AI.
    """
    print("=== Connect Four Game ===")
    print("You are X, the AI is O.")
    
    # Let the player choose a difficulty level
    difficulty = get_difficulty_choice()
    print(f"You selected {difficulty.capitalize()} difficulty.")
    print("Enter a column number (0-6) to place your piece.")
    
    # Initialize game components
    game = ConnectFourGame()
    
    # Create a validator (not actively used in the example, but would be
    # used in a full implementation to verify game states)
    _ = StateValidator()
    
    # Choose the AI based on selected difficulty
    ai = get_ai_by_difficulty(difficulty)
    
    # If the system supports thermal monitoring, wrap the AI with thermal awareness
    try:
        # Import here to avoid the unused import warning
        from thermal_aware_ai import ThermalAwareAI
        thermal_ai = ThermalAwareAI()
        # Check if thermal monitoring is available
        temp = thermal_ai.get_current_temperature()
        if temp > 0:
            print("Thermal monitoring is available.")
            print("The AI will adapt to system temperature.")
            ai = thermal_ai
    except (ImportError, AttributeError):
        # Either thermal_aware_ai module is not available or
        # there was an error accessing the thermal information
        pass
    
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
            
            # Get the AI's move
            col = ai.find_best_move(game)
            
            # Display the current temperature if available
            if hasattr(ai, 'get_current_temperature'):
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