"""
Patches for the game to enhance debugging capabilities
"""
from PyQt6.QtWidgets import QPushButton, QLabel
import time
from app.handlers.user_input_handler import UserInputHandler as OriginalUserInputHandler
from app.handlers.game_state_handler import GameStateHandler as OriginalGameStateHandler


class DebugUserInputHandler(OriginalUserInputHandler):
    """Enhanced version of UserInputHandler with debug logging"""
    
    def __init__(self, app):
        """Initialize with extra debugging"""
        super().__init__(app)
        print(f"[DEBUG] DebugUserInputHandler initialized at {time.time()}")
        
    def on_column_selected(self, column):
        """Enhanced version with debug logging"""
        print(f"[DEBUG] Column {column} selected at {time.time()}")
        print(f"[DEBUG] Game over status: {self.app.game_controller.is_game_over()}")
        
        # Show board state before move
        print("[DEBUG] Board state before move:")
        self.app.game_controller.game.print_board()
        
        # Call the original method
        super().on_column_selected(column)
        
        # Show board state after move
        print("[DEBUG] Board state after move:")
        self.app.game_controller.game.print_board()
        
        # Debug button state
        self._debug_button_state()
        
    def _debug_button_state(self):
        """Debug the state of column buttons"""
        for col in range(7):
            button_name = f"colButton_{col}"
            button = self.app.game_container.findChild(QPushButton, button_name)
            if button:
                enabled = button.isEnabled()
                style = bool(button.styleSheet())
                print(f"[DEBUG] Button {col}: enabled={enabled}, has_style={style}")
            else:
                print(f"[DEBUG] Button {col} not found!")
                
    def new_game(self):
        """Enhanced version with debug logging"""
        print(f"[DEBUG] New game requested at {time.time()}")
        
        # Call the original method
        super().new_game()
        
        # Show board state after new game
        print("[DEBUG] Board state after new game:")
        self.app.game_controller.game.print_board()


class DebugGameStateHandler(OriginalGameStateHandler):
    """Enhanced version of GameStateHandler with debug logging"""
    
    def __init__(self, app):
        """Initialize with extra debugging"""
        print(f"[DEBUG] DebugGameStateHandler initialized at {time.time()}")
        super().__init__(app)
        
    def update_board(self):
        """Enhanced version with debug logging"""
        print(f"[DEBUG] update_board called at {time.time()}")
        
        # Call the original method
        super().update_board()
        
        # Debug cell state
        self._debug_cell_state()
        
    def _debug_cell_state(self):
        """Debug the state of all cells on the board"""
        print("[DEBUG] Cell states:")
        has_any_cell_content = False
        
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app.game_container.findChild(QLabel, cell_key)
                if cell:
                    has_pixmap = cell.pixmap() is not None
                    has_style = bool(cell.styleSheet())
                    if has_pixmap:
                        has_any_cell_content = True
                    print(f"[DEBUG] Cell {row},{col}: has_pixmap={has_pixmap}, has_style={has_style}")
                else:
                    print(f"[DEBUG] Cell {row},{col} not found!")
        
        print(f"[DEBUG] At least one cell has content: {has_any_cell_content}")


# Patch function to apply enhanced handlers
def patch_handlers(app):
    """
    Replace the original handlers with debug-enhanced versions
    
    Args:
        app: The GameMasterApp instance
    """
    print("[DEBUG] Patching handlers with debug versions")
    
    # Replace the handler classes
    app.input_handler = DebugUserInputHandler(app)
    app.state_handler = DebugGameStateHandler(app)
    
    print("[DEBUG] Handlers patched successfully") 