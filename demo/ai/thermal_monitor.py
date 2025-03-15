import psutil
import random

class ThermalMonitor:
    def __init__(self, high_temp_threshold=75.0, simulate_temp=True):
        self.high_temp_threshold = high_temp_threshold
        self.simulate_temp = simulate_temp
        self.simulated_temp = 50.0  # Start with normal temperature
        
    def get_cpu_temperature(self):
        """Get the current CPU temperature (or simulate it)"""
        if self.simulate_temp:
            # Randomly adjust simulated temperature for demo purposes
            self.simulated_temp += random.uniform(-1.0, 1.0)
            # Keep within reasonable bounds
            self.simulated_temp = max(40.0, min(90.0, self.simulated_temp))
            return self.simulated_temp
            
        try:
            # Try to get real temperature readings
            temps = psutil.sensors_temperatures()
            if not temps:
                return 50.0  # Default if no sensors found

            # Try to find CPU temperature
            for name, entries in temps.items():
                if name.lower() in ['cpu', 'coretemp', 'k10temp', 'cpu_thermal']:
                    return entries[0].current

            # If specific CPU temp not found, use the max temperature
            return max([temp.current for sublist in temps.values() for temp in sublist])
        except:
            return 50.0  # Default fallback
    
    def is_overheating(self):
        """Check if the system is overheating"""
        return self.get_cpu_temperature() > self.high_temp_threshold 