from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget, QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont

class GameBoard(QWidget):
    move_made = pyqtSignal(int)  # Signal when a move is made
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Create title label
        title_label = QLabel("Connect Four")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            color: #3A6A9C;
            background-color: rgba(255, 255, 255, 150);
            border-radius: 8px;
            padding: 5px;
            margin-bottom: 10px;
        """)
        self.layout.addWidget(title_label)
        
        # Create button row
        self.button_frame = QFrame()
        button_layout = QGridLayout(self.button_frame)
        button_layout.setSpacing(8)
        
        # Create column buttons
        self.buttons = []
        for col in range(7):
            button = QPushButton("▼")
            button.setFixedSize(60, 40)
            button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            button.clicked.connect(lambda _, c=col: self.move_made.emit(c))
            button_layout.addWidget(button, 0, col)
            self.buttons.append(button)
        
        self.layout.addWidget(self.button_frame)
        
        # Create board frame
        self.board_frame = QFrame()
        self.board_frame.setStyleSheet("""
            background-color: #3A6A9C;
            border-radius: 10px;
            padding: 5px;
        """)
        self.board_layout = QGridLayout(self.board_frame)
        self.board_layout.setSpacing(8)
        
        # Apply overall styling for cell aesthetics
        self.setStyleSheet("""
            QPushButton { 
                font-size: 18px; 
                font-weight: bold; 
                min-height: 40px;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4DA6FF, stop:1 #2A5A8C);
                color: white;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6DB9FF, stop:1 #3A6A9C);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #999999;
            }
        """)
        
        # Create board cells
        self.cells = []
        for row in range(6):
            row_cells = []
            for col in range(7):
                cell = QWidget()
                cell.setFixedSize(60, 60)
                cell.setStyleSheet("""
                    background-color: white; 
                    border: 1px solid #333; 
                    border-radius: 30px; 
                    margin: 2px;
                """)
                self.board_layout.addWidget(cell, row, col)
                row_cells.append(cell)
            self.cells.append(row_cells)
        
        self.layout.addWidget(self.board_frame)
            
    def disable_buttons(self):
        """Disable all buttons when game is over"""
        for button in self.buttons:
            button.setEnabled(False)
            
    def enable_buttons(self):
        """Enable all buttons for a new game"""
        for button in self.buttons:
            button.setEnabled(True)
            
    def reset_board(self):
        """Reset all cells to white (empty)"""
        for row in self.cells:
            for cell in row:
                cell.setStyleSheet("""
                    background-color: white; 
                    border: 1px solid #333; 
                    border-radius: 30px; 
                    margin: 2px;
                """) 