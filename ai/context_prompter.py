import os
from jinja2 import Environment, FileSystemLoader
import random
from game.connect_four import Player

class ContextAwarePrompter:
    def __init__(self, template_path="templates/"):
        # Ensure the templates directory exists
        os.makedirs(template_path, exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_default_templates(template_path)
        
        # Set up Jinja environment
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.templates = {
            "fantasy": self.env.get_template("fantasy.jinja2"),
            "scifi": self.env.get_template("scifi.jinja2"),
            "sci-fi": self.env.get_template("scifi.jinja2")  # Add hyphenated alias
        }

    def _create_default_templates(self, path):
        """Create default templates if they don't exist"""
        fantasy_path = os.path.join(path, "fantasy.jinja2")
        scifi_path = os.path.join(path, "scifi.jinja2")
        
        if not os.path.exists(fantasy_path):
            with open(fantasy_path, 'w') as f:
                f.write("""{% if move_count < 5 %}
The battle has just begun on the Crystal Grid. The {{ faction }} consider their next move carefully.
{% elif move_count < 15 %}
As the conflict intensifies, the {{ faction }} prepare to {{ action }} in Column {{ next_column }}.
{% if last_move %}
Previously: {{ last_move.faction }} placed their crystal in column {{ last_move.column }}, creating a powerful resonance.
{% endif %}
{% else %}
The Crystal Grid pulses with energy as the final confrontation approaches. The {{ faction }} must choose wisely.
{% endif %}

Suggest a strategic move for the {{ faction }} that balances offense and storytelling impact.
""")
                
        if not os.path.exists(scifi_path):
            with open(scifi_path, 'w') as f:
                f.write("""{% if move_count < 5 %}
Quantum initialization sequence began. The {{ faction }} calculating optimal trajectory.
{% elif move_count < 15 %}
Neural network analysis suggests the {{ faction }} should {{ action }} in Sector {{ next_column }}.
{% if last_move %}
Previous action: {{ last_move.faction }} deployed a quantum token in sector {{ last_move.column }}, altering the probability field.
{% endif %}
{% else %}
Quantum field instability critical. The {{ faction }} must execute precise particle placement to prevent dimensional collapse.
{% endif %}

Calculate the optimal strategic move for the {{ faction }} considering both tactical advantage and narrative momentum.
""")

    def create_prompt(self, game_state, theme="fantasy", last_move=None):
        """Create a context-aware prompt based on game state"""
        template = self.templates[theme]
        
        # Count moves (non-zero cells)
        move_count = sum(1 for row in game_state.board for cell in row if cell != 0)
        
        # Determine faction name based on current player
        current_player_value = game_state.current_player.value if hasattr(game_state.current_player, 'value') else game_state.current_player
        
        faction = "Crystal Lords" if current_player_value == 1 else "Shadow Keepers"
        if theme == "scifi":
            faction = "Quantum Collective" if current_player_value == 1 else "Void Syndicate"
        
        # Analyze the board for strategic context
        threats = self._detect_threats(game_state.board, current_player_value)
        opportunities = self._detect_opportunities(game_state.board, current_player_value)
        
        # Select an action based on game state and analysis
        action = self._select_action(threats, opportunities)
        
        # Find a possible next column based on strategy
        next_column = self._suggest_strategic_column(game_state, threats, opportunities)
        
        # Create game phase description
        game_phase = self._determine_game_phase(move_count)
        
        context = {
            "board": game_state.board,
            "current_player": current_player_value,
            "last_move": last_move,
            "move_count": move_count,
            "faction": faction,
            "action": action,
            "next_column": next_column,
            "game_phase": game_phase,
            "threats": threats,
            "opportunities": opportunities
        }
        
        return template.render(**context)
    
    def _detect_threats(self, board, player):
        """Detect potential threats (opponent about to win)"""
        # Simple threat detection - count opponent pieces in rows/columns/diagonals
        # Ensure player is an integer
        player_value = player.value if hasattr(player, 'value') else player
        opponent = 3 - player_value  # Assuming player is 1 or 2
        threats = []
        
        # Check for 3-in-a-row threats
        # This is a simplified version - a real implementation would be more thorough
        for row in range(len(board)):
            for col in range(len(board[0]) - 3):
                window = [board[row][col+i] for i in range(4)]
                if window.count(opponent) == 3 and window.count(0) == 1:
                    threats.append({"type": "horizontal", "severity": "high"})
        
        # More threat detection would go here
        
        return threats
    
    def _detect_opportunities(self, board, player):
        """Detect potential winning opportunities"""
        # Simple opportunity detection - count player pieces in rows/columns/diagonals
        # Ensure player is an integer
        player_value = player.value if hasattr(player, 'value') else player
        opportunities = []
        
        # Check for 3-in-a-row opportunities
        # This is a simplified version - a real implementation would be more thorough
        for row in range(len(board)):
            for col in range(len(board[0]) - 3):
                window = [board[row][col+i] for i in range(4)]
                if window.count(player_value) == 3 and window.count(0) == 1:
                    opportunities.append({"type": "horizontal", "value": "high"})
        
        # More opportunity detection would go here
        
        return opportunities
    
    def _select_action(self, threats, opportunities):
        """Select an appropriate action based on game analysis"""
        if opportunities and any(o["value"] == "high" for o in opportunities):
            actions = ["seize victory", "execute a winning move", "claim triumph", "secure dominance"]
        elif threats and any(t["severity"] == "high" for t in threats):
            actions = ["block a threat", "defend against attack", "counter the opposition", "prevent defeat"]
        else:
            actions = ["advance their strategy", "strengthen their position", "develop their formation", "prepare an attack"]
        
        return random.choice(actions)
    
    def _suggest_strategic_column(self, game_state, threats, opportunities):
        """Suggest a strategic column based on game analysis"""
        # In a real implementation, this would use the threats and opportunities
        # to suggest a strategic column. For now, we'll just pick a valid column.
        valid_columns = []
        for col in range(len(game_state.board[0])):
            # Check if column is not full
            if game_state.board[0][col] == 0:
                valid_columns.append(col)
        
        return random.choice(valid_columns) if valid_columns else 3
    
    def _determine_game_phase(self, move_count):
        """Determine the current phase of the game"""
        if move_count < 10:
            return "opening"
        elif move_count < 25:
            return "midgame"
        else:
            return "endgame" 