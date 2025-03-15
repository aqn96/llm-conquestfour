"""
Test script to verify switching difficulty during gameplay
"""
from app.handlers.user_input_handler import UserInputHandler
from app.controllers.game_controller import GameController


# Mock app for testing
class MockApp:
    pass


def test_switch_difficulty_during_game():
    """Test switching difficulty during an active game"""
    print("Testing switching difficulty during gameplay...")
    
    # Create mock app and controllers
    app = MockApp()
    app.game_controller = GameController()
    handler = UserInputHandler(app)
    
    # Start with Medium difficulty (default)
    print(f"Starting with Medium difficulty - depth: {app.game_controller.ai.max_depth}")
    
    # Make some moves to simulate gameplay
    print("\nMaking player move...")
    app.game_controller.make_player_move(3)  # Player 1 moves in middle
    print(f"Board after player move:")
    app.game_controller.game.print_board()
    
    print("\nMaking AI move...")
    app.game_controller.make_ai_move()  # AI moves
    print(f"Board after AI move:")
    app.game_controller.game.print_board()
    
    # Now switch to Easy difficulty
    print("\nSwitching to Easy difficulty...")
    handler._apply_difficulty("Easy")
    print(f"AI depth after switch: {app.game_controller.ai.max_depth}")
    
    # Make another move
    print("\nMaking player move...")
    app.game_controller.make_player_move(4)  # Player 1 moves
    print(f"Board after player move:")
    app.game_controller.game.print_board()
    
    print("\nMaking AI move with Easy difficulty...")
    app.game_controller.make_ai_move()  # AI moves with new difficulty
    print(f"Board after Easy AI move:")
    app.game_controller.game.print_board()
    
    # Switch to Hard difficulty
    print("\nSwitching to Hard difficulty...")
    handler._apply_difficulty("Hard")
    print(f"AI depth after switch: {app.game_controller.ai.max_depth}")
    
    # Make another move
    print("\nMaking player move...")
    app.game_controller.make_player_move(2)  # Player 1 moves
    print(f"Board after player move:")
    app.game_controller.game.print_board()
    
    print("\nMaking AI move with Hard difficulty...")
    app.game_controller.make_ai_move()  # AI moves with new difficulty
    print(f"Board after Hard AI move:")
    app.game_controller.game.print_board()
    

if __name__ == "__main__":
    test_switch_difficulty_during_game() 