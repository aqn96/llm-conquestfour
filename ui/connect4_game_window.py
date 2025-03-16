import sys
import os
from ui.connect4board import Connect4Board
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget,
    QTextEdit, QLineEdit, QPushButton, QMessageBox, QGridLayout, QDialog
)
from PyQt6.QtGui import QPixmap, QFont, QAction
from PyQt6.QtCore import Qt, QTimer
from ai.ollama.llama_bot import LLMBot
from game.thermal_aware_ai import ThermalAwareAI
from speech_to_text.audio_recorder import AudioRecorder
from speech_to_text.speech_to_text import SpeechToText

class Connect4GameWindow(QMainWindow):
    def __init__(self, bot, difficulty, start_window):
        super().__init__()
        self.bot = bot
        self.difficulty = difficulty
        self.start_window = start_window
        self.temperatureAI = ThermalAwareAI()
        self.event = ""
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle("Connect 4 - Game Window")
        self.setGeometry(450, 100, 1000, 800)  # Set window size

        # Create a central widget to hold the layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Add Background Image
        self.background_label = QLabel(central_widget)
        image_path = os.path.abspath("ui/connect4_game_bg.png")
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
        
        # How to Play Action
        how_to_play_action = QAction("&How To Play", self)
        menu_bar.addAction(how_to_play_action)
        how_to_play_action.triggered.connect(self.show_how_to_play_action)

        # Help Menu
        help_menu_item = menu_bar.addMenu("&Help")
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.show_about)  # Open About Dialog

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        main_layout.setContentsMargins(90, 0, 90, 30)

        bottom_layout = QHBoxLayout()  # Game board on left, chatbox on right

        # Board Container (500 x 500)
        self.game_board = Connect4Board(self.difficulty, self)
        self.game_board.moveMade.connect(self.update_event)
        bottom_layout.addWidget(self.game_board)

        # Chatbox Section
        chat_layout = QVBoxLayout()

        # Chat Display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: white; border: 1px solid gray; color: black")
        self.chat_display.setFixedSize(300, 400)  # Set chat display size
        chat_layout.addWidget(self.chat_display)

        # User Input
        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Enter your message...")
        self.chat_input.setFixedSize(300, 40)
        self.chat_input.setFocus()

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        # Send Button
        self.send_button = QPushButton("Send", self)
        self.send_button.setFixedSize(100, 40)
        self.send_button.setStyleSheet("background-color: green; font-size: 18px;")

        # Speak Button (New)
        self.speak_button = QPushButton("Speak", self)
        self.speak_button.setFixedSize(100, 40)
        self.speak_button.setStyleSheet("background-color: blue; font-size: 18px; color: white;")

        # Add widgets to layout
        buttons_layout.addWidget(self.send_button)
        buttons_layout.addWidget(self.speak_button)

        # Add widgets to chat layout
        chat_layout.addWidget(self.chat_input)
        chat_layout.addLayout(buttons_layout)

        # Connect button click to send_message function
        self.send_button.clicked.connect(self.send_message)
        self.chat_input.returnPressed.connect(self.send_message)

        # Connect Speak button to record and transcribe function
        self.speak_button.clicked.connect(self.process_speech)

        # Add Chatbox Layout to Bottom Layout
        bottom_layout.addLayout(chat_layout)

        # Add Bottom Layout to Main Layout
        main_layout.addLayout(bottom_layout)

        # Apply layout to central widget
        central_widget.setLayout(main_layout)

        # CPU temperature widget#
        temp = self.temperatureAI.get_current_temperature()
        self.temp_label = QLabel(f"{temp:.1f}°C", central_widget)
        self.temp_label.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 5px;
            font-size: 30px;
            color: black;
        """)
        self.temp_label.adjustSize()
        label_width = self.temp_label.width()
        self.temp_label.move(self.width() - label_width - 50, 40)
        self.temp_label.raise_()
        # Clearly add timer explicitly for continuous updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_temperature)
        self.timer.start(1000)  # Update every second
    
    def process_speech(self):
        """ Records speech, transcribes it, and inserts into chat input field. """
        transcription = self.record_and_transcribe()
        if transcription:
            self.chat_input.setText(transcription)
            self.send_message()  # Automatically process the transcribed message

    def update_temperature(self):
        """ Update the temperature label regularly. """
        temp = self.temperatureAI.get_current_temperature()

        self.temp_label.setText(f"{temp:.1f}°C")
        self.temp_label.adjustSize()
        
        # Keep aligned top-right clearly after resizing
        label_width = self.temp_label.width()
        self.temp_label.move(self.width() - label_width - 50, 40)
    
    def update_event(self, move_score):
        """ ✅ Update event when a move is made """
        self.event = move_score
        print(f"Updated Event: {self.event}")  # debugging
        self.chat_display.append(self.bot.get_response_to_speech(f"Player makes a {self.event} move!"))
        self.chat_display.append(f"\n")
        self.chat_display.toPlainText()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        label_width = self.temp_label.width()
        self.temp_label.move(self.width() - label_width - 50, 40)
    
    def send_message(self):
        """ Capture user input and display it in the chat display """
        user_input = self.chat_input.text()
        
        if user_input.strip():
            self.chat_display.append(f"You: {user_input}")
            self.chat_input.clear()
            self.chat_display.append(f"\n")
            self.chat_display.append(self.bot.get_response_to_speech(user_input))
            self.chat_display.append(f"\n")

        self.chat_display.toPlainText()

    def show_about(self):
        """ Opens the About dialog """
        dialog = AboutDialog()
        dialog.exec()
    
    def show_how_to_play_action(self):
        """ Displays an how_to_play message in a dialog"""
        dialog = HowToPlayDialog()
        dialog.exec()

    def restart(self):
        """ Restart the Game """
        dialog = RestartDialog(self.start_window, self)
        dialog.exec()

    def quit(self):
        """ Quit the Game """
        dialog = QuitDialog()
        dialog.exec()
    
    def record_and_transcribe(self, duration: int = 5, model_size: str = "base"):
        """
        Records audio from the microphone and transcribes it to text.

        Args:
            duration (int): The length of the recording in seconds.
            model_size (str): The Whisper model size to use for transcription.

        Returns:
            str: The transcribed text.
        """
        # Initialize modules
        recorder = AudioRecorder()
        stt = SpeechToText(model_size=model_size)

        # Record audio
        audio_file = recorder.record(duration=duration)

        # Transcribe audio
        transcription = stt.transcribe(audio_file)
        print("Transcription:", transcription)

        # Clean up by deleting the recorded file
        recorder.delete_audio(audio_file)

        return transcription


class AboutDialog(QMessageBox):
    """ About Dialog (Shared with Login Page) """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Connect 4")
        content = """
        Connect 4 Game - Have fun playing in your own setting!
        """
        self.setText(content)


class HowToPlayDialog(QMessageBox):
    """ How To Play Connect4 Instruction Dialog """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("How to Play Connect 4")
        content =  """
        <h2>🔴🟡 Welcome to Connect 4! 🟡🔴</h2>
        
        <h3>🎯 Goal:</h3>
        <p>Be the first player to connect <b>four</b> of your pieces in a row, column, or diagonal.</p>

        <h3>🎮 How to Play:</h3>
        <ol>
            <li>Click on a <b>numbered button in the top row</b> to select a column.</li>
            <li>Hold the mouse to display your <b style='color: red;'>red (🔴)</b> or <b style='color: yellow;'>yellow (🟡)</b> disk above the board.</li>
            <li><b>Release the mouse in the same column</b> to drop the disk into the lowest available row.</li>
            <li><b>If released outside the top row or in a different column, the move is canceled.</b></li>
        </ol>

        <h3>🔄 Turn-Based Play:</h3>
        <ul>
            <li>Players take turns dropping disks.</li>
            <li><b>Red (🔴) always plays first</b>, followed by <b>Yellow (🟡).</b></li>
        </ul>

        <h3>🏆 Winning the Game:</h3>
        <p>Align <b>four pieces</b> vertically, horizontally, or diagonally to win!</p>

        <h3>🚫 Restart or Quit:</h3>
        <ul>
            <li>Use the <b>"Restart"</b> option in the menu to reset the game.</li>
            <li>Use <b>"Quit"</b> to exit.</li>
        </ul>

        <p style='text-align:center; font-size: 18px;'><b>Good luck and have fun! 🎉</b></p>
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
    def __init__(self, start_window, curr_window):
        super().__init__()
        self.setWindowTitle("Restart The Game")
        layout = QGridLayout()
        self.start_window = start_window
        self.curr_window = curr_window

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
        self.curr_window.close()
        self.start_window.show()
