import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QTextEdit, QLineEdit, QPushButton, QMessageBox, QGridLayout, QDialog
)
from PyQt6.QtGui import QPixmap, QFont, QAction
from PyQt6.QtCore import Qt


class Connect4GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Connect 4 - Game Window")
        self.setGeometry(450, 100, 1000, 800)  # Set window size

        # Create a central widget to hold the layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Add Background Image
        self.background_label = QLabel(central_widget)
        image_path = os.path.abspath("connect4_game_bg.png")
        pixmap = QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1000, 800)
        
        # Create Menu Bar
        self.menuBar().setNativeMenuBar(False)  # Ensure it appears inside the window
        menu_bar = self.menuBar()

        # Game Menu
        game_control_item = menu_bar.addMenu("&Game Controls")
        restart_action = QAction("Restart", self)
        quit_action = QAction("Quit", self)
        game_control_item.addAction(restart_action)
        game_control_item.addAction(quit_action)
        restart_action.triggered.connect(self.restart)
        quit_action.triggered.connect(self.quit)
        
        # Help Menu
        help_menu_item = menu_bar.addMenu("&Help")
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.show_about)  # Open About Dialog

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        main_layout.setContentsMargins(90, 0, 90, 30)

        
        bottom_layout = QHBoxLayout()  # Game board on left, chatbox on right

        # Game Board Placeholder
        self.game_board = QWidget(self)
        self.game_board.setStyleSheet("background-color: lightblue; border: 2px solid black;")
        self.game_board.setFixedSize(500, 500)  # Set game board size
        bottom_layout.addWidget(self.game_board)

        # Chatbox Section
        chat_layout = QVBoxLayout()

        # Chat Display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.chat_display.setFixedSize(300, 400)  # Set chat display size
        chat_layout.addWidget(self.chat_display)

        # User Input
        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Enter your message...")
        self.chat_input.setFixedSize(300, 40)
        chat_layout.addWidget(self.chat_input)

        # Send Button
        self.send_button = QPushButton("Send", self)
        self.send_button.setFixedSize(100, 40)
        self.send_button.setStyleSheet("background-color: green; font-size: 18px;")
        chat_layout.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Connect button click to send_message function
        self.send_button.clicked.connect(self.send_message)

        # Add Chatbox Layout to Bottom Layout
        bottom_layout.addLayout(chat_layout)

        # Add Bottom Layout to Main Layout
        main_layout.addLayout(bottom_layout)

        # Apply layout to central widget
        central_widget.setLayout(main_layout)

    def send_message(self):
        """ Capture user input and display it in the chat display """
        user_input = self.chat_input.text()
        if user_input.strip():
            self.chat_display.append(f"You: {user_input}")
            self.chat_input.clear()

        self.last_user_message = user_input
        print("User said:", self.last_user_message)

    def show_about(self):
        """ Opens the About dialog """
        dialog = AboutDialog()
        dialog.exec()
    
    def restart(self):
        """ Restart the Game """
        dialog = RestartDialog()
        dialog.exec()
    
    def quit(self):
        """ Quit the Game """
        dialog = QuitDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    """ About Dialog (Shared with Login Page) """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Connect 4")
        content = """
        Connect 4 Game - Have fun playing in your own setting!
        """
        self.setText(content)


class QuitDialog(QDialog):
    """ Quit Dialog (Exit the Game) """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quit Current Game")
        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to quit?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.quit_application)
        no.clicked.connect(self.close)

    def quit_application(self):
        """ Closes everything (the entire application) """
        self.close()
        QApplication.quit()
        sys.exit(0)
        os._exit(0)


class RestartDialog(QDialog):
    """ Restart Dialog (Back to Log in) """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restart The Game")
        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to restart?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.restart_application)
        no.clicked.connect(self.close)
    
    def restart_application(self):
        """ Close current game window and load start_game"""
        self.close()
        subprocess.Popen([sys.executable, "game_setup.py"])
        QApplication.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Connect4GameWindow()
    window.show()
    sys.exit(app.exec())
