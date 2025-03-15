"""
Controller for the intro/login screen
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QPalette, QBrush

from app.ui.styles import apply_button_style


class IntroController(QWidget):
    """Controller for the intro screen"""
    
    # Signal to emit when the start button is clicked
    start_game_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._build_ui()
        
    def _build_ui(self):
        """Build the UI for the intro screen"""
        # Set up a central widget with fixed size to better control layout
        self.setMinimumSize(1000, 700)
        
        # Set background image
        bg_image_path = os.path.join('assets', 'images', 'log_in_page_bg.jpg')
        if os.path.exists(bg_image_path):
            # Create and set background
            palette = QPalette()
            pixmap = QPixmap(bg_image_path)
            
            # Scale the pixmap to fit the widget
            pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Set the background
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setAutoFillBackground(True)
            self.setPalette(palette)
        else:
            # Fallback to a color if image doesn't exist
            self.setStyleSheet("""
                background-color: #1e3a8a;
            """)
            print(f"Warning: Background image not found at {bg_image_path}")
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Add spacer at top
        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )
        
        # Create dialog frame for controls
        dialog_frame = QFrame()
        dialog_frame.setObjectName("loginFrame")
        dialog_frame.setStyleSheet("""
            #loginFrame {
                background-color: rgba(16, 24, 40, 0.8);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        # Set maximum width for the dialog frame
        dialog_frame.setMaximumWidth(500)
        
        # Create layout for the dialog
        dialog_layout = QVBoxLayout(dialog_frame)
        dialog_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Connect Four Game")
        title_label.setStyleSheet("""
            font-size: 28px;
            color: white;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_layout.addWidget(title_label)
        
        # Add subtitle
        subtitle_label = QLabel("AI-Powered Narrative Game")
        subtitle_label.setStyleSheet("""
            font-size: 18px;
            color: #9ca3af;
            margin-bottom: 20px;
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_layout.addWidget(subtitle_label)
        
        # Name input
        name_label = QLabel("Your Name:")
        name_label.setStyleSheet("color: white; font-size: 16px;")
        dialog_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #374151;
                background-color: #1f2937;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1px solid #60a5fa;
            }
        """)
        self.name_input.setText("Player")
        dialog_layout.addWidget(self.name_input)
        
        # Difficulty selection
        difficulty_label = QLabel("Difficulty:")
        difficulty_label.setStyleSheet("color: white; font-size: 16px;")
        dialog_layout.addWidget(difficulty_label)
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setCurrentText("Medium")
        self.difficulty_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #374151;
                background-color: #1f2937;
                color: white;
                font-size: 16px;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #1f2937;
                color: white;
                selection-background-color: #2563eb;
            }
        """)
        dialog_layout.addWidget(self.difficulty_combo)
        
        # Theme selection
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: white; font-size: 16px;")
        dialog_layout.addWidget(theme_label)
        
        theme_layout = QHBoxLayout()
        
        self.fantasy_checkbox = QCheckBox("Fantasy")
        self.fantasy_checkbox.setChecked(True)
        self.fantasy_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 16px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #374151;
                background-color: #1f2937;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #60a5fa;
                background-color: #3b82f6;
            }
        """)
        self.fantasy_checkbox.toggled.connect(self._on_fantasy_toggled)
        theme_layout.addWidget(self.fantasy_checkbox)
        
        self.scifi_checkbox = QCheckBox("Sci-Fi")
        self.scifi_checkbox.setChecked(False)
        self.scifi_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 16px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #374151;
                background-color: #1f2937;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #60a5fa;
                background-color: #3b82f6;
            }
        """)
        self.scifi_checkbox.toggled.connect(self._on_scifi_toggled)
        theme_layout.addWidget(self.scifi_checkbox)
        
        dialog_layout.addLayout(theme_layout)
        
        # Start button
        self.start_button = QPushButton("Start Game")
        apply_button_style(self.start_button)
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self._on_start_clicked)
        dialog_layout.addWidget(self.start_button)
        
        # Center the dialog horizontally
        dialog_container = QHBoxLayout()
        dialog_container.addStretch(1)
        dialog_container.addWidget(dialog_frame)
        dialog_container.addStretch(1)
        
        # Add dialog to main layout
        main_layout.addLayout(dialog_container)
        
        # Add spacer at bottom
        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Expanding)
        )
        
    def _on_start_clicked(self):
        """Handle the start button click"""
        # Gather settings
        settings = {
            'player_name': self.name_input.text(),
            'difficulty': self.difficulty_combo.currentText(),
            'themes': []
        }
        
        # Add selected themes
        if self.fantasy_checkbox.isChecked():
            settings['themes'].append('fantasy')
        if self.scifi_checkbox.isChecked():
            settings['themes'].append('sci-fi')
            
        # Emit signal with settings
        self.start_game_signal.emit(settings)
        
    def _on_fantasy_toggled(self, checked):
        """Handle fantasy checkbox toggled"""
        if checked and self.scifi_checkbox.isChecked():
            # Prevent both from being checked - uncheck sci-fi
            self.scifi_checkbox.blockSignals(True)
            self.scifi_checkbox.setChecked(False)
            self.scifi_checkbox.blockSignals(False)

    def _on_scifi_toggled(self, checked):
        """Handle sci-fi checkbox toggled"""
        if checked and self.fantasy_checkbox.isChecked():
            # Prevent both from being checked - uncheck fantasy
            self.fantasy_checkbox.blockSignals(True)
            self.fantasy_checkbox.setChecked(False)
            self.fantasy_checkbox.blockSignals(False)
        
    def resizeEvent(self, event):
        """Handle resize events to update background image scaling"""
        super().resizeEvent(event)
        
        # Update background on resize
        bg_image_path = os.path.join('assets', 'images', 'log_in_page_bg.jpg')
        if os.path.exists(bg_image_path):
            # Create and set background
            palette = QPalette()
            pixmap = QPixmap(bg_image_path)
            
            # Scale the pixmap to fit the widget
            pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Set the background
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette) 