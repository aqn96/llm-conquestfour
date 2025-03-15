"""
Controller for CPU temperature monitoring and display
"""
import random
import platform
import subprocess
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor


class TemperatureController(QObject):
    """Controller for temperature monitoring and display"""
    
    # Signal emitted when temperature changes
    temperature_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.current_temp = 40.0  # Default starting temperature
        self.display_widget = None
        self.is_simulating = False
        self.simulate_step = 0
        self.high_temp_threshold = 75.0  # Temperature threshold for "hot" status
        
    def get_display_widget(self):
        """
        Create and return a widget for displaying temperature
        
        Returns:
            QLabel: A label showing the current temperature
        """
        self.display_widget = QLabel("CPU: 40.0°C")
        self.display_widget.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: #2ecc71;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
        """)
        return self.display_widget
    
    def update_display(self):
        """Update the temperature display with current readings"""
        # Get actual temperature on supported platforms
        if not self.is_simulating:
            self._get_actual_temperature()
        else:
            self._simulate_temperature()
        
        # Update display if widget exists
        if self.display_widget:
            color = self._get_temp_color(self.current_temp)
            self.display_widget.setStyleSheet(f"""
                QLabel {{
                    background-color: #2c3e50;
                    color: {color};
                    border-radius: 5px;
                    padding: 5px 10px;
                    font-weight: bold;
                }}
            """)
            self.display_widget.setText(f"CPU: {self.current_temp:.1f}°C")
            
        # Emit signal
        self.temperature_changed.emit(self.current_temp)
        
    def is_overheating(self):
        """Check if the system is overheating"""
        return self.current_temp > self.high_temp_threshold
            
    def _get_actual_temperature(self):
        """Get the actual CPU temperature on supported platforms"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Use sysctl to get CPU temperature on Mac
            try:
                result = subprocess.run(
                    ["sysctl", "-a"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                for line in result.stdout.split("\n"):
                    if "CPU die temperature" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            try:
                                self.current_temp = float(parts[1].strip())
                                return
                            except ValueError:
                                pass
                # Fallback to simulation if we can't get real temperature
                self._simulate_mild_fluctuation()
            except:
                self._simulate_mild_fluctuation()
                
        elif system == "Linux":
            # Attempt to read from thermal zones on Linux
            try:
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    temp = int(f.read().strip()) / 1000.0  # Convert from millidegrees
                    self.current_temp = temp
                    return
            except:
                self._simulate_mild_fluctuation()
        else:
            # Windows or other platforms - use simulated temp
            self._simulate_mild_fluctuation()
            
    def _simulate_mild_fluctuation(self):
        """Simulate mild temperature fluctuations"""
        # Add some random fluctuation for more realistic visualization
        self.current_temp += random.uniform(-0.5, 0.5)
        # Keep within reasonable bounds
        self.current_temp = max(35.0, min(90.0, self.current_temp))
            
    def _simulate_temperature(self):
        """Simulate a temperature spike for testing UI"""
        if self.simulate_step < 15:
            # Increase temperature
            self.current_temp += 2
        elif self.simulate_step < 30:
            # Decrease temperature
            self.current_temp -= 1.5
        else:
            # Reset simulation
            self.is_simulating = False
            self.simulate_step = 0
            return
            
        self.simulate_step += 1
        
    def _get_temp_color(self, temp):
        """Get a color representing the temperature severity"""
        if temp < 50:
            return "#2ecc71"  # Green - normal
        elif temp < 70:
            return "#f39c12"  # Orange - warm
        else:
            return "#e74c3c"  # Red - hot
            
    def simulate_overheat(self):
        """Begin simulating an overheating event"""
        self.is_simulating = True
        self.simulate_step = 0 