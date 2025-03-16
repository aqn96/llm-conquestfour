import sys
import os
import subprocess
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QComboBox, QWidget, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap, QAction
from PyQt6.QtCore import Qt
from ai.ollama.llama_bot import LLMBot
from game import Connect4GameWindow


class Connect4IntroUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.window2 = None

    def initUI(self):
        self.setWindowTitle("Connect 4")
        self.setGeometry(550, 100, 800, 800)

        # Create a central widget for layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Add Background Image
        self.background_label = QLabel(central_widget)
        image_path = os.path.abspath("log_in_page_bg.jpg")
        pixmap = QPixmap(image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 800, 800)

        self.menuBar().setNativeMenuBar(False)

        # Create a Menu Bar
        menu_bar = self.menuBar()
        game_menu_item = menu_bar.addMenu("&Game Colletions")
        help_menu_item = menu_bar.addMenu("&Help")

        # Add "About" Action to Help Menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.show_about)

        # Add Future Games to "Game Collections"
        hangman_action = QAction("Hangman", self)
        game_menu_item.addAction(hangman_action)
        hangman_action.triggered.connect(lambda: self.show_future_games("Hangman"))
        # lambda delays the function being run when staring the program

        battle_ship_action = QAction("Battle Ship", self)
        game_menu_item.addAction(battle_ship_action)
        battle_ship_action.triggered.connect(lambda: self.show_future_games("Battle Ship"))

        code_name_action = QAction("Code Name", self)
        game_menu_item.addAction(code_name_action)
        code_name_action.triggered.connect(lambda: self.show_future_games("Code Name"))

        d_n_d_action = QAction("Dungeons and Dragons", self)
        game_menu_item.addAction(d_n_d_action)
        d_n_d_action.triggered.connect(lambda: self.show_future_games("Dungeons & Dragons"))

        # Layout for UI Elements
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        layout.setContentsMargins(150, 0, 150, 50)

        # UI Components
        self.name_label = QLabel("Name:", self)
        self.name_label.setFont(QFont("Arial", 20))
        self.name_label.setStyleSheet("color: black; background-color: lightgray; padding: 5px; border-radius: 5px;")

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setStyleSheet("color: black; background-color: white; font-size: 16px; height: 40px; width: 300px; padding: 5px;")  

        self.difficulty_label = QLabel("Difficulty Level:", self)
        self.difficulty_label.setFont(QFont("Arial", 20))
        self.difficulty_label.setStyleSheet("color: black; background-color: lightgray; padding: 5px; border-radius: 5px;")

        self.difficulty_dropdown = QComboBox(self)
        self.difficulty_dropdown.addItems(["Easy", "Normal", "Hard"])
        self.difficulty_dropdown.setStyleSheet("color: black; background-color: white; font-size: 16px; height: 40px; width: 300px; padding: 5px;")  

        self.theme_label = QLabel("Game Narrative Theme:", self)
        self.theme_label.setFont(QFont("Arial", 20))
        self.theme_label.setStyleSheet("color: black; background-color: lightgray; padding: 5px; border-radius: 5px;")

        self.theme_dropdown = QComboBox(self)
        self.theme_dropdown.addItems(["Western", "Civil War", "Fantasy", "Harry Potter"])
        self.theme_dropdown.setStyleSheet("color: black; background-color: white; font-size: 16px; height: 40px; width: 300px; padding: 5px;")

        self.ai_label = QLabel("Narrator Personality:", self)
        self.ai_label.setFont(QFont("Arial", 20))
        self.ai_label.setStyleSheet("color: black; background-color: lightgray; padding: 5px; border-radius: 5px;")

        self.ai_dropdown = QComboBox(self)
        self.ai_dropdown.addItems(["Snarky", "Aggressive", "Encouraging"])
        self.ai_dropdown.setStyleSheet("color: black; background-color: white; font-size: 16px; height: 40px; width: 300px; padding: 5px;") 

        self.start_button = QPushButton("Start Game", self)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                font-size: 20px;
                padding: 15px;
                border-radius: 10px;
                color: black;
            }
            QPushButton:hover {
                background-color: #87CEEB;
            }
        """)
        self.start_button.clicked.connect(self.start_game)

        # Add Widgets to Layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.difficulty_label)
        layout.addWidget(self.difficulty_dropdown)
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_dropdown)
        layout.addWidget(self.ai_label)
        layout.addWidget(self.ai_dropdown)
        layout.addWidget(self.start_button)

        # Apply Layout to Central Widget
        central_widget.setLayout(layout)
        
    
    def init_bot(self, name, ai_personality, theme):
        """Initialize the Bot with different settings"""
        self.bot = LLMBot("mistral", "Gemma", name, personality_key=ai_personality, occupation_key="Pikachu", setting_key=theme)

    def start_game(self):
        """ Collects user input and starts the game """
        name = self.name_input.text()
        difficulty = self.difficulty_dropdown.currentText()
        theme = self.theme_dropdown.currentText()
        ai_personality = self.ai_dropdown.currentText()

        print(f"Starting game with:\nName: {name}\nDifficulty: {difficulty}\nTheme: {theme}\nAI Personality: {ai_personality}")
        
        # subprocess.Popen([
        #     sys.executable, "game.py",
        #     "--name", name,
        #     "--difficulty", difficulty,
        #     "--theme", theme,
        #     "--ai-personality", ai_personality
        # ])
        bot = LLMBot("mistral","Gemma",name,personality_key=ai_personality,occupation_key="Pikachu",setting_key=theme)
        self.window2 = Connect4GameWindow(bot, difficulty, self)
        self.window2.show()
        self.close()
        

    def show_about(self):
        """ Displays an About message in a dialog"""
        dialog = AboutDialog()
        dialog.exec()

    def show_future_games(self, game):
        """ Displays an Future Game message in a dialog"""
        dialog = FutureGameDialog(game)
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Connect 4")
        content = """
        Connect 4 Game - Have fun playing in your own setting!
        """
        self.setText(content)


class FutureGameDialog(QMessageBox):
    def __init__(self, game):
        super().__init__()
        self.setWindowTitle(f"About {game}")
        content = f"{game} Coming Soon! Stay Tuned!"
        self.setText(content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Connect4IntroUI()
    window.show()
    window.start_button.clicked.connect(window.start_game)
    
    sys.exit(app.exec())
