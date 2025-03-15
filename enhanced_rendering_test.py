#!/usr/bin/env python3
"""
Enhanced interactive rendering test for diagnosing chip rendering issues.

This script provides a more interactive way to test and debug rendering issues,
particularly when returning from the title screen and starting a new game.
It includes additional diagnostic information, visual verification, and
interactive controls to help identify the cause of rendering problems.
"""
import sys
import time
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget,
                            QPushButton, QHBoxLayout, QTextEdit, QGridLayout)
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, Qt, QEvent
from PyQt6.QtGui import QColor, QPalette, QFont
from app.game_master import GameMasterApp


class EnhancedRenderingTest(QObject):
    """Enhanced test for rendering issues with connect four chips"""
    
    finished = pyqtSignal()
    
    def __init__(self, app_instance, debug_window):
        super().__init__()
        self.app_instance = app_instance
        self.debug_window = debug_window
        self.step = 0
        self.logs = []
        self.paused = False
        self.test_in_progress = False
        self.cell_states = {}  # Track cell states for verification
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"render_test_log_{timestamp}.txt"
        
    def log(self, message, level="INFO"):
        """Log a message with a timestamp and level"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.logs.append(log_entry)
        
        # Add to debug window
        if self.debug_window:
            self.debug_window.add_log(log_entry)
            
        # Also write to log file immediately
        with open(self.log_file, "a") as f:
            f.write(f"{log_entry}\n")
        
    def start_test(self):
        """Start the enhanced rendering test"""
        self.test_in_progress = True
        self.log("Starting enhanced rendering test sequence", "TEST")
        self.log(f"Logging to: {self.log_file}", "TEST")
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.timer.start(2000)  # Longer intervals for visual verification
        
    def pause_test(self):
        """Pause or resume the test"""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        self.log(f"Test {status}", "TEST")
        
    def stop_test(self):
        """Stop the test"""
        self.test_in_progress = False
        self.timer.stop()
        self.log("Test stopped by user", "TEST")
        self.write_report()
        
    def next_step(self):
        """Execute the next test step"""
        if self.paused:
            return
            
        if self.step == 0:
            self.log("Step 1: Checking game state", "TEST")
            self.debug_window.update_status("Checking game state and starting new game")
            
            # Check if we're at the intro screen or already in game
            if hasattr(self.app_instance, 'stacked_widget'):
                # Since we're testing the game, we just need to ensure we're in a game
                # We'll apply settings directly to input handler
                if hasattr(self.app_instance, 'input_handler'):
                    self.log("Applying test settings to input handler", "TEST")
                    self.app_instance.input_handler.current_difficulty = 'Easy'
                    self.app_instance.input_handler.current_theme = 'Fantasy'
                    self.app_instance.input_handler.new_game()
            
        elif self.step == 1:
            self.log("Step 2: Applying special rendering flags", "TEST")
            if hasattr(self.app_instance, 'state_handler'):
                self.verify_renderer_support()
                self.debug_window.update_status("Checking renderer support")
            else:
                self.log("ERROR: No state handler found!", "ERROR")
                self.debug_window.update_status("ERROR: Missing state handler")
            
        elif self.step == 2:
            self.log("Step 3: Making multiple moves", "TEST")
            self.debug_window.update_status("Making moves in first game")
            # Make several moves
            if hasattr(self.app_instance, 'input_handler'):
                # Make some test moves
                self.app_instance.input_handler.on_column_selected(3)
                # Check cell visibility after first move
                self.check_piece_visibility("after first move")
                self.capture_cell_states("after_first_move")
            else:
                self.log("ERROR: No input handler found!", "ERROR")
                
        elif self.step == 3:
            # Make another move
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(4)
                self.log("Made second move in column 4", "TEST")
                self.capture_cell_states("after_second_move")
                
        elif self.step == 4:
            # Make another move to see more chips
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(5)
                self.log("Made third move in column 5", "TEST")
                self.capture_cell_states("after_third_move")
                
        elif self.step == 5:
            self.log("Step 6: Checking board visibility before starting new game", "TEST")
            self.check_piece_visibility("before starting new game")
            self.debug_window.update_status("About to start new game - CHECK GAME BOARD")
            self.pause_test()  # Pause for manual verification
            self.debug_window.show_prompt("MANUAL CHECK NEEDED", 
                                        "Please verify chips are visible on the game board.\n"
                                        "Click 'Continue Test' when ready to proceed.")
            
        elif self.step == 6:
            self.log("Step 7: Starting new game with new settings", "TEST")
            self.debug_window.update_status("Starting new game with new settings")
            
            # Log state before starting new game
            self.log_ui_components("before_new_game")
            
            # Change settings to trigger new game
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_difficulty_changed("Hard")
                self.app_instance.input_handler.on_theme_changed("Sci-Fi")
                self.app_instance.input_handler.new_game()
            
            # Add delay before next step
            QTimer.singleShot(1000, self.check_after_new_game)
            
        elif self.step == 7:
            self.log("Step 8: Making move in new game", "TEST")
            self.debug_window.update_status("Making first move after new game - CHECK FOR RENDERING ISSUES")
            
            # Force additional update to ensure we're in a good state
            self.apply_rendering_fix()
            
            # Log the state of the game board before making a move
            self.log_game_board("before_first_move_after_new_game")
            
            # Make a move
            if hasattr(self.app_instance, 'input_handler'):
                # Pause for manual verification before the move
                self.pause_test()
                self.debug_window.show_prompt("MANUAL CHECK NEEDED",
                                            "Please check if the board is empty.\n"
                                            "After clicking Continue, a move will be made.\n"
                                            "Watch carefully for chip rendering.")
                
                # Make the move
                self.app_instance.input_handler.on_column_selected(3)
                
                # Check visibility right after the move
                self.check_piece_visibility("immediately after move in new game")
                self.capture_cell_states("first_move_after_new_game")
                
                # Schedule another check after a delay
                QTimer.singleShot(1000, self.check_delayed_visibility)
                    
        elif self.step == 8:
            self.log("Step 9: Making more moves in new game", "TEST")
            self.debug_window.update_status("Making additional moves in new game")
            
            # Pause for manual verification
            self.pause_test()
            self.debug_window.show_prompt("MANUAL CHECK NEEDED",
                                        "Please verify if first move chip is visible.\n"
                                        "Click Continue to make more moves.")
            
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(4)
                # Force extra rendering update
                self.apply_rendering_fix()
                
        elif self.step == 9:
            # Make one more move for good measure
            if hasattr(self.app_instance, 'input_handler'):
                self.app_instance.input_handler.on_column_selected(2)
                self.check_piece_visibility("after multiple moves in new game")
                
                # Pause for final verification
                self.pause_test()
                self.debug_window.show_prompt("FINAL CHECK",
                                            "Please verify if all chips are now visible.\n"
                                            "Click Continue to finish the test.")
                
        elif self.step == 10:
            self.log("Test completed!", "TEST")
            self.debug_window.update_status("Test complete - Writing results")
            self.write_report()
            self.timer.stop()
            self.test_in_progress = False
            self.finished.emit()
            self.debug_window.update_status("Test finished")
            return
            
        self.step += 1
    
    def check_after_new_game(self):
        """Check state after starting new game"""
        self.log("Checking state after starting new game", "DEBUG")
        self.log_ui_components("after_new_game")
        self.force_extra_update()
        
    def force_extra_update(self):
        """Apply extra updates after starting new game"""
        self.log("Applying extra updates after starting new game", "DEBUG")
        if hasattr(self.app_instance, 'state_handler'):
            # Force update all cells
            if hasattr(self.app_instance.state_handler, 'force_update_all_cells'):
                self.app_instance.state_handler.force_update_all_cells()
                
        # Log state after starting new game
        self.log_ui_components("after_extra_updates")
        
    def check_delayed_visibility(self):
        """Check visibility after a delay"""
        self.log("Checking piece visibility after delay", "DEBUG")
        self.check_piece_visibility("after delay in new game")
        
    def verify_renderer_support(self):
        """Verify renderer support exists and apply if needed"""
        # Check for force_update_all_cells method
        has_force_update = hasattr(self.app_instance.state_handler, 'force_update_all_cells')
        self.log(f"Renderer has force_update_all_cells method: {has_force_update}", "DEBUG")
        
        # Apply our rendering fix
        self.apply_rendering_fix()
            
    def apply_rendering_fix(self):
        """Apply rendering fixes to ensure pieces are visible"""
        self.log("Applying additional rendering fixes", "DEBUG")
        
        try:
            # Force a double update with delay to ensure rendering
            if hasattr(self.app_instance.state_handler, 'force_update_all_cells'):
                self.app_instance.state_handler.force_update_all_cells()
                # Schedule another update after a short delay
                QTimer.singleShot(300, self.app_instance.state_handler.force_update_all_cells)
                # And another for good measure
                QTimer.singleShot(600, self.app_instance.state_handler.force_update_all_cells)
            else:
                self.log("WARNING: force_update_all_cells method not found", "WARNING")
                # Apply a manual update instead
                self.manual_cell_update()
        except Exception as e:
            self.log(f"ERROR in apply_rendering_fix: {e}", "ERROR")
            
    def manual_cell_update(self):
        """Manual update of cells as a fallback"""
        self.log("Applying manual cell update as fallback", "DEBUG")
        board = self.app_instance.game_controller.get_board()
        
        try:
            for row in range(6):
                for col in range(7):
                    cell_key = f"cell_{row}_{col}"
                    cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                    if cell:
                        player = board[row][col]
                        # Even for empty cells, force a refresh
                        cell.clear()
                        cell.repaint()
                        
                        if player > 0:
                            # For non-empty cells, apply emphatic styling
                            if player == 1:
                                # Force-style Player 1 cells (RED)
                                cell.setStyleSheet("""
                                    background-color: #e74c3c;
                                    border-radius: 30px;
                                    border: 4px solid #c0392b;
                                """)
                            elif player == 2:
                                # Force-style Player 2 cells (YELLOW)
                                cell.setStyleSheet("""
                                    background-color: #f1c40f;
                                    border-radius: 30px;
                                    border: 4px solid #f39c12;
                                """)
                            # Force immediate update
                            cell.update()
                            cell.repaint()
                            self.log(f"Manually styled cell {row},{col} for player {player}", "DEBUG")
        except Exception as e:
            self.log(f"ERROR in manual_cell_update: {e}", "ERROR")
            
    def log_ui_components(self, context):
        """Log the state of important UI components"""
        self.log(f"UI component check: {context}", "DEBUG")
        
        try:
            # Log game container status
            if hasattr(self.app_instance, 'game_container'):
                self.log(f"Game container exists: {self.app_instance.game_container is not None}", "DEBUG")
                self.log(f"Game container is visible: {self.app_instance.game_container.isVisible()}", "DEBUG")
                
            # Log stacked widget status
            if hasattr(self.app_instance, 'stacked_widget'):
                current_widget = self.app_instance.stacked_widget.currentWidget()
                self.log(f"Current stacked widget: {current_widget.__class__.__name__}", "DEBUG")
                
            # Log game controller status
            if hasattr(self.app_instance, 'game_controller'):
                board = self.app_instance.game_controller.get_board()
                self.log(f"Game board shape: {board.shape}", "DEBUG")
                has_pieces = (board > 0).any()
                self.log(f"Board has pieces: {has_pieces}", "DEBUG")
                
            # Log handler status
            if hasattr(self.app_instance, 'state_handler'):
                self.log(f"State handler exists: {self.app_instance.state_handler is not None}", "DEBUG")
                
            if hasattr(self.app_instance, 'input_handler'):
                self.log(f"Input handler exists: {self.app_instance.input_handler is not None}", "DEBUG")
                
        except Exception as e:
            self.log(f"ERROR in log_ui_components: {e}", "ERROR")
            
    def log_game_board(self, context):
        """Log the current game board state"""
        self.log(f"Game board check: {context}", "DEBUG")
        
        try:
            if hasattr(self.app_instance, 'game_controller'):
                board = self.app_instance.game_controller.get_board()
                self.log(f"Board shape: {board.shape}", "DEBUG")
                self.log(f"Board contents:\n{board}", "DEBUG")
                
                # Check for any cell with pieces
                piece_positions = []
                for row in range(board.shape[0]):
                    for col in range(board.shape[1]):
                        if board[row][col] > 0:
                            piece_positions.append((row, col, int(board[row][col])))
                            
                self.log(f"Found {len(piece_positions)} pieces on board: {piece_positions}", "DEBUG")
                
        except Exception as e:
            self.log(f"ERROR in log_game_board: {e}", "ERROR")
            
    def capture_cell_states(self, context):
        """Capture the visual state of all cells"""
        self.log(f"Capturing cell states: {context}", "DEBUG")
        states = {}
        
        try:
            for row in range(6):
                for col in range(7):
                    cell_key = f"cell_{row}_{col}"
                    cell = self.app_instance.game_container.findChild(QLabel, cell_key)
                    if cell:
                        has_pixmap = cell.pixmap() is not None
                        has_color = "background-color" in cell.styleSheet()
                        if has_pixmap:
                            state = "pixmap"
                        elif has_color and ("#e74c3c" in cell.styleSheet() or "#f1c40f" in cell.styleSheet()):
                            state = "color"
                        else:
                            state = "empty"
                        states[(row, col)] = state
                        
            self.cell_states[context] = states
            filled_cells = sum(1 for state in states.values() if state != "empty")
            self.log(f"Captured {filled_cells} non-empty cells for {context}", "DEBUG")
            
        except Exception as e:
            self.log(f"ERROR in capture_cell_states: {e}", "ERROR")
            
    def check_piece_visibility(self, context):
        """Check which cells are visible and have content"""
        self.log(f"Checking piece visibility: {context}", "DEBUG")
        piece_count = 0
        board = self.app_instance.game_controller.get_board()
        
        # First, log the expected cell states from the board
        self.log("Expected board state:", "DEBUG")
        expected_pieces = []
        for row in range(6):
            for col in range(7):
                if board[row][col] > 0:
                    player = int(board[row][col])
                    expected_pieces.append((row, col, player))
                    
        self.log(f"Expected {len(expected_pieces)} pieces: {expected_pieces}", "DEBUG")
        
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
                        
        self.log(f"Visible pieces: {piece_count} at positions {visible_pieces}", "DEBUG")
        
        # Check for mismatches
        missing = []
        for row, col, player in expected_pieces:
            if (row, col) not in visible_pieces:
                missing.append((row, col, player))
                
        if missing:
            self.log(f"WARNING: {len(missing)} pieces not visible: {missing}", "WARNING")
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
                            border: 4px solid #c0392b;
                        """)
                    elif player == 2:
                        # Force-style Player 2 cells
                        cell.setStyleSheet("""
                            background-color: #f1c40f;
                            border-radius: 30px;
                            border: 4px solid #f39c12;
                        """)
                    cell.update()  # Force update
                    cell.repaint()  # Force immediate repaint
                    self.log(f"Forced update of missing piece at {row},{col} for player {player}", "DEBUG")
        
        return len(missing) == 0  # Return True if all pieces are visible
        
    def write_report(self):
        """Write the final test report"""
        self.log("Generating test report", "TEST")
        
        with open(self.log_file, "a") as f:
            f.write("\n\nRENDERING TEST SUMMARY\n")
            f.write("=====================\n\n")
            
            # Add cell state comparison
            if len(self.cell_states) > 0:
                f.write("Cell State Comparisons:\n")
                for context, states in self.cell_states.items():
                    filled_cells = sum(1 for state in states.values() if state != "empty")
                    f.write(f"  {context}: {filled_cells} non-empty cells\n")
                f.write("\n")
            
            # Add recommendations
            f.write("Recommendations:\n")
            f.write("1. Ensure force_update_all_cells is called after starting a new game\n")
            f.write("2. Consider using stronger visual refresh techniques in the cell updates\n")
            f.write("3. Check that the game board container is properly cleared before rebuilding\n")
            
        self.log(f"Test report written to {self.log_file}", "TEST")


class DebugWindow(QMainWindow):
    """Debug window for the rendering test"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Rendering Test Debug")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status display
        self.status_label = QLabel("Test not started")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Test")
        self.pause_button = QPushButton("Pause/Resume")
        self.continue_button = QPushButton("Continue Test")
        self.stop_button = QPushButton("Stop Test")
        
        self.pause_button.setEnabled(False)
        self.continue_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.continue_button)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # Prompt area
        self.prompt_area = QWidget()
        self.prompt_layout = QVBoxLayout()
        self.prompt_area.setLayout(self.prompt_layout)
        self.prompt_area.setVisible(False)
        
        self.prompt_title = QLabel("")
        self.prompt_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #e74c3c;")
        self.prompt_message = QLabel("")
        self.prompt_message.setWordWrap(True)
        
        self.prompt_button = QPushButton("OK")
        
        self.prompt_layout.addWidget(self.prompt_title)
        self.prompt_layout.addWidget(self.prompt_message)
        self.prompt_layout.addWidget(self.prompt_button)
        
        main_layout.addWidget(self.prompt_area)
        
        # Log display
        log_label = QLabel("Test Log:")
        log_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(log_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("font-family: monospace;")
        main_layout.addWidget(self.log_display)
        
        # Cell observation grid
        grid_label = QLabel("Cell States (Hover for details):")
        grid_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(grid_label)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        main_layout.addWidget(self.grid_widget)
        
        # Create empty cell observation grid
        self.cell_labels = {}
        for row in range(6):
            for col in range(7):
                label = QLabel()
                label.setFixedSize(30, 30)
                label.setStyleSheet("background-color: #bdc3c7; border: 1px solid #7f8c8d;")
                label.setToolTip(f"Cell {row},{col}: No data")
                self.grid_layout.addWidget(label, row, col)
                self.cell_labels[(row, col)] = label
        
    def connect_signals(self, test_runner):
        """Connect UI signals to the test runner"""
        self.test_runner = test_runner
        
        self.start_button.clicked.connect(self.on_start)
        self.pause_button.clicked.connect(test_runner.pause_test)
        self.continue_button.clicked.connect(self.on_continue)
        self.stop_button.clicked.connect(test_runner.stop_test)
        self.prompt_button.clicked.connect(self.on_prompt_ok)
        
    def on_start(self):
        """Handle start button click"""
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.continue_button.setEnabled(False)
        self.test_runner.start_test()
        
    def on_continue(self):
        """Handle continue button click"""
        self.prompt_area.setVisible(False)
        self.continue_button.setEnabled(False)
        self.test_runner.paused = False
        self.test_runner.next_step()
        
    def on_prompt_ok(self):
        """Handle prompt OK button click"""
        self.prompt_area.setVisible(False)
        self.continue_button.setEnabled(True)
        
    def update_status(self, status):
        """Update the status display"""
        self.status_label.setText(status)
        
    def show_prompt(self, title, message):
        """Show a prompt message"""
        self.prompt_title.setText(title)
        self.prompt_message.setText(message)
        self.prompt_area.setVisible(True)
        self.continue_button.setEnabled(True)
        
    def add_log(self, message):
        """Add a message to the log display"""
        self.log_display.append(message)
        # Scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_cell_grid(self, board):
        """Update the cell observation grid"""
        if board is None:
            return
            
        for row in range(min(6, board.shape[0])):
            for col in range(min(7, board.shape[1])):
                player = board[row][col]
                label = self.cell_labels.get((row, col))
                if label:
                    if player == 0:
                        label.setStyleSheet("background-color: #bdc3c7; border: 1px solid #7f8c8d;")
                        label.setToolTip(f"Cell {row},{col}: Empty")
                    elif player == 1:
                        label.setStyleSheet("background-color: #e74c3c; border: 1px solid #c0392b;")
                        label.setToolTip(f"Cell {row},{col}: Player 1")
                    elif player == 2:
                        label.setStyleSheet("background-color: #f1c40f; border: 1px solid #f39c12;")
                        label.setToolTip(f"Cell {row},{col}: Player 2")


def run_enhanced_test():
    """Run the enhanced rendering test"""
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Create the debug window
    debug_window = DebugWindow()
    debug_window.show()
    
    # Create the main game window
    main_window = GameMasterApp()
    main_window.show()
    
    # Create and start the test runner
    test_runner = EnhancedRenderingTest(main_window, debug_window)
    debug_window.connect_signals(test_runner)
    
    # Set up cell grid updater timer
    def update_grid():
        if hasattr(main_window, 'game_controller'):
            board = main_window.game_controller.get_board()
            debug_window.update_cell_grid(board)
    
    grid_timer = QTimer()
    grid_timer.timeout.connect(update_grid)
    grid_timer.start(500)  # Update every 500ms
    
    # Install event filter for additional debugging
    class EventFilter(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.Show and obj is main_window.game_container:
                test_runner.log("Game container SHOW event detected", "DEBUG")
            elif event.type() == QEvent.Type.Hide and obj is main_window.game_container:
                test_runner.log("Game container HIDE event detected", "DEBUG")
            return False
    
    event_filter = EventFilter()
    main_window.game_container.installEventFilter(event_filter)
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    run_enhanced_test() 