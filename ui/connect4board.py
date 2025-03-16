from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QMouseEvent
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from game.connect_four import ConnectFourGame, Player
from game.narrative_engine import MoveEvaluator
from game.difficulty_levels import EasyAI, MediumAI, HardAI


class Connect4Board(QWidget):
    moveMade = pyqtSignal(str) # Signal to pass move score to the main window
    def __init__(self, difficulty, parent=None):
        super().__init__(parent)
        self.difficulty = difficulty
        self.current_column = None  # Track where the player is clicking
        self.current_player = "red"  # Start with player Red
        self.board_state = [6] * 7
        self.game_logic = ConnectFourGame()
        self.game_over = False
        if difficulty == "Easy":
            self.computer_player = EasyAI()
        elif difficulty == "Normal":
            self.computer_player = MediumAI()
        else:
            self.computer_player = HardAI()
        self.move_evaluator = MoveEvaluator()
        self.init_board()

    def init_board(self):
        """ Initialize the Connect 4 Board UI. """
        self.board_container = QWidget(self)
        self.board_container.setFixedSize(500, 500)
        self.board_container.setStyleSheet("background-color: lightblue; border: 2px solid black; border-radius: 10px")

        # Create grid layout for board
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(10)  # Set margin between cells

        self.board_buttons = [[QPushButton(" ") for _ in range(7)] for _ in range(7)]  # 7x7 Grid

        for row in range(7):
            for col in range(7):
                if row == 0:
                    self.create_top_buttons(col)  # Top row for dropping disks
                else:
                    self.board_buttons[row][col].setFixedSize(60, 60)
                    self.board_buttons[row][col].setStyleSheet(
                        "background-color: white; border: 2px solid grey; border-radius: 30px"
                    )

                self.board_layout.addWidget(self.board_buttons[row][col], row, col)

        self.setLayout(self.board_layout)  # Set layout to the board

    def create_top_buttons(self, col):
        """ Create invisible buttons on top row for dropping disks. """
        self.board_buttons[0][col].setFixedSize(60, 60)
        self.board_buttons[0][col].setStyleSheet("background-color: lightgrey; border: 2px solid grey; font-size: 20px")
        self.board_buttons[0][col].setText(f"{col}")

        # Enable mouse tracking
        self.board_buttons[0][col].installEventFilter(self)

    def eventFilter(self, obj, event):
        """ Handle mouse press and release for dropping disks when it is player's turn"""
        if self.game_over:
            return super().eventFilter(obj, event)
        if isinstance(event, QMouseEvent) and self.current_player == "red":
            for col in range(7):
                if obj == self.board_buttons[0][col]:  # Only allow clicking top row
                    if event.type() == QEvent.Type.MouseButtonPress:
                        return self.on_mouse_press(col)
                    elif event.type() == QEvent.Type.MouseButtonRelease:
                        return self.on_mouse_release(event, col)
        return super().eventFilter(obj, event)

    def on_mouse_press(self, col):
        """ Show the disk when the player clicks a top button. """
        self.current_column = col
        # color = "red" if self.current_player == "red" else "yellow"
        self.board_buttons[0][col].setStyleSheet(f"background-color: 'red'; border-radius: 30px; border: 2px solid grey;")
        return True

    def on_mouse_release(self, event, col):
        """ Drop the disk if released in the same column and top row, otherwise remove it."""
        release_pos = event.globalPosition()  # Get global coordinates

        board_pos = self.mapFromGlobal(release_pos)  # Convert to board-local position
        release_col = int(board_pos.x() // (60 + 10))  # Convert X position to column index
        release_row = int(board_pos.y() // (60 + 10))  # Convert Y position to row index

        if release_row == 0 and release_col == self.current_column and self.game_logic.is_valid_move(release_col):
            self.drop_piece(release_col)
        else:
            self.reset_top_button(self.current_column)
        
        return True

    def drop_piece(self, column):
        """ Drop the piece into the lowest available row. """
        row = self.board_state[column] # the lowest available row in this column

        if row < 1: # If row is full, do nothing
            self.reset_top_button(column)
            return
        
        color = "red" if self.current_player == "red" else "yellow"
        self.game_logic.make_move(column)
        if self.current_player == "red":
            # Get move score and emit signal to main window
            score_str = self.getMoveScore(column)
            self.moveMade.emit(score_str)  # Emit move score
        self.board_buttons[row][column].setStyleSheet(f"background-color: {color}; border-radius: 30px; border: 2px solid grey")
        self.reset_top_button(column)
        self.board_state[column] -= 1
        self.current_player = "yellow" if self.current_player == "red" else "red"  # Switch player
        end_state = self.check_board_state()
        if not end_state and self.current_player == "yellow":
            self.computer_move()
    
    def getMoveScore(self, col):
        """ Evaluate move score using MoveEvaluator """
        return self.move_evaluator.evaluate_move(self.game_logic, col)
    
    def computer_move(self):
        """ Computer moving piece into column"""
        col = self.computer_player.find_best_move(self.game_logic)
        self.drop_piece(col)
        
    def check_board_state(self):
        """ Check current board state if there is a winner"""
        winner = self.game_logic.get_winner()
        if winner:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Game Over")
            winner_player = "Computer" if winner == Player.TWO else "YOU"
            msg_box.setText(f"The winner is: {winner_player}!\n")
            msg_box.exec()
            self.setEnabled(False)
            self.game_over = True
            return winner
        return None

    def reset_top_button(self, col):
        """ Reset the top row button color if not dropped. """
        self.board_buttons[0][col].setStyleSheet("background-color: lightgrey; border: 2px solid grey; font-size: 20px")
