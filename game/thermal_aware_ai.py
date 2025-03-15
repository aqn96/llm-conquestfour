"""
Thermal-Aware AI Strategy Selector

This module provides a thermal-aware AI strategy selector that can dynamically
switch between different AI strategies based on system temperature to manage
computational load and prevent overheating.
"""

import psutil
from .minimax import MinimaxEngine, DepthLimitedMinimax


class ThermalMonitor:
    """
    Monitor system temperature and provide information about thermal state.
    """
    
    def __init__(self, high_temp_threshold=75.0):
        """
        Initialize the thermal monitor.
        
        Args:
            high_temp_threshold (float): Temperature threshold in Celsius
                above which the system is considered to be overheating
                (default: 75.0)
        """
        self.high_temp_threshold = high_temp_threshold
    
    def get_cpu_temperature(self):
        """
        Get the current CPU temperature.
        
        Returns:
            float: Current CPU temperature in Celsius, or 0.0 if unavailable
        """
        try:
            # This is platform-dependent and might need different approaches
            # depending on the OS
            temps = psutil.sensors_temperatures()
            if not temps:
                return 0.0
            
            # Try to find CPU temperature (this may vary by system)
            cpu_prefixes = ('cpu', 'core', 'k10temp', 'coretemp')
            for name, entries in temps.items():
                if name.lower().startswith(cpu_prefixes):
                    # Return the maximum temperature of all CPU cores
                    return max(entry.current for entry in entries)
            
            # If we can't find a CPU temperature, use the highest temperature
            # from any available sensor
            return max(
                entry.current for sublist in temps.values() 
                for entry in sublist
            )
        except Exception:
            return 0.0  # Default if we can't get the temperature
    
    def is_overheating(self):
        """
        Check if the system is overheating.
        
        Returns:
            bool: True if the system temperature is above the threshold,
                  False otherwise
        """
        return self.get_cpu_temperature() > self.high_temp_threshold


class ThermalAwareAI:
    """
    AI strategy selector that adapts based on system temperature.
    This class implements the core thermal adaptation strategy from the
    project proposal, switching between full and limited AI depending
    on temperature.
    """
    
    def __init__(
        self, 
        high_temp_threshold=75.0, 
        standard_depth=4, 
        limited_depth=2
    ):
        """
        Initialize the thermal-aware AI.
        
        Args:
            high_temp_threshold (float): Temperature threshold in Celsius
                (default: 75.0)
            standard_depth (int): Search depth for normal temperature
                (default: 4)
            limited_depth (int): Reduced search depth for high temperature
                (default: 2)
        """
        self.thermal_monitor = ThermalMonitor(high_temp_threshold)
        self.standard_ai = MinimaxEngine(max_depth=standard_depth)
        self.limited_ai = DepthLimitedMinimax(max_depth=limited_depth)
    
    def select_strategy(self):
        """
        Select the appropriate AI strategy based on current temperature.
        
        Returns:
            MinimaxEngine: The selected AI strategy
        """
        if self.thermal_monitor.is_overheating():
            print("System temperature high, using limited AI strategy")
            return self.limited_ai
        else:
            return self.standard_ai
    
    def find_best_move(self, game):
        """
        Find the best move for the current player, using the appropriate
        AI strategy based on current system temperature.
        
        Args:
            game (ConnectFourGame): The current game state
            
        Returns:
            int: The column index of the best move
        """
        strategy = self.select_strategy()
        return strategy.find_best_move(game)
    
    def get_current_temperature(self):
        """
        Get the current system temperature.
        
        Returns:
            float: Current temperature in Celsius
        """
        return self.thermal_monitor.get_cpu_temperature() 