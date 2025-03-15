"""
Layout builder for the main game interface
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpacerItem, QSizePolicy, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPalette, QLinearGradient, QBrush

from app.ui.styles import apply_button_style
from app.ui.narrative import NarrativeDisplay


def build_main_layout(app):
    """
    Build the main layout for the game screen
    
    Args:
        app: The GameMasterApp instance
    """
    # Get the existing layout from the game container
    existing_layout = app.game_container.layout()
    if existing_layout is None:
        return  # Safety check
    
    # Clear any existing contents from the layout
    while existing_layout.count():
        item = existing_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
    
    # Set the background color to a nice gradient instead of using a heavy image
    # This will improve performance
    palette = QPalette()
    gradient = QLinearGradient(0, 0, 0, app.game_container.height())
    gradient.setColorAt(0, QColor(30, 50, 100))  # Dark blue at top
    gradient.setColorAt(1, QColor(10, 20, 40))   # Darker blue at bottom
    palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
    app.game_container.setAutoFillBackground(True)
    app.game_container.setPalette(palette)
    
    # Create header with title and temperature
    header_layout = QHBoxLayout()
    
    # Title label
    title_label = QLabel("Connect Four")
    title_label.setObjectName("titleLabel")
    title_label.setStyleSheet("""
        font-size: 28px;
        color: white;
        font-weight: bold;
    """)
    header_layout.addWidget(title_label)
    
    # Spacer to push temperature to the right
    header_layout.addSpacerItem(
        QSpacerItem(40, 20, QSizePolicy.Policy.Expanding,
                   QSizePolicy.Policy.Minimum)
    )
    
    # Temperature display
    temp_display = app.temp_controller.get_display_widget()
    header_layout.addWidget(temp_display)
    
    existing_layout.addLayout(header_layout)
    
    # Create content area
    content_layout = QHBoxLayout()
    
    # Game board frame - stylize to look like the connect4_game_bg.png
    game_frame = QFrame()
    game_frame.setObjectName("gameFrame")
    game_frame.setStyleSheet("""
        #gameFrame {
            background-color: #2c3e50;
            border: 4px solid #3498db;
            border-radius: 10px;
            padding: 15px;
        }
    """)
    
    game_layout = QVBoxLayout(game_frame)
    
    # Create grid for game board
    board_grid = QGridLayout()
    board_grid.setSpacing(5)

    # Create connect four board cells
    for row in range(6):
        for col in range(7):
            cell = QLabel()
            cell.setObjectName(f"cell_{row}_{col}")
            cell.setMinimumSize(QSize(60, 60))
            cell.setMaximumSize(QSize(60, 60))
            cell.setStyleSheet("""
                background-color: #34495e;
                border-radius: 30px;
                border: 2px solid #2c3e50;
            """)
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            board_grid.addWidget(cell, row, col)
            
    # Store board grid in app for later access
    app.board_grid = board_grid
    
    # Add board grid to game layout
    game_layout.addLayout(board_grid)
    
    # Create button grid for user moves
    button_grid = QGridLayout()
    button_grid.setSpacing(5)
    
    # Create buttons for each column (FIXED CONNECTION METHOD)
    for col in range(7):
        button = QPushButton("↓")
        button.setObjectName(f"colButton_{col}")
        button.setMinimumSize(QSize(60, 40))
        button.setMaximumSize(QSize(60, 40))
        apply_button_style(button)
        
        # IMPORTANT FIX: Use direct connection with explicit column number
        # to avoid issues with stale lambda connections
        def create_column_handler(column):
            def on_column_clicked():
                print(f"Direct column handler called for column {column}")
                if hasattr(app, 'input_handler') and app.input_handler is not None:
                    app.input_handler.on_column_selected(column)
            return on_column_clicked
        
        # Connect each button to its dedicated handler function
        button.clicked.connect(create_column_handler(col))
        
        button_grid.addWidget(button, 0, col)
    
    # Store button grid in app for later access
    app.button_grid = button_grid
    
    # Add button grid to game layout
    game_layout.addLayout(button_grid)
    
    # Add game frame to content layout
    content_layout.addWidget(game_frame)
    
    # Create narrative and controls area
    sidebar_layout = QVBoxLayout()
    
    # Create narrative display
    narrative_frame = QFrame()
    narrative_frame.setObjectName("narrativeFrame")
    narrative_frame.setStyleSheet("""
        #narrativeFrame {
            background-color: #2c3e50;
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 10px;
        }
    """)
    
    narrative_layout = QVBoxLayout(narrative_frame)
    
    # Add title for narrative area
    narrative_title = QLabel("Game Narrative")
    narrative_title.setStyleSheet("""
        font-size: 18px;
        color: white;
        font-weight: bold;
        margin-bottom: 5px;
    """)
    narrative_layout.addWidget(narrative_title)
    
    # Create and add narrative display
    narrative_display = NarrativeDisplay()
    message = "Welcome to Connect Four! Make your move by clicking a button."
    narrative_display.set_message(message)
    narrative_layout.addWidget(narrative_display)
    
    # Store narrative display in app for later access
    app.narrative_display = narrative_display
    
    # Add narrative frame to sidebar
    sidebar_layout.addWidget(narrative_frame, 3)
    
    # Create controls area
    controls_frame = QFrame()
    controls_frame.setObjectName("controlsFrame")
    controls_frame.setStyleSheet("""
        #controlsFrame {
            background-color: #2c3e50;
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 10px;
        }
    """)
    
    controls_layout = QVBoxLayout(controls_frame)
    
    # Add title for controls area
    controls_title = QLabel("Game Controls")
    controls_title.setStyleSheet("""
        font-size: 18px;
        color: white;
        font-weight: bold;
        margin-bottom: 5px;
    """)
    controls_layout.addWidget(controls_title)
    
    # Create difficulty control
    difficulty_layout = QHBoxLayout()
    difficulty_label = QLabel("Difficulty:")
    difficulty_label.setStyleSheet("color: white;")
    difficulty_layout.addWidget(difficulty_label)
    
    # Create difficulty combo box
    difficulty_combo = QComboBox()
    difficulty_combo.setObjectName("difficulty_combo")
    difficulty_combo.addItems(["Easy", "Medium", "Hard"])
    difficulty_combo.setCurrentText("Medium")
    difficulty_combo.setStyleSheet("""
        QComboBox {
            background-color: #34495e;
            color: white;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox::drop-down {
            border: 0px;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: white;
            selection-background-color: #3498db;
        }
    """)
    
    # Connect the difficulty combo box to a handler for tracking changes
    if hasattr(app, 'input_handler') and app.input_handler is not None:
        difficulty_combo.currentTextChanged.connect(app.input_handler.on_difficulty_changed)
    
    difficulty_layout.addWidget(difficulty_combo)
    controls_layout.addLayout(difficulty_layout)
    
    # Store the difficulty combo in app for later access
    app.difficulty_combo = difficulty_combo
    
    # Create theme control
    theme_layout = QHBoxLayout()
    theme_label = QLabel("Theme:")
    theme_label.setStyleSheet("color: white;")
    theme_layout.addWidget(theme_label)
    
    # Create theme combo box
    theme_combo = QComboBox()
    theme_combo.setObjectName("theme_combo")
    theme_combo.addItems(["Fantasy", "Sci-Fi"])
    theme_combo.setCurrentText("Fantasy")
    theme_combo.setStyleSheet("""
        QComboBox {
            background-color: #34495e;
            color: white;
            border: 1px solid #3498db;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox::drop-down {
            border: 0px;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #34495e;
            color: white;
            selection-background-color: #3498db;
        }
    """)
    
    # Connect the theme combo box to a handler for tracking changes
    if hasattr(app, 'input_handler') and app.input_handler is not None:
        theme_combo.currentTextChanged.connect(app.input_handler.on_theme_changed)
    
    theme_layout.addWidget(theme_combo)
    controls_layout.addLayout(theme_layout)
    
    # Store the theme combo in app for later access
    app.theme_combo = theme_combo
    
    # Create new game button
    new_game_button = QPushButton("New Game")
    new_game_button.setObjectName("new_game_button")
    apply_button_style(new_game_button)
    
    # Connect to the new game handler
    if hasattr(app, 'input_handler') and app.input_handler is not None:
        new_game_button.clicked.connect(app.input_handler.new_game)
    
    controls_layout.addWidget(new_game_button)
    
    # Store the new game button in app for later access
    app.new_game_button = new_game_button
    # Enable new game button by default
    new_game_button.setEnabled(True)
    
    # Add controls frame to sidebar
    sidebar_layout.addWidget(controls_frame, 1)
    
    # Add sidebar to content layout
    content_layout.addLayout(sidebar_layout)
    
    # Set content layout ratio
    content_layout.setStretch(0, 3)  # Game board
    content_layout.setStretch(1, 2)  # Sidebar
    
    # Add content layout to main layout
    existing_layout.addLayout(content_layout, 1)
    
    # Set margins and spacing for better appearance
    existing_layout.setContentsMargins(10, 10, 10, 10)
    existing_layout.setSpacing(10) 