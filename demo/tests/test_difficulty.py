"""
Test script to verify AI difficulty settings
"""
from app.handlers.user_input_handler import UserInputHandler
from app.controllers.game_controller import GameController


# Mock app for testing
class MockApp:
    pass


def test_difficulty_settings():
    """Test that difficulty settings are properly applied"""
    print("Testing AI difficulty settings...")
    
    # Create mock app and controllers
    app = MockApp()
    app.game_controller = GameController()
    handler = UserInputHandler(app)
    
    # Check initial (Medium) depth
    print(f"Initial AI depth: {app.game_controller.ai.max_depth}")
    print(
        f"Initial thermal AI depth: {app.game_controller.thermal_ai.max_depth}"
    )
    
    # Test Easy difficulty
    print("\nSetting to Easy...")
    handler._apply_difficulty("Easy")
    print(f"Easy AI depth: {app.game_controller.ai.max_depth}")
    print(
        f"Easy thermal AI depth: {app.game_controller.thermal_ai.max_depth}"
    )
    
    # Test Medium difficulty
    print("\nSetting to Medium...")
    handler._apply_difficulty("Medium")
    print(f"Medium AI depth: {app.game_controller.ai.max_depth}")
    print(
        f"Medium thermal AI depth: {app.game_controller.thermal_ai.max_depth}"
    )
    
    # Test Hard difficulty
    print("\nSetting to Hard...")
    handler._apply_difficulty("Hard")
    print(f"Hard AI depth: {app.game_controller.ai.max_depth}")
    print(
        f"Hard thermal AI depth: {app.game_controller.thermal_ai.max_depth}"
    )
    

if __name__ == "__main__":
    test_difficulty_settings() 