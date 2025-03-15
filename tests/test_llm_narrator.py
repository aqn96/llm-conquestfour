"""
Test LLM Battle Narrator

This script tests the LLM battle narrator implementation by simulating
different game scenarios and generating narratives.
"""
import os
import logging
from game.connect_four import ConnectFourGame, Player
from ai.llm_battle_narrator import LLMBattleNarrator

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def test_llm_battle_narrator():
    """Test the LLM battle narrator with different themes and game states"""
    # Get API key from environment or use a dummy key for testing
    api_key = os.environ.get("LLM_API_KEY", "dummy_api_key")
    
    # Create battle narrator
    narrator = LLMBattleNarrator(api_key=api_key)
    
    # Create a game
    game = ConnectFourGame()
    
    # Test different themes
    themes = ["fantasy", "sci-fi", "western"]
    
    for theme in themes:
        print(f"\n\n===== Testing {theme.upper()} Theme =====\n")
        
        # Set theme
        narrator.set_theme(theme)
        
        # Reset game
        game.reset()
        
        # Make some moves to create an interesting board state
        moves = [3, 4, 3, 4, 3, 2]
        
        for i, col in enumerate(moves):
            player = Player.ONE if i % 2 == 0 else Player.TWO
            game.make_move(col, player.value)
            
            # Generate narrative after each move
            narrative = narrator.generate_narrative(game, col)
            
            # Print board and narrative
            print(f"\nMove {i+1}: Player {player.name} placed in column {col}")
            print(game)
            print(f"Narrative: {narrative}\n")
            print("-" * 50)
    
    # Test with a near-win scenario
    print("\n\n===== Testing NEAR WIN Scenario =====\n")
    game.reset()
    
    # Create a near win for Player ONE (horizontal)
    near_win_moves = [
        (0, Player.ONE), (0, Player.TWO), 
        (1, Player.ONE), (1, Player.TWO),
        (2, Player.ONE), (2, Player.TWO)
    ]
    
    for col, player in near_win_moves:
        game.make_move(col, player.value)
    
    # This move will create a threat
    game.make_move(3, Player.ONE.value)
    
    # Generate narrative for the threat
    narrative = narrator.generate_narrative(game, 3)
    
    # Print board and narrative
    print("\nNear win scenario for Player ONE (horizontal):")
    print(game)
    print(f"Narrative: {narrative}\n")
    print("-" * 50)
    
    # Test with a winning move
    print("\n\n===== Testing WIN Scenario =====\n")
    
    # Player ONE wins with a horizontal line
    game.make_move(4, Player.ONE.value)
    
    # Check if there's a winner
    winner = game.check_winner()
    
    # Generate narrative for the win
    narrative = narrator.generate_narrative(game, 4)
    
    # Print board and narrative
    print("\nWin scenario for Player ONE (horizontal):")
    print(game)
    print(f"Winner: {winner}")
    print(f"Narrative: {narrative}\n")


if __name__ == "__main__":
    test_llm_battle_narrator() 