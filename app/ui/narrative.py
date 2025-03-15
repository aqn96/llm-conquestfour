"""
Narrative display component
"""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette


class NarrativeDisplay(QTextEdit):
    """
    A specialized text widget for displaying game narratives
    with stylized text and animations
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure the appearance of the narrative display"""
        # Make read-only - users shouldn't edit the narrative
        self.setReadOnly(True)
        
        # Set text color and styling
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # Configure text edit display properties
        self.setAcceptRichText(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Make slightly transparent to show game background
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(20, 30, 50, 120);
                border: none;
                border-radius: 5px;
                padding: 10px;
                color: #ecf0f1;
                font-size: 14px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 60);
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 70);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Set default text
        self.setPlaceholderText("Game events will be narrated here...")
        
    def set_message(self, message, color=None, bold=False, clear=False):
        """
        Set a new message in the narrative display
        
        Args:
            message: The message text to display
            color: Optional color for the text (hex string or QColor)
            bold: Whether to make the text bold
            clear: Whether to clear previous content
        """
        if clear:
            self.clear()
            
        # Parse color
        color_style = ""
        if color:
            if isinstance(color, str):
                color_style = f"color: {color};"
            elif isinstance(color, QColor):
                color_style = f"color: {color.name()};"
        else:
            color_style = "color: #ecf0f1;"  # Default light text color
            
        # Add bold styling if needed
        bold_start = "<b>" if bold else ""
        bold_end = "</b>" if bold else ""
        
        # Create paragraph with proper spacing
        # Using margin-top and margin-bottom for better separation between messages
        formatted_text = f"""
        <div style="margin-top: 8px; margin-bottom: 12px; {color_style}">
            <p style="margin: 0; padding: 0; line-height: 1.5;">
                {bold_start}{message}{bold_end}
            </p>
        </div>
        """
        
        # If there's existing content, make sure we start on a new block
        doc = self.document()
        if not doc.isEmpty() and not clear:
            # First position the cursor at the end
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
        
        # Append the formatted text
        self.insertHtml(formatted_text)
            
        # Scroll to the bottom to show newest content
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
    def add_narration(self, text, player=None):
        """
        Add a narration segment with optional player attribution
        
        Args:
            text: The narration text
            player: Optional player object or name to attribute this narration to
        """
        if player:
            # If player is passed, format as player speech
            if hasattr(player, 'name'):
                player_name = player.name
            else:
                player_name = str(player)
                
            self.set_message(f"[{player_name}] {text}", 
                            color="#3498db" if player_name == "AI" else "#e74c3c")
        else:
            # Otherwise format as narrator text
            self.set_message(text)
            
    def clear_narrative(self):
        """Clear the narrative display"""
        self.clear() 