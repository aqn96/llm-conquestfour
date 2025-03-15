from game.connect_four import ConnectFourGame
from game.minimax import MinimaxEngine


def test_ai_moves():
    """Test that the AI can make valid moves"""
    print("Testing AI move generation...")
    
    # Create a new game
    game = ConnectFourGame()
    
    # Make a player move first
    game.make_move(3)  # Player 1 moves in the middle
    
    # Print the board after player move
    print("Board after player move:")
    game.print_board()
    
    # Create AI engine with depth 3 (faster for testing)
    ai = MinimaxEngine(depth=3)
    
    # Get board in format expected by the AI
    board = game.board.T.tolist()  # Convert to column-major format
    
    # Get AI move
    ai_move = ai.find_best_move(board, 2)  # AI is player 2
    
    print(f"AI selected move: Column {ai_move}")
    
    # Verify the move is valid
    is_valid = game.is_valid_move(ai_move)
    print(f"Move is valid: {is_valid}")
    
    # Make the AI move
    if is_valid:
        game.make_move(ai_move)
        print("Board after AI move:")
        game.print_board()
        return True
    else:
        print("ERROR: AI suggested an invalid move!")
        return False


if __name__ == "__main__":
    success = test_ai_moves()
    print(f"\nTest {'passed' if success else 'failed'}") 