"""
Window setup utilities for the application
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os


def configure_window_appearance(window):
    """
    Configure the appearance of the main application window
    
    Args:
        window: The main window to configure
    """
    # Set window title
    window.setWindowTitle("LLM GameMaster: Connect Four")
    
    # Set window flags for proper appearance
    window.setWindowFlags(
        Qt.WindowType.Window |
        Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowCloseButtonHint |
        Qt.WindowType.WindowMinimizeButtonHint |
        Qt.WindowType.WindowMaximizeButtonHint
    )
    
    # Set window icon if available
    icon_path = os.path.join('assets', 'images', 'app_icon.png')
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
        
    # Set stylesheet for the window
    window.setStyleSheet("""
        QMainWindow {
            background-color: #1e293b;
        }
        QToolTip {
            color: #ffffff;
            background-color: #2a3f5f;
            border: 1px solid #061539;
            border-radius: 3px;
            padding: 3px;
        }
    """)
    
    # Minimum size for usability
    window.setMinimumSize(800, 600)

def load_background_images(window):
    """Load background and title images for the application"""
    # Root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    ui_dir = os.path.join(root_dir, 'ui')
    
    # Check for background images
    window.background_image = None
    for bg_name in ['background.png', 'background.jpg', 'bg.png', 'bg.jpg']:
        bg_path = os.path.join(ui_dir, bg_name)
        if os.path.exists(bg_path):
            try:
                # Set window background
                palette = QPalette()
                pixmap = QPixmap(bg_path)
                brush = QBrush(pixmap)
                palette.setBrush(QPalette.ColorRole.Window, brush)
                window.setPalette(palette)
                window.background_image = pixmap
                print(f"Loaded background image: {bg_path}")
                break
            except Exception as e:
                print(f"Error loading background: {e}")
    
    # Check for title/start screen images
    window.title_image = None
    for title_name in ['start_screen.png', 'start.png', 'title.png']:
        title_path = os.path.join(ui_dir, title_name)
        if os.path.exists(title_path):
            try:
                window.title_image = QPixmap(title_path)
                print(f"Loaded title image: {title_path}")
                break
            except Exception as e:
                print(f"Error loading title image: {e}") 