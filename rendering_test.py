#!/usr/bin/env python3
"""
Specialized test script for diagnosing and fixing rendering issues,
particularly focused on chip rendering after returning from the title screen.

This script implements temporary rendering modifications and validates
the visual state of the board.
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette
from app.game_master import GameMasterApp


class RenderingTest(QObject):
    """Test for rendering issues with connect four chips"""
    
    finished = pyqtSignal()
    
    def __init__(self, app_instance):
        super().__init__()
        self.app_instance = app_instance
        self.step = 0
        self.logs = []
        
    def log(self, message):
        """Log a message with a timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] RENDER TEST: {message}"
        print(log_entry)
        self.logs.append(log_entry)
        
    def start_test(self):
        """Start the rendering test"""
        self.log("Starting rendering test sequence")
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(1500)  # Longer intervals for visual verification
        
    def next_step(self):
        """Execute the next test step"""
        if self.step == 0:
            self.log("Step 1: Starting game")
            settings = {
                'player_name': 'RenderTest',
                'difficulty': 'Easy',
                'themes': ['fantasy']
            }
            self.app_instance.start_game(settings)
            
        elif self.step == 1:
            self.log("Step 2: Applying special rendering flags")
            if hasattr(self.app_instance, 'state_handler'):
                self.verify_renderer_support()
            else:
                self.log("ERROR: No state handler found!")
            
        elif self.step == 2:
            self.log("Step 3: Making multiple moves")
            # Make several moves
            if hasattr(self.app_instance, 'input_handler'):
                # Make some test moves
                self.app_instance.input_handler.on_column_selected(3)
                # Check cell visibility after first move
                self.check_piece_visibility("after first move")
            else:
                self.log("ERROR: No input handler found!")
                
        elif self.step == 3:
            # Make another move
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(2)
                # Allow time for AI to respond
            
        elif self.step == 4:
            # Make another move
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(4)
                # Allow time for AI to respond
                
        elif self.step == 5:
            self.log("Step 6: Checking board visibility")
            self.check_piece_visibility("before returning to title")
            
        elif self.step == 6:
            self.log("Step 7: Returning to title screen")
            self.app_instance.show_intro_screen()
            
        elif self.step == 7:
            self.log("Step 8: Starting new game after title screen")
            settings = {
                'player_name': 'RenderTest2',
                'difficulty': 'Medium',
                'themes': ['sci-fi']
            }
            self.app_instance.start_game(settings)
            # Check if the state_handler.returned_from_title flag is set
            if hasattr(self.app_instance, 'state_handler'):
                if hasattr(self.app_instance.state_handler, 'returned_from_title'):
                    self.log(f"Returned from title flag: {self.app_instance.state_handler.returned_from_title}")
                else:
                    self.log("ERROR: No returned_from_title flag in state handler")
            
        elif self.step == 8:
            self.log("Step 9: Making move in new game after returning from title")
            # Force additional update to ensure we're in a good state
            if hasattr(self.app_instance, 'state_handler'):
                self.apply_rendering_fix()
                if hasattr(self.app_instance, 'input_handler'):
                    self.app_instance.input_handler.on_column_selected(3)
                    self.check_piece_visibility("after move in new game")
                    
        elif self.step == 9:
            self.log("Step 10: Making more moves in new game")
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(4)
                # Force extra rendering update
                self.apply_rendering_fix()
                
        elif self.step == 10:
            self.log("Test completed! Writing results to render_test_log.txt")
            
            with open("render_test_log.txt", "w") as f:
                f.write("Rendering Test Results\n")
                f.write("=====================\n\n")
                for line in self.logs:
                    f.write(f"{line}\n")
                    
            self.timer.stop()
            self.finished.emit()
            
        self.step += 1
        
    def verify_renderer_support(self):
        """Verify renderer support exists and apply if needed"""
        # Check for force_update_all_cells method
        has_force_update = hasattr(self.app_instance.state_handler, 'force_update_all_cells')
        self.log(f"Renderer has force_update_all_cells method: {has_force_update}")
        
        # Apply our rendering fix
        self.apply_rendering_fix()
            
    def apply_rendering_fix(self):
        """Apply rendering fixes to ensure pieces are visible"""
        self.log("Applying additional rendering fixes")
        
        try:
            # Force a double update with delay to ensure rendering
            if hasattr(self.app_instance.state_handler, 'force_update_all_cells'):
                self.app_instance.state_handler.force_update_all_cells()
                # Schedule another update after a short delay
                QTimer.singleShot(100, self.app_instance.state_handler.force_update_all_cells)
            else:
                self.log("WARNING: force_update_all_cells method not found")
                # Apply a manual update instead
                self.manual_cell_update()
        except Exception as e:
            self.log(f"ERROR in apply_rendering_fix: {e}")
            
    def manual_cell_update(self):
        """Manual update of cells as a fallback"""
        self.log("Applying manual cell update as fallback")
        board = self.app_instance.game_controller.get_board()
        
        try:
            for row in range(6):
                for col in range(7):
                    cell_key = f"cell_{row}_{col}"
                    cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                    if cell and board[row][col] > 0:
                        # For non-empty cells, force visibility by toggling styles
                        player = board[row][col]
                        if player == 1:
                            # Force-style Player 1 cells
                            cell.setStyleSheet("""
                                background-color: #e74c3c;
                                border-radius: 30px;
                                border: 3px solid #c0392b;
                            """)
                        elif player == 2:
                            # Force-style Player 2 cells
                            cell.setStyleSheet("""
                                background-color: #f1c40f;
                                border-radius: 30px;
                                border: 3px solid #f39c12;
                            """)
                        cell.update()  # Force update
                        self.log(f"Manually styled cell {row},{col} for player {player}")
        except Exception as e:
            self.log(f"ERROR in manual_cell_update: {e}")
            
    def check_piece_visibility(self, context):
        """Check which cells are visible and have content"""
        self.log(f"Checking piece visibility: {context}")
        piece_count = 0
        board = self.app_instance.game_controller.get_board()
        
        # First, log the expected cell states from the board
        self.log("Expected board state:")
        expected_pieces = []
        for row in range(6):
            for col in range(7):
                if board[row][col] > 0:
                    player = int(board[row][col])
                    expected_pieces.append((row, col, player))
                    
        self.log(f"Expected {len(expected_pieces)} pieces: {expected_pieces}")
        
        # Now check what's actually visible
        visible_pieces = []
        for row in range(6):
            for col in range(7):
                cell_key = f"cell_{row}_{col}"
                cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                if cell:
                    has_color = "background-color" in cell.styleSheet()
                    has_pixmap = cell.pixmap() is not None
                    is_visible = has_color or has_pixmap
                    
                    # Determine if this is a player cell
                    is_player_cell = False
                    if has_color:
                        color = cell.styleSheet()
                        is_player_cell = "#e74c3c" in color or "#f1c40f" in color
                    
                    if is_player_cell or has_pixmap:
                        visible_pieces.append((row, col))
                        piece_count += 1
                        
        self.log(f"Visible pieces: {piece_count} at positions {visible_pieces}")
        
        # Check for mismatches
        missing = []
        for row, col, player in expected_pieces:
            if (row, col) not in visible_pieces:
                missing.append((row, col, player))
                
        if missing:
            self.log(f"WARNING: {len(missing)} pieces not visible: {missing}")
            # Force update the missing pieces
            for row, col, player in missing:
                cell_key = f"cell_{row}_{col}"
                cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                if cell:
                    if player == 1:
                        # Force-style Player 1 cells
                        cell.setStyleSheet("""
                            background-color: #e74c3c;
                            border-radius: 30px;
                            border: 3px solid #c0392b;
                        """)
                    elif player == 2:
                        # Force-style Player 2 cells
                        cell.setStyleSheet("""
                            background-color: #f1c40f;
                            border-radius: 30px;
                            border: 3px solid #f39c12;
                        """)
                    cell.update()  # Force update
                    cell.repaint()  # Force immediate repaint
                    self.log(f"Forced update of missing piece at {row},{col} for player {player}")


def run_test():
    """Run the rendering test"""
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = GameMasterApp()
    main_window.show()
    
    # Create and start the test runner
    test_runner = RenderingTest(main_window)
    test_runner.finished.connect(app.quit)
    
    # Start the test sequence after a short delay to allow UI to initialize
    QTimer.singleShot(1000, test_runner.start_test)
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    run_test() 