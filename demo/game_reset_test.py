#!/usr/bin/env python3
"""
Diagnostic test script to verify game state reset functionality
when returning from title screen to a new game.

This script patches relevant functions to add debugging and verification
and runs a simple scenario to test the reset functionality.
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from app.game_master import GameMasterApp
from test_patch import patch_handlers


class TestRunner(QObject):
    """Runs an automated test sequence to verify game reset functionality"""
    
    finished = pyqtSignal()
    
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.step = 0
        self.test_log = []
        
    def log(self, message):
        """Log a message with a timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] TEST: {message}"
        print(formatted_message)
        self.test_log.append(formatted_message)
        
    def start_test(self):
        """Start the test sequence"""
        self.log("Starting game reset test sequence...")
        
        # Patch the handlers with debug versions
        self.log("Patching handlers with debug versions...")
        patch_handlers(self.app_instance)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(1000)  # Run steps with 1-second intervals
        
    def next_step(self):
        """Execute the next test step"""
        if self.step == 0:
            self.log("Step 1: Starting initial game...")
            # Start a game with test settings
            self.app_instance.intro_controller.start_game.emit({
                'player_name': 'TestPlayer',
                'difficulty': 'Easy',
                'themes': ['fantasy']
            })
            
        elif self.step == 1:
            self.log("Step 2: Verifying initial game state...")
            # Check if game board is properly initialized
            self.verify_board_state("Initial game")
            
        elif self.step == 2:
            self.log("Step 3: Making a test move (column 3)...")
            # Make a move in column 3
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(3)
            else:
                self.log("ERROR: input_handler not found!")
                
        elif self.step == 3:
            self.log("Step 4: Verifying board state after move...")
            # Check if the move was correctly applied
            self.verify_board_state("After player move")
            
        elif self.step == 4:
            self.log("Step 5: Returning to title screen...")
            # Return to title screen
            self.app_instance.show_intro_screen()
            
        elif self.step == 5:
            self.log("Step 6: Verifying handler cleanup...")
            # Check if handlers are properly cleaned up or reset
            self.verify_handlers("After title screen return")
            
        elif self.step == 6:
            self.log("Step 7: Starting a new game...")
            # Start a new game with different settings
            self.app_instance.intro_controller.start_game.emit({
                'player_name': 'TestPlayer2',
                'difficulty': 'Medium',
                'themes': ['fantasy']
            })
            
        elif self.step == 7:
            self.log("Step 8: Verifying new game state...")
            # Check if the game board is properly initialized for the new game
            self.verify_board_state("New game after title screen")
            
        elif self.step == 8:
            self.log("Step 9: Testing button connections...")
            # Test if buttons are connected and working
            self.verify_button_connections()
            
        elif self.step == 9:
            self.log("Step 10: Making a test move in new game (column 2)...")
            # Make a move in column 2
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(2)
            else:
                self.log("ERROR: input_handler not found in new game!")
                
        elif self.step == 10:
            self.log("Step 11: Verifying board state after move in new game...")
            # Check if the move was correctly applied in the new game
            self.verify_board_state("After move in new game")
            
        elif self.step == 11:
            self.log("Step 12: Testing direct UI cell visibility...")
            # Check if cells are visible and have proper styles
            self.verify_cell_visibility()
            
        elif self.step == 12:
            self.log("Test sequence completed!")
            self.log("Writing test results to test_report.txt...")
            
            # Write test results to a file
            with open("test_report.txt", "w") as f:
                f.write("Game Reset Test Results\n")
                f.write("======================\n\n")
                for line in self.test_log:
                    f.write(f"{line}\n")
                    
            # End the test
            self.timer.stop()
            self.finished.emit()
            
        self.step += 1
        
    def verify_board_state(self, context):
        """Verify the current board state"""
        self.log(f"Verifying board state: {context}")
        
        # Check if game controller exists
        if not hasattr(self.app_instance, 'game_controller'):
            self.log("ERROR: game_controller not found!")
            return
            
        # Get and log the current board state
        board = self.app_instance.game_controller.get_board()
        self.log(f"Board state: {board}")
        
        # Check if state handler exists
        if not hasattr(self.app_instance, 'state_handler'):
            self.log("ERROR: state_handler not found!")
            return
            
        # Check if the board is visually represented
        # by looking for player pieces in the UI
        has_pieces = False
        piece_count = 0
        
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                if cell and not cell.pixmap() is None:
                    has_pieces = True
                    piece_count += 1
                    
        self.log(f"Visual board has {piece_count} pieces visible: {has_pieces}")
        
    def verify_handlers(self, context):
        """Verify the state of game handlers"""
        self.log(f"Verifying handlers: {context}")
        
        # Check input handler
        has_input_handler = hasattr(self.app_instance, 'input_handler') and self.app_instance.input_handler is not None
        self.log(f"Input handler exists: {has_input_handler}")
        
        # Check state handler
        has_state_handler = hasattr(self.app_instance, 'state_handler') and self.app_instance.state_handler is not None
        self.log(f"State handler exists: {has_state_handler}")
        
        # Check current widget in stacked widget
        current_widget_name = type(self.app_instance.stacked_widget.currentWidget()).__name__
        self.log(f"Current widget: {current_widget_name}")
        
    def verify_button_connections(self):
        """Verify if column buttons are connected and responsive"""
        self.log("Testing button connections...")
        
        # Check if column buttons exist and are connected
        for col in range(7):
            button_name = f"colButton_{col}"
            button = self.app_instance.game_container.findChild(QPushButton, button_name)
            
            if button:
                self.log(f"Button for column {col} exists: {button.isEnabled()}")
                
                # Check if the button is connected to an action
                connections = hasattr(button, 'receivers') and button.receivers(button.clicked) > 0
                self.log(f"Button for column {col} has connections: {connections}")
                
                # Check what property values are stored on the button
                column_prop = button.property("column")
                self.log(f"Button for column {col} has property 'column': {column_prop}")
            else:
                self.log(f"ERROR: Button for column {col} not found!")
                
    def verify_cell_visibility(self):
        """Verify if cells are properly styled and visible"""
        self.log("Testing cell visibility...")
        
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                
                if cell:
                    style = cell.styleSheet()
                    size = f"{cell.width()}x{cell.height()}"
                    has_pixmap = cell.pixmap() is not None
                    self.log(f"Cell {row},{col}: size={size}, has_style={bool(style)}, has_pixmap={has_pixmap}")
                else:
                    self.log(f"ERROR: Cell {row},{col} not found!")


def run_test():
    """Main function to run the test"""
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = GameMasterApp()
    main_window.show()
    
    # Create and start the test runner
    test_runner = TestRunner(main_window)
    test_runner.finished.connect(app.quit)
    
    # Start the test sequence after a short delay
    QTimer.singleShot(1000, test_runner.start_test)
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    run_test() 