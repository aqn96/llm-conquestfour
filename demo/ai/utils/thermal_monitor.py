"""
Thermal Monitoring Utility - Monitor system temperature on various platforms
"""
import logging
import os
import platform
import subprocess
import time
from typing import Dict, Optional, Tuple


class ThermalMonitor:
    """
    A utility to monitor system temperature.
    
    This class provides methods to check CPU and GPU temperatures
    on various platforms (macOS, Linux, Windows).
    """
    
    def __init__(self):
        """Initialize the thermal monitor."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.system = platform.system().lower()
        self.last_check_time = 0
        self.temperature_cache = {}
        self.check_interval = 5  # seconds
    
    def get_temperature(self, force_check: bool = False) -> Dict[str, float]:
        """
        Get the current system temperature.
        
        Args:
            force_check: Force a temperature check even if cache is recent
            
        Returns:
            Dict: Dictionary with temperature values for CPU and/or GPU
        """
        current_time = time.time()
        
        # Use cache if available and recent, unless forced
        if (not force_check and 
            self.temperature_cache and 
            current_time - self.last_check_time < self.check_interval):
            return self.temperature_cache
        
        temperatures = {}
        
        # Get temperatures based on platform
        if self.system == "darwin":  # macOS
            temps = self._get_mac_temperatures()
            temperatures.update(temps)
        elif self.system == "linux":
            temps = self._get_linux_temperatures()
            temperatures.update(temps)
        elif self.system == "windows":
            temps = self._get_windows_temperatures()
            temperatures.update(temps)
        else:
            self.logger.warning(f"Unsupported platform: {self.system}")
        
        # Update cache
        self.temperature_cache = temperatures
        self.last_check_time = current_time
        
        return temperatures
    
    def _get_mac_temperatures(self) -> Dict[str, float]:
        """
        Get temperature on macOS using powermetrics.
        
        Returns:
            Dict: Dictionary with temperature values
        """
        temps = {}
        
        try:
            # Try to run powermetrics to get temperature data
            cmd = ["powermetrics", "-s", "thermal", "-n", "1"]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=3
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse CPU die temperature
                if "CPU die temperature" in output:
                    for line in output.split('\n'):
                        if "CPU die temperature" in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                temp_str = parts[1].strip().split()[0]
                                temps["cpu"] = float(temp_str)
                                break
                
                # Parse GPU temperature if available
                if "GPU die temperature" in output:
                    for line in output.split('\n'):
                        if "GPU die temperature" in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                temp_str = parts[1].strip().split()[0]
                                temps["gpu"] = float(temp_str)
                                break
            else:
                self.logger.warning("Failed to run powermetrics")
                
        except (subprocess.SubprocessError, ValueError, IndexError) as e:
            self.logger.error(f"Error getting Mac temperatures: {e}")
        
        return temps
    
    def _get_linux_temperatures(self) -> Dict[str, float]:
        """
        Get temperature on Linux using sensors command.
        
        Returns:
            Dict: Dictionary with temperature values
        """
        temps = {}
        
        try:
            # Check if sensors command is available
            if subprocess.run(
                ["which", "sensors"], 
                capture_output=True
            ).returncode == 0:
                # Run sensors command
                result = subprocess.run(
                    ["sensors"], 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    # Parse CPU temperature
                    if "Core 0" in output:
                        for line in output.split('\n'):
                            if "Core 0" in line and "+" in line:
                                parts = line.split('+')
                                if len(parts) >= 2:
                                    temp_str = parts[1].split('°')[0]
                                    temps["cpu"] = float(temp_str)
                                    break
                    
                    # Parse GPU temperature if nvidia-smi is available
                    if subprocess.run(
                        ["which", "nvidia-smi"], 
                        capture_output=True
                    ).returncode == 0:
                        gpu_result = subprocess.run(
                            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"], 
                            capture_output=True, 
                            text=True
                        )
                        
                        if gpu_result.returncode == 0:
                            gpu_temp = gpu_result.stdout.strip()
                            if gpu_temp:
                                temps["gpu"] = float(gpu_temp)
                
        except (subprocess.SubprocessError, ValueError, IndexError) as e:
            self.logger.error(f"Error getting Linux temperatures: {e}")
        
        return temps
    
    def _get_windows_temperatures(self) -> Dict[str, float]:
        """
        Get temperature on Windows.
        
        Returns:
            Dict: Dictionary with temperature values
        """
        temps = {}
        
        try:
            # On Windows, we'd need to use WMI or a third-party tool
            # This is a simplified placeholder
            self.logger.warning("Windows temperature monitoring not fully implemented")
            
        except Exception as e:
            self.logger.error(f"Error getting Windows temperatures: {e}")
        
        return temps
    
    def is_system_too_hot(self, threshold: float = 85.0) -> Tuple[bool, float]:
        """
        Check if the system is too hot.
        
        Args:
            threshold: Temperature threshold in Celsius
            
        Returns:
            Tuple: (is_too_hot, max_temperature)
        """
        temps = self.get_temperature()
        
        if not temps:
            return False, 0.0
        
        max_temp = max(temps.values()) if temps else 0.0
        is_too_hot = max_temp > threshold
        
        if is_too_hot:
            self.logger.warning(f"System temperature ({max_temp}°C) exceeds threshold ({threshold}°C)")
        
        return is_too_hot, max_temp
    
    def get_temperature_str(self) -> str:
        """
        Get a formatted string with current temperatures.
        
        Returns:
            str: Formatted temperature string
        """
        temps = self.get_temperature()
        
        if not temps:
            return "Temperature: Unknown"
        
        parts = []
        for device, temp in temps.items():
            parts.append(f"{device.upper()}: {temp:.1f}°C")
        
        return "Temperature: " + ", ".join(parts) 