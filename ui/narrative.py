from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class NarrativeDisplay(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins
        self.setLayout(layout)
        
        # Apply styling
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #333;
                border: 1px solid #ccc;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 5px;
                background-color: rgba(77, 166, 255, 180);
                border-radius: 8px;
            }
        """)
        
        # Add title
        title = QLabel("Game Narrative")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create text display area
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_area.setMinimumHeight(300)
        layout.addWidget(self.text_area, 1)  # 1 = stretch factor
        
        # Add temperature display with improved styling
        self.temp_label = QLabel("CPU Temperature: --°C")
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 150); 
            padding: 5px; 
            border-radius: 5px;
            border: 1px solid #ccc;
        """)
        layout.addWidget(self.temp_label)
    
    def set_text(self, text):
        """Set the narrative text"""
        # Format text with proper line breaks
        formatted_text = "<p style='line-height: 150%;'>" + text.replace('\n', '</p><p style="line-height: 150%;">') + "</p>"
        self.text_area.setHtml(formatted_text)
        # Scroll to the bottom to show latest text
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())
    
    def update_temperature(self, temp):
        """Update the temperature display"""
        # Color code: blue for cool, red for hot
        color = "#FF4500" if temp > 65 else "#4169E1"
        self.temp_label.setText(f"CPU Temperature: <span style='color: {color};'>{temp:.1f}°C</span>") 