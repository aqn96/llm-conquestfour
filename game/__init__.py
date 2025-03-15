"""
Game Package for Connect Four

This package contains the core game logic and AI components for the 
Connect Four game, including:

1. ConnectFourGame - The main game logic
2. MinimaxEngine - AI using minimax algorithm with alpha-beta pruning
3. StateValidator - Z3-based game state validator
4. ThermalAwareAI - Temperature-adaptive AI strategy selector
"""

from .connect_four import Player, ConnectFourGame
from .minimax import MinimaxEngine, DepthLimitedMinimax
from .state_validator import StateValidator
from .thermal_aware_ai import ThermalMonitor, ThermalAwareAI

__all__ = [
    'Player',
    'ConnectFourGame',
    'MinimaxEngine',
    'DepthLimitedMinimax',
    'StateValidator',
    'ThermalMonitor',
    'ThermalAwareAI'
] 