"""
Temperature Monitor Module

This module provides temperature monitoring functionality for the Connect Four game.
It allows the game to adapt to high system temperatures by reducing AI complexity.
"""
import os
import platform
import logging
import random
from datetime import datetime


class TemperatureMonitor:
    """
    Monitors system temperature and provides information about thermal state.
    
    This class checks if the system is running hot and allows the application
    to adapt its behavior for optimal performance and system health.
    """
    
    def __init__(self):
        """Initialize the temperature monitor"""
        # Set temperature thresholds (Celsius)
        self.high_temp_threshold = 75.0
        self.critical_temp_threshold = 85.0
        
        # For testing/development, can be set to simulate high temperature
        self.simulated_temp = None
        
        # Temperature history for trending
        self.temp_history = []
        self.max_history_size = 10
    
    def get_temperature(self):
        """
        Get the current CPU temperature
        
        Returns:
            float: The current temperature in Celsius, or None if unavailable
        """
        # If simulated temperature is set, use that
        if self.simulated_temp is not None:
            return self.simulated_temp
        
        # Try to get actual temperature based on platform
        try:
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                # On macOS, use system_profiler or osx-cpu-temp if available
                # This is a simplified implementation that returns a random value
                # In a real implementation, you'd use actual sensors
                temp = random.uniform(40.0, 65.0)
                
            elif system == 'Linux':
                # On Linux, check thermal zones
                # This is a simplified implementation
                temp = random.uniform(40.0, 65.0)
                
            elif system == 'Windows':
                # On Windows, use wmi
                # This is a simplified implementation
                temp = random.uniform(40.0, 65.0)
                
            else:
                # Unknown platform
                logging.warning(f"Unsupported platform for temperature monitoring: {system}")
                return None
                
            # Update temperature history
            self._update_history(temp)
            return temp
            
        except Exception as e:
            logging.error(f"Error getting temperature: {e}")
            return None
    
    def _update_history(self, temp):
        """Update temperature history"""
        self.temp_history.append((datetime.now(), temp))
        if len(self.temp_history) > self.max_history_size:
            self.temp_history.pop(0)
    
    def is_high_temperature(self):
        """
        Check if the system is running at a high temperature
        
        Returns:
            bool: True if temperature is high, False otherwise
        """
        temp = self.get_temperature()
        if temp is None:
            return False
            
        return temp >= self.high_temp_threshold
    
    def is_critical_temperature(self):
        """
        Check if the system is running at a critical temperature
        
        Returns:
            bool: True if temperature is critical, False otherwise
        """
        temp = self.get_temperature()
        if temp is None:
            return False
            
        return temp >= self.critical_temp_threshold
    
    def get_temperature_trend(self):
        """
        Get the temperature trend (rising, falling, stable)
        
        Returns:
            str: 'rising', 'falling', 'stable', or None if not enough data
        """
        if len(self.temp_history) < 2:
            return None
            
        # Get the first and last temperatures
        first_temp = self.temp_history[0][1]
        last_temp = self.temp_history[-1][1]
        
        # Calculate difference
        diff = last_temp - first_temp
        
        # Determine trend
        if abs(diff) < 2.0:
            return 'stable'
        elif diff > 0:
            return 'rising'
        else:
            return 'falling' 