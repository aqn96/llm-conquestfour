"""
Styles and theming functions for the UI
"""
from PyQt6.QtGui import QFont


def get_main_font(size=12, bold=False):
    """
    Returns a consistent font for the application
    
    Args:
        size: Font size
        bold: Whether the font should be bold
    
    Returns:
        QFont: The configured font
    """
    font = QFont("Arial", size)
    if bold:
        font.setBold(True)
    return font


def apply_button_style(button, primary=True):
    """
    Apply a consistent style to buttons
    
    Args:
        button: The QPushButton to style
        primary: Whether this is a primary action button
    """
    if primary:
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                border: none;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
    else:
        button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                border: none;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #6b7879;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
    
    # QPushButton doesn't have setAlignment, but we can center the text
    # using the stylesheet instead 