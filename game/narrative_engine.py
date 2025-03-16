"""
Narrative Engine Module for Connect Four

This module evaluates player moves and generates appropriate narrative prompts
for a local LLM based on move quality. It creates an immersive storytelling
experience that evolves with gameplay.
"""

import copy
from game.connect_four import Player, ConnectFourGame
from game.minimax import MinimaxEngine


class MoveEvaluator:
    """
    Evaluates the quality of player moves in Connect Four.
    
    This class uses a minimax-based approach to determine if a move is good,
    mediocre, or bad, by comparing it to the optimal move the AI would make.
    """
    
    def __init__(self, evaluation_depth=4):
        """
        Initialize the move evaluator.
        
        Args:
            evaluation_depth (int): Depth for minimax evaluation (default: 4)
        """
        self.minimax_engine = MinimaxEngine(max_depth=evaluation_depth)
        
    def evaluate_move(self, game, column):
        """
        Evaluate the quality of a player's move.
        
        Args:
            game (ConnectFourGame): The game state before the move
            column (int): The column where the player placed their piece
            
        Returns:
            str: 'good', 'mediocre', or 'bad' based on move quality
        """
        # Create a copy of the game to avoid modifying the original
        game_copy = game.copy()
        
        # Find the best move according to minimax
        best_move = self.minimax_engine.find_best_move(game_copy)
        
        # Get all possible moves and rank them
        valid_moves = game_copy.get_valid_columns()
        move_scores = []
        
        for col in valid_moves:
            col_game_copy = game_copy.copy()
            col_game_copy.make_move(col)
            
            # For player's moves, we evaluate from the perspective of Player.ONE
            score = self._evaluate_position(col_game_copy, Player.ONE)
            move_scores.append((col, score))
        
        # Sort moves by score (best first)
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Determine move quality by its rank
        if not move_scores:
            return 'mediocre'  # No valid moves
            
        top_score = move_scores[0][1]
        player_score = next((score for col, score in move_scores if col == column), None)
        
        if player_score is None:
            return 'mediocre'  # Invalid move
            
        # Calculate relative quality as a percentage of the best move
        if top_score <= 0:
            # If all moves are bad, consider defensive plays
            quality_ratio = 1.0 if player_score == top_score else 0.0
        else:
            quality_ratio = player_score / top_score if top_score > 0 else 0.0
        
        # Classify move quality
        if quality_ratio >= 0.9:
            return 'good'
        elif quality_ratio >= 0.5:
            return 'mediocre'
        else:
            return 'bad'
    
    def _evaluate_position(self, game, player):
        """
        Evaluate the board position for the given player.
        
        Args:
            game (ConnectFourGame): The game state to evaluate
            player (Player): The player perspective (Player.ONE or Player.TWO)
            
        Returns:
            float: A score for the position
        """
        # Check if this is a winning position
        winner = game.check_win()
        if winner == player:
            return 1000.0
        elif winner is not None:
            return -1000.0
        
        # Use the minimax engine's position evaluation
        return self.minimax_engine._score_position(game.board, player)
    
    def get_move_insight(self, game, column, move_quality):
        """
        Get strategic insight about the move for narrative generation.
        
        Args:
            game (ConnectFourGame): The game state
            column (int): The column where the player placed their piece
            move_quality (str): The evaluated quality ('good', 'mediocre', 'bad')
            
        Returns:
            dict: Context information about the move for narrative generation
        """
        game_copy = game.copy()
        
        # Check if this creates any threats
        threats_created = self._count_threats(game_copy, column)
        
        # Check if this blocks any opponent threats
        blocks = self._check_blocking_move(game_copy, column)
        
        # Check if this is a center column (strategically valuable)
        is_center = (column == game.cols // 2)
        
        # Check if this move enables a future win
        enables_win = self._enables_future_win(game_copy, column)
        
        # Check if this is a setup for a trap (multiple threats)
        creates_trap = self._creates_trap(game_copy, column)
        
        return {
            'quality': move_quality,
            'column': column,
            'threats_created': threats_created,
            'blocks_opponent': blocks,
            'is_center': is_center,
            'enables_win': enables_win,
            'creates_trap': creates_trap
        }
    
    def _count_threats(self, game, column):
        """Count how many threats are created by this move."""
        threats = 0
        game_copy = game.copy()
        
        # Find the row where the piece was placed
        row = None
        for r in range(game.rows - 1, -1, -1):
            if game.board[r][column] == 0:
                row = r
                break
                
        if row is None:
            return 0
            
        # Simulate the move
        game_copy.make_move(column)
        
        # Check if we now have any three-in-a-row situations
        # with an open space (threat)
        player = 3 - game_copy.current_player.value  # The player who just moved
        
        # Check in all directions
        directions = [
            [(0, 1), (0, -1)],  # Horizontal
            [(1, 0), (-1, 0)],  # Vertical
            [(1, 1), (-1, -1)],  # Diagonal /
            [(1, -1), (-1, 1)]   # Diagonal \
        ]
        
        for dir_pair in directions:
            count = 1  # Count the placed piece
            for dx, dy in dir_pair:
                x, y = row + dx, column + dy
                streak = 0
                while (0 <= x < game.rows and 0 <= y < game.cols and 
                       game_copy.board[x][y] == player):
                    count += 1
                    x += dx
                    y += dy
            
            # Check if this direction has a threat
            if count == 3:
                # Check if there's an open space at either end
                for dx, dy in dir_pair:
                    x, y = row + dx * 3, column + dy * 3
                    if (0 <= x < game.rows and 0 <= y < game.cols and 
                        game_copy.board[x][y] == 0):
                        threats += 1
        
        return threats
    
    def _check_blocking_move(self, game, column):
        """Check if this move blocks an opponent's threat."""
        game_copy = game.copy()
        opponent = game.current_player.value
        
        # Simulate the opponent making a move in this column
        if not game_copy.is_valid_move(column):
            return False
            
        # Find the row where the piece would be placed
        row = game_copy.get_next_open_row(column)
        if row == -1:
            return False
            
        # Temporarily place opponent's piece
        game_copy.board[row][column] = opponent
        
        # Check if this would create a win for the opponent
        # (if so, then the player's move is blocking this win)
        
        # Check horizontal
        for c in range(max(0, column - 3), min(column + 4, game.cols - 3)):
            window = [game_copy.board[row][c + i] for i in range(4)]
            if window.count(opponent) == 4:
                return True
                
        # Check vertical
        if row <= game.rows - 4:
            window = [game_copy.board[row + i][column] for i in range(4)]
            if window.count(opponent) == 4:
                return True
                
        # Check diagonal (positive slope)
        for r, c in zip(range(max(0, row - 3), min(row + 4, game.rows - 3)),
                       range(max(0, column - 3), min(column + 4, game.cols - 3))):
            window = [game_copy.board[r + i][c + i] for i in range(4)]
            if window.count(opponent) == 4:
                return True
                
        # Check diagonal (negative slope)
        for r, c in zip(range(min(game.rows - 1, row + 3), max(row - 4, -1), -1),
                       range(max(0, column - 3), min(column + 4, game.cols - 3))):
            window = [game_copy.board[r - i][c + i] for i in range(4)]
            if window.count(opponent) == 4:
                return True
                
        return False
    
    def _enables_future_win(self, game, column):
        """Check if this move enables a win in the next move."""
        game_copy = game.copy()
        
        # Make the player's move
        if not game_copy.make_move(column):
            return False
            
        # Now it's the opponent's turn - switch back to the player
        game_copy.current_player = Player.ONE
        
        # Check if any move would create a win for the player
        for col in game_copy.get_valid_columns():
            test_copy = game_copy.copy()
            test_copy.make_move(col)
            if test_copy.check_win() == Player.ONE:
                return True
                
        return False
    
    def _creates_trap(self, game, column):
        """Check if this move creates a 'trap' (multiple threats)."""
        game_copy = game.copy()
        
        # Make the player's move
        if not game_copy.make_move(column):
            return False
            
        # Now it's the opponent's turn - simulate their defense
        
        # For each possible opponent move, check if the player still has a winning move
        winning_paths = 0
        for opp_col in game_copy.get_valid_columns():
            opp_copy = game_copy.copy()
            opp_copy.make_move(opp_col)
            
            # Switch back to player and check for winning moves
            opp_copy.current_player = Player.ONE
            has_winning_move = False
            
            for player_col in opp_copy.get_valid_columns():
                player_copy = opp_copy.copy()
                player_copy.make_move(player_col)
                if player_copy.check_win() == Player.ONE:
                    has_winning_move = True
                    winning_paths += 1
                    break
                    
        # If there are multiple ways to win, it's a trap
        return winning_paths >= 2


class NarrativePromptGenerator:
    """
    Generates narrative prompts for an LLM based on Connect Four game state
    and move evaluation.
    """
    
    def __init__(self):
        """Initialize the narrative prompt generator."""
        self.move_evaluator = MoveEvaluator()
        self.theme_templates = {
            'fantasy': self._fantasy_templates(),
            'scifi': self._scifi_templates()
        }
        
    def generate_prompt(self, game, column, theme='fantasy'):
        """
        Generate a narrative prompt based on the player's move.
        
        Args:
            game (ConnectFourGame): The current game state
            column (int): The column where the player placed their piece
            theme (str): The narrative theme ('fantasy' or 'scifi')
            
        Returns:
            str: A prompt for the LLM to generate a narrative response
        """
        # Evaluate the move quality
        move_quality = self.move_evaluator.evaluate_move(game, column)
        
        # Get strategic insights for this move
        insights = self.move_evaluator.get_move_insight(game, column, move_quality)
        
        # Select the appropriate template based on theme and move quality
        if theme not in self.theme_templates:
            theme = 'fantasy'  # Default to fantasy if theme not found
            
        templates = self.theme_templates[theme]
        template = templates[move_quality]
        
        # Format the template with game state and insights
        faction_name = self._get_faction_name(game, theme)
        opponent_name = self._get_opponent_faction_name(game, theme)
        
        context = {
            'faction': faction_name,
            'opponent': opponent_name,
            'column': column + 1,  # Convert to 1-indexed for narrative
            'move_number': game.move_count,
            'blocks_opponent': insights['blocks_opponent'],
            'creates_threat': insights['threats_created'] > 0,
            'creates_trap': insights['creates_trap'],
            'is_center': insights['is_center']
        }
        
        return self._format_template(template, context)
    
    def _format_template(self, template, context):
        """Format a template string with the provided context."""
        # Simple placeholder replacement
        result = template
        for key, value in context.items():
            placeholder = '{' + key + '}'
            if placeholder in result:
                result = result.replace(placeholder, str(value))
                
        return result
    
    def _get_faction_name(self, game, theme):
        """Get the appropriate faction name based on theme."""
        if game.current_player == Player.ONE:
            return self._player_factions(theme)[0]
        else:
            return self._player_factions(theme)[1]
    
    def _get_opponent_faction_name(self, game, theme):
        """Get the opponent faction name based on theme."""
        if game.current_player == Player.ONE:
            return self._player_factions(theme)[1]
        else:
            return self._player_factions(theme)[0]
    
    def _player_factions(self, theme):
        """Get faction names for both players based on theme."""
        if theme == 'fantasy':
            return ['Crystal Kingdom', 'Shadow Empire']
        elif theme == 'scifi':
            return ['Quantum Alliance', 'Neural Collective']
        else:
            return ['Player 1', 'Player 2']
    
    def _fantasy_templates(self):
        """Create templates for fantasy theme."""
        return {
            'good': [
                "The {faction} makes a masterful move, placing their crystal in column {column}. "
                "This strategic placement radiates power across the Crystal Grid, creating new "
                "pathways of magical energy that threaten the {opponent}'s position. "
                "The battlefield shimmers with anticipation as the {faction} seizes the advantage. "
                "\n\nGenerate a detailed and vivid description of this powerful move from the {faction}'s "
                "perspective, emphasizing their growing strength and strategic brilliance.",
                
                "With unerring precision, the {faction} commander directs a crystal shard into "
                "column {column}, blocking the {opponent}'s magical convergence. The tactical "
                "brilliance of this maneuver sends ripples through the arcane battlefield, "
                "as mystic energies realign in the {faction}'s favor. "
                "\n\nDescribe this masterful defensive play and how it disrupts the {opponent}'s "
                "plans while strengthening the {faction}'s position in the Crystal War."
            ],
            
            'mediocre': [
                "The {faction} places a crystal in column {column}, a cautious move that "
                "neither greatly strengthens their position nor significantly weakens their opponent's. "
                "The Crystal Grid hums steadily, waiting for more decisive actions. "
                "\n\nGenerate a description of this balanced but unremarkable move, showing "
                "the {faction}'s careful consideration but lack of aggressive strategy.",
                
                "Column {column} receives a crystal from the {faction}, a conventional deployment "
                "that maintains the current balance of power. While not advancing their position "
                "dramatically, it does establish a foundation for future maneuvers. "
                "\n\nDescribe this standard tactical move and how the {faction} is being cautious "
                "but prepared in their ongoing battle with the {opponent}."
            ],
            
            'bad': [
                "The {faction} hesitantly places a crystal in column {column}, a move that "
                "reveals a concerning lack of foresight. The magical energies of the Crystal Grid "
                "seem to dim around their formation, while the {opponent} positions pulse with "
                "renewed vigor. "
                "\n\nGenerate a description of this strategic misstep and the advantage it gives "
                "to the {opponent}, portraying the {faction}'s uncertainty and the consequences "
                "of their error.",
                
                "With apparent confusion, the {faction} directs a crystal into column {column}, "
                "overlooking the tactical vulnerability this creates. The {opponent}'s crystals "
                "seem to resonate more strongly, sensing the weakness in their adversary's formation. "
                "\n\nDescribe this tactical blunder and how the {opponent} might capitalize on this "
                "mistake, showing the {faction}'s growing concern as they realize their error."
            ]
        }
    
    def _scifi_templates(self):
        """Create templates for sci-fi theme."""
        return {
            'good': [
                "The {faction} executes a calculated protocol, deploying a quantum node to "
                "column {column}. This precision maneuver optimizes their network topology, "
                "creating multiple data pathways that threaten to overrun the {opponent}'s defenses. "
                "The battle grid illuminates with cascading probability waves. "
                "\n\nGenerate a technical yet dramatic description of this optimal strategic "
                "algorithm from the {faction}'s perspective, emphasizing the mathematical "
                "perfection of their approach.",
                
                "With algorithmic precision, the {faction} deploys a node to column {column}, "
                "effectively countering the {opponent}'s emerging network pattern. The holographic "
                "battlefield reconfigures as probability matrices shift heavily toward {faction} "
                "victory scenarios. "
                "\n\nDescribe this masterful counter-protocol and how it disrupts the {opponent}'s "
                "processing while strengthening the {faction}'s position in the data war."
            ],
            
            'mediocre': [
                "The {faction} allocates a quantum node to column {column}, a standard protocol "
                "that maintains system stability without significantly altering the battle parameters. "
                "The grid continues processing at expected efficiency rates. "
                "\n\nGenerate a description of this mathematically sound but uninspired move, showing "
                "the {faction}'s computational caution but lack of innovative algorithms.",
                
                "Column {column} receives a {faction} quantum node, a statistically neutral deployment "
                "that preserves current probability distributions. While not maximizing their position, "
                "it maintains sufficient processing capacity for subsequent operations. "
                "\n\nDescribe this standard protocol execution and how the {faction} is processing "
                "within expected parameters in their ongoing conflict with the {opponent}."
            ],
            
            'bad': [
                "The {faction} hesitantly deploys a quantum node to column {column}, a "
                "processing error that introduces instability into their network. The holographic "
                "battlefield flickers as probability calculations shift favorably toward the {opponent}'s "
                "victory conditions. "
                "\n\nGenerate a description of this algorithmic failure and the computational advantage "
                "it provides to the {opponent}, portraying the {faction}'s system diagnostics and "
                "the cascading errors this may cause.",
                
                "With apparent logic fragmentation, the {faction} allocates resources to column {column}, "
                "overlooking critical vulnerability vectors this creates. The {opponent}'s systems "
                "immediately begin calculating exploitation pathways through the weakened defenses. "
                "\n\nDescribe this tactical processing error and how the {opponent} might exploit this "
                "system vulnerability, showing the {faction}'s emergency diagnostics as they detect "
                "their mistake."
            ]
        }
    
    def get_random_template(self, templates_dict, quality):
        """Get a random template from the available ones for a quality."""
        import random
        templates = templates_dict[quality]
        return random.choice(templates)


class GameNarrator:
    """
    High-level class that integrates move evaluation and narrative generation
    with local LLM integration.
    """
    
    def __init__(self, theme='fantasy'):
        """
        Initialize the game narrator.
        
        Args:
            theme (str): Narrative theme ('fantasy' or 'scifi')
        """
        self.prompt_generator = NarrativePromptGenerator()
        self.theme = theme
        self.move_history = []
        
    def set_theme(self, theme):
        """
        Set the narrative theme.
        
        Args:
            theme (str): The theme to use ('fantasy' or 'scifi')
        """
        self.theme = theme
        
    def generate_move_narrative(self, game, column):
        """
        Generate a narrative prompt for the player's move.
        
        Args:
            game (ConnectFourGame): The current game state
            column (int): The column where the player placed their piece
            
        Returns:
            str: A prompt for the LLM to generate a narrative response
        """
        # Record move for history context
        move_quality = self.prompt_generator.move_evaluator.evaluate_move(game, column)
        self.move_history.append((column, move_quality))
        
        # Generate the prompt
        prompt = self.prompt_generator.generate_prompt(game, column, self.theme)
        
        return prompt
    
    def generate_game_start_prompt(self, theme=None):
        """
        Generate a prompt for the beginning of the game.
        
        Args:
            theme (str, optional): Override the current theme
            
        Returns:
            str: A prompt for the LLM to generate a game introduction
        """
        theme = theme or self.theme
        
        if theme == 'fantasy':
            return (
                "Two ancient kingdoms vie for control of the Crystal Grid, a magical battlefield "
                "where power flows through aligned crystals. The Crystal Kingdom, masters of light and order, "
                "face the Shadow Empire, wielders of darkness and chaos. As the battle begins, both sides "
                "prepare to place their mystical crystals, knowing that four aligned will channel enough "
                "power to overwhelm their enemy.\n\n"
                "Generate an epic introduction to this magical conflict, describing the two factions, "
                "the Crystal Grid battlefield, and the tension as the first move is about to be made."
            )
        elif theme == 'scifi':
            return (
                "In the digital battlespace of Nexus-7, two advanced AI collectives compete for "
                "computational dominance. The Quantum Alliance, champions of deterministic algorithms, "
                "face the Neural Collective, masters of emergent intelligence. Victory requires establishing "
                "a four-node quantum link, creating an unbreakable processing chain that will grant "
                "control of the entire network.\n\n"
                "Generate a technologically rich introduction to this digital conflict, describing the two "
                "factions, the Nexus-7 battlefield, and the analytical tension as the first move is calculated."
            )
        else:
            return (
                "Two players face off in an intense battle of strategy and foresight. "
                "The objective: connect four pieces in a row - horizontally, vertically, or diagonally - "
                "before your opponent. Each move brings new possibilities and dangers.\n\n"
                "Generate an engaging introduction to this classic game of strategy, "
                "highlighting the anticipation as the players prepare to make their first moves."
            )
    
    def generate_victory_prompt(self, winner, theme=None):
        """
        Generate a prompt for the end of the game.
        
        Args:
            winner (Player): The winning player
            theme (str, optional): Override the current theme
            
        Returns:
            str: A prompt for the LLM to generate a victory narrative
        """
        theme = theme or self.theme
        
        if theme == 'fantasy':
            faction = 'Crystal Kingdom' if winner == Player.ONE else 'Shadow Empire'
            return (
                f"The {faction} has achieved victory! Four mystical crystals align perfectly, "
                "channeling overwhelming magical energy across the Crystal Grid. The defeated "
                "opponent's formations crumble as the battlefield resonates with the victor's power.\n\n"
                f"Generate an epic conclusion to the battle, describing how the {faction} achieved "
                "their victory, the magical energies unleashed by their aligned crystals, and the "
                "implications of their triumph in the ongoing Crystal War."
            )
        elif theme == 'scifi':
            faction = 'Quantum Alliance' if winner == Player.ONE else 'Neural Collective'
            return (
                f"The {faction} has achieved computational dominance! Four quantum nodes form a "
                "perfect processing chain, exponentially amplifying their algorithms throughout "
                "the Nexus-7 network. The opponent's systems rapidly degrade as the victor's "
                "protocols propagate.\n\n"
                f"Generate a technically rich conclusion to the battle, describing how the {faction} "
                "achieved their victory, the computational breakthrough enabled by their node alignment, "
                "and the implications of their control over the network."
            )
        else:
            player = 'Player 1' if winner == Player.ONE else 'Player 2'
            return (
                f"{player} has won the game! By connecting four pieces in a row, they've "
                "demonstrated superior strategy and foresight.\n\n"
                f"Generate a satisfying conclusion to the match, describing {player}'s "
                "winning move, their strategy throughout the game, and the excitement "
                "of their victory."
            )
    
    def generate_draw_prompt(self, theme=None):
        """
        Generate a prompt for a draw game.
        
        Args:
            theme (str, optional): Override the current theme
            
        Returns:
            str: A prompt for the LLM to generate a draw narrative
        """
        theme = theme or self.theme
        
        if theme == 'fantasy':
            return (
                "The Crystal Grid has reached equilibrium! Neither the Crystal Kingdom nor "
                "the Shadow Empire could establish dominance, and now the battlefield is completely "
                "filled with interlocking crystal formations that pulse with contained power.\n\n"
                "Generate a conclusion to this perfectly balanced magical conflict, describing how "
                "both sides must now retreat and reconsider their strategies for the next battle."
            )
        elif theme == 'scifi':
            return (
                "Nexus-7 has reached processing saturation! Neither the Quantum Alliance nor "
                "the Neural Collective could establish a dominant processing chain, and now "
                "the network is completely filled with interconnected nodes that calculate "
                "endlessly without resolution.\n\n"
                "Generate a conclusion to this computational stalemate, describing how both "
                "factions must now disconnect and recalibrate their algorithms for the next engagement."
            )
        else:
            return (
                "The game ends in a draw! Both players have filled the board without either "
                "establishing a connecting four in a row.\n\n"
                "Generate a conclusion to this evenly matched contest, describing the strategic "
                "deadlock and the anticipation for a rematch between these equally skilled opponents."
            )


# Example of how to use the GameNarrator with local LLM integration

def get_llm_response(prompt):
    """
    Function to get a response from a local LLM.
    This is a placeholder - replace with actual LLM integration code.
    
    Args:
        prompt (str): The prompt to send to the LLM
        
    Returns:
        str: The generated narrative
    """
    # This is where you would add code to call your local LLM
    # For example, using a library like llama-cpp-python, transformers, etc.
    
    # Placeholder response
    return f"[This is where the LLM would generate a narrative based on the prompt: '{prompt[:50]}...']"


def evaluate_and_narrate(game, column, narrator):
    """
    Helper function to evaluate a move and generate narrative using LLM.
    
    Args:
        game (ConnectFourGame): The current game state
        column (int): The column where the player placed their piece
        narrator (GameNarrator): The game narrator
        
    Returns:
        str: The generated narrative
    """
    # Generate the appropriate prompt based on game state
    prompt = narrator.generate_move_narrative(game, column)
    
    # Get response from LLM
    narrative = get_llm_response(prompt)
    
    return narrative 