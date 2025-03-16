"""
Narrative Connect Four Example

This example demonstrates how to use the narrative engine with the Connect Four game
to create an immersive, storytelling experience with move quality evaluation.
"""

from connect_four import ConnectFourGame, Player
from difficulty_levels import computer_move
from narrative_engine import GameNarrator, get_llm_response

# For this example, we'll simulate LLM responses with predefined texts
def mock_llm_response(prompt):
    """
    Mock function to simulate LLM responses.
    
    In a real implementation, this would call your local LLM.
    """
    if "introduction" in prompt.lower():
        return (
            "The Crystal Kingdom and Shadow Empire face each other across the mystical Crystal Grid. "
            "Ancient energies pulse between them as they prepare their first crystals, "
            "each seeking to create a powerful alignment that will channel enough magical force "
            "to overwhelm their adversary. The air crackles with arcane tension as the battle begins."
        )
    elif "good" in prompt.lower():
        return (
            "The Crystal Kingdom's mages focus their collective will, directing a brilliant sapphire crystal "
            "into position. It lands with perfect precision, creating a resonance that amplifies their previous "
            "placements. The Shadow Empire's generals exchange concerned glances as they observe the tactical "
            "brilliance of this move. New possibilities of power have opened for the Kingdom, and the battlefield "
            "glows with their gathering strength."
        )
    elif "mediocre" in prompt.lower():
        return (
            "A crystal shard descends cautiously into the grid, guided by the Crystal Kingdom's tacticians. "
            "Its glow is steady but not particularly inspired, maintaining their current formation without "
            "significant advancement. The Shadow Empire observes this conservative move with mild interest, "
            "recognizing that while it poses no immediate threat, it maintains the Kingdom's options for "
            "future maneuvers."
        )
    elif "bad" in prompt.lower():
        return (
            "Hesitation marks the Crystal Kingdom's move as they place a crystal with apparent uncertainty. "
            "The moment it settles into position, the magical energies of the grid seem to dim around it, "
            "failing to connect with their existing formation. The Shadow Empire's dark mages smile, sensing "
            "the tactical error and already calculating how to exploit this misplacement in their next turn."
        )
    elif "victory" in prompt.lower():
        return (
            "Four crystals align in perfect harmony, channeling an overwhelming surge of magical energy! "
            "The Crystal Kingdom's formation pulses with blinding light as power courses through their aligned gems. "
            "The Shadow Empire's defenses crumble under this arcane onslaught, their dark crystals shattering "
            "as they're overwhelmed by the pure magical force. Victory belongs to the Kingdom, who have proven "
            "their superior command of the Crystal Grid's ancient powers!"
        )
    else:
        return (
            "The battle continues across the Crystal Grid, with both sides seeking the perfect alignment "
            "of four crystals that will channel enough power to defeat their enemy."
        )


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
    Run a narrative Connect Four game.
    """
    # Initialize game components
    game = ConnectFourGame()
    difficulty = "medium"  # Can be "easy", "medium", or "hard"
    
    # Create narrator for narrative generation
    theme = "fantasy"  # Can be "fantasy" or "scifi"
    narrator = GameNarrator(theme=theme)
    
    # Start the game with an introduction
    print("=== Narrative Connect Four ===")
    print("You are the Crystal Kingdom (X), the computer is the Shadow Empire (O).")
    
    # Generate and display the introduction narrative
    intro_prompt = narrator.generate_game_start_prompt()
    intro_narrative = mock_llm_response(intro_prompt)
    print("\n" + intro_narrative + "\n")
    
    # Main game loop
    while not game.is_game_over():
        print_board(game)
        
        if game.current_player == Player.ONE:
            # Human player's turn
            print("Your turn (Crystal Kingdom)")
            col = get_player_move(game)
            
            # Save game state before making the move for evaluation
            pre_move_game = game.copy()
            
            # Make the move
            game.make_move(col)
            
            # Generate narrative based on move quality
            prompt = narrator.generate_move_narrative(pre_move_game, col)
            narrative = mock_llm_response(prompt)
            print("\n" + narrative + "\n")
            
        else:
            # AI's turn
            print("Shadow Empire is planning their move...")
            
            # Get the AI's move using the computer_move function
            col = computer_move(game, difficulty)
            
            print(f"Shadow Empire places crystal in column {col}")
            game.make_move(col)
            
            # For AI moves, we could also generate narratives, but for simplicity
            # we'll just use a standard message in this example
            print("\nThe Shadow Empire deploys their crystal with calculated precision, "
                  "advancing their dark strategy across the battlefield.\n")
    
    # Game over - display final state and result
    print_board(game)
    
    winner = game.get_winner()
    if winner == Player.ONE:
        # Generate victory narrative for player
        prompt = narrator.generate_victory_prompt(winner)
        narrative = mock_llm_response(prompt)
        print("\n" + narrative + "\n")
        print("You win! The Crystal Kingdom triumphs!")
    elif winner == Player.TWO:
        # Generate victory narrative for AI
        prompt = narrator.generate_victory_prompt(winner)
        narrative = mock_llm_response(prompt)
        print("\n" + narrative + "\n")
        print("Shadow Empire wins! Darkness descends upon the realm!")
    else:
        # Generate draw narrative
        prompt = narrator.generate_draw_prompt()
        narrative = mock_llm_response(prompt)
        print("\n" + narrative + "\n")
        print("It's a draw! The forces are perfectly balanced.")


if __name__ == "__main__":
    main() 