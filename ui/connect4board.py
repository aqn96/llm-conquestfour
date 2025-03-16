from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QMouseEvent


class Connect4Board(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_board()
        self.current_column = None  # Track where the player is clicking
        self.current_player = "red"  # Start with player Red
        self.board_state = [6] * 7 # This needs to be connected with the game

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
        """ Handle mouse press and release for dropping disks. """
        if isinstance(event, QMouseEvent):
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
        color = "red" if self.current_player == "red" else "yellow"
        self.board_buttons[0][col].setStyleSheet(f"background-color: {color}; border-radius: 30px; border: 2px solid grey;")
        return True

    def on_mouse_release(self, event, col):
        """ Drop the disk if released in the same column and top row, otherwise remove it."""
        release_pos = event.globalPosition()  # Get global coordinates

        board_pos = self.mapFromGlobal(release_pos)  # Convert to board-local position
        release_col = board_pos.x() // (60 + 10)  # Convert X position to column index
        release_row = board_pos.y() // (60 + 10)  # Convert Y position to row index

        if release_row == 0 and release_col == self.current_column:
            self.drop_piece(col)
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
        self.board_buttons[row][column].setStyleSheet(f"background-color: {color}; border-radius: 30px; border: 2px solid grey")
        self.reset_top_button(column)
        self.board_state[column] -= 1
        self.current_player = "yellow" if self.current_player == "red" else "red"  # Switch player
    
    def reset_top_button(self, col):
        """ Reset the top row button color if not dropped. """
        self.board_buttons[0][col].setStyleSheet("background-color: lightgrey; border: 2px solid grey; font-size: 20px")
