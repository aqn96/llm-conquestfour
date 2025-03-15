#!/usr/bin/env python3
"""
Test Dynamic Battle Narrator with Local LLM

This script demonstrates how the local LLM can function as a battle narrator
that adapts to the quality of moves, creating more engaging, contextual narratives
that vary based on player performance.
"""
import os
import sys
import time
import logging
import torch

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game.connect_four import ConnectFourGame, Player
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Path to the Mistral model
MODEL_PATH = os.path.expanduser(os.environ.get("LOCAL_LLM_PATH", "~/models/mistral-7b"))

class DynamicBattleNarrator:
    """
    An enhanced battle narrator that analyzes move quality and generates
    narratives that reflect the strategic value of each move.
    """
    
    def __init__(self, model_path=MODEL_PATH):
        """
        Initialize the dynamic battle narrator with a local LLM.
        
        Args:
            model_path: Path to the local LLM model
        """
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.current_theme = "fantasy"
        self.theme_context = {}
        self.battle_history = []
        self.last_narrative = ""
        
    def load(self):
        """
        Load the LLM model for narrative generation.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            logging.info(f"Loading model from {self.model_path}...")
            
            # Check if model path exists
            if not os.path.exists(self.model_path):
                logging.error(f"Model path does not exist: {self.model_path}")
                return False
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # Load model with reduced precision for efficiency
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            # Create generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer
            )
            
            # Initialize theme contexts
            self._initialize_theme_contexts()
            
            logging.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            return False
    
    def _initialize_theme_contexts(self):
        """Initialize context information for all supported themes"""
        # Fantasy theme
        self.themes = {
            "fantasy": {
                "player1_name": "Crystal Lords",
                "player2_name": "Shadow Keepers",
                "board_name": "Crystal Grid",
                "piece_names": ["crystal shard", "obsidian token"],
                "setting": "mystical realm",
                "good_descriptors": ["brilliant", "masterful", "inspired", "tactical", "ingenious"],
                "bad_descriptors": ["risky", "uncertain", "desperate", "questionable", "precarious"],
                "neutral_descriptors": ["steady", "calculated", "measured", "deliberate", "patient"]
            },
            "sci-fi": {
                "player1_name": "Quantum Collective",
                "player2_name": "Void Syndicate",
                "board_name": "Probability Matrix",
                "piece_names": ["quantum token", "void fragment"],
                "setting": "deep space station",
                "good_descriptors": ["calculated", "strategic", "optimal", "precise", "efficient"],
                "bad_descriptors": ["chaotic", "erratic", "miscalculated", "unstable", "flawed"],
                "neutral_descriptors": ["standard", "procedural", "regulated", "systematic", "methodical"]
            },
            "western": {
                "player1_name": "Lawmen",
                "player2_name": "Desperados",
                "board_name": "Territory Grid",
                "piece_names": ["sheriff badge", "outlaw token"],
                "setting": "dusty frontier town",
                "good_descriptors": ["sharp-eyed", "quick-draw", "dead-shot", "cunning", "seasoned"],
                "bad_descriptors": ["green", "reckless", "wild", "hasty", "careless"],
                "neutral_descriptors": ["steady", "watchful", "careful", "deliberate", "guarded"]
            }
        }
        self.theme_context = self.themes[self.current_theme]
    
    def set_theme(self, theme):
        """
        Set the current theme for narrative generation.
        
        Args:
            theme: Name of the theme (fantasy, sci-fi, western)
        """
        if theme.lower() in self.themes:
            self.current_theme = theme.lower()
            self.theme_context = self.themes[self.current_theme]
            self.battle_history = []
            self.last_narrative = ""
            logging.info(f"Set theme to {theme}")
        else:
            logging.warning(f"Unknown theme: {theme}. Using current theme.")
    
    def analyze_move_quality(self, game, player, move_column):
        """
        Analyze the quality of a move.
        
        Args:
            game: The Connect Four game state
            player: The player who made the move (1 or 2)
            move_column: The column where the piece was placed
            
        Returns:
            str: 'good', 'bad', or 'neutral' based on move analysis
        """
        # Get the board for analysis
        board = game.board if hasattr(game, 'board') else game
        
        # If this created a win, it's obviously good
        if hasattr(game, 'check_win'):
            if game.check_win() == player:
                return "good"
        
        # Check if the move blocked an opponent's potential win
        opponent = 3 - player  # Connect Four uses 1 and 2 for players
        
        # Create a copy of the game to test opponent's potential
        test_game = ConnectFourGame()
        test_game.board = [row.copy() for row in board]
        
        # Find potential opponent win in next move
        blocked_win = False
        for col in range(7):  # Connect Four has 7 columns
            # Skip if column is full
            if all(test_game.board[row][col] != 0 for row in range(6)):
                continue
                
            # Find the row where the piece would land
            for row in range(5, -1, -1):
                if test_game.board[row][col] == 0:
                    # Try opponent's move here
                    test_game.board[row][col] = opponent
                    if test_game.check_win() == opponent:
                        blocked_win = True
                    # Reset for next test
                    test_game.board[row][col] = 0
                    break
        
        if blocked_win and move_column == col:
            return "good"
        
        # Check if the move created a threat (3 in a row)
        created_threat = False
        for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:  # Horizontal, vertical, diagonal
            dx, dy = direction
            for row in range(6):
                for col in range(7):
                    # Skip if cell is empty or not the player's piece
                    if board[row][col] != player:
                        continue
                    
                    # Count consecutive pieces
                    count = 1
                    r, c = row + dx, col + dy
                    while 0 <= r < 6 and 0 <= c < 7 and board[r][c] == player:
                        count += 1
                        r += dx
                        c += dy
                    
                    # Check if there's an empty spot after the sequence for a potential win
                    if count == 3 and 0 <= r < 6 and 0 <= c < 7 and board[r][c] == 0:
                        created_threat = True
        
        if created_threat:
            return "good"
            
        # Check if it's a center move (generally better in Connect Four)
        if 2 <= move_column <= 4:
            return "neutral"
            
        # Check if it's an edge move (generally worse)
        if move_column in [0, 6]:
            # But if it's the only available move, it's neutral
            available_columns = sum(1 for col in range(7) 
                                   if any(board[row][col] == 0 for row in range(6)))
            if available_columns <= 2:
                return "neutral"
            return "bad"
        
        # Default to neutral
        return "neutral"
    
    def generate_narrative(self, game, player, move_column):
        """
        Generate a narrative based on game state and move quality.
        
        Args:
            game: The Connect Four game state
            player: The player who made the move (1 or 2)
            move_column: The column where the piece was placed
            
        Returns:
            str: Generated narrative
        """
        if not self.generator:
            return f"The {self.theme_context['player' + str(player) + '_name']} make their move."
        
        # Analyze the quality of the move
        move_quality = self.analyze_move_quality(game, player, move_column)
        logging.info(f"Move quality analysis: {move_quality.upper()}")
        
        # Build system prompt based on move quality
        prompt = self._create_dynamic_prompt(game, player, move_column, move_quality)
        
        try:
            # Generate narrative
            start_time = time.time()
            response = self.generator(
                prompt,
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                return_full_text=False
            )
            elapsed = time.time() - start_time
            logging.info(f"Narrative generation took {elapsed:.2f} seconds")
            
            # Extract and format response
            if response and len(response) > 0:
                narrative = response[0]["generated_text"].strip()
                
                # If we somehow got the same narrative or it contains generic phrases, try again
                if narrative.lower() == self.last_narrative.lower() or "mystical energies" in narrative.lower():
                    # Try one more time with stronger uniqueness instructions
                    logging.info("Narrative was repetitive. Trying again...")
                    prompt += "\nIMPORTANT: Create something COMPLETELY different from previous narratives!"
                    
                    response = self.generator(
                        prompt,
                        max_new_tokens=100,
                        temperature=0.8,  # Slightly higher temperature for more variation
                        top_p=0.95,
                        do_sample=True,
                        return_full_text=False
                    )
                    
                    if response and len(response) > 0:
                        narrative = response[0]["generated_text"].strip()
                
                # Store this narrative to avoid repetition next time
                self.last_narrative = narrative
                
                # Add to battle history for context in future prompts
                self.battle_history.append({
                    "player": player,
                    "column": move_column,
                    "quality": move_quality,
                    "narrative": narrative
                })
                
                # Keep history limited to avoid context length issues
                if len(self.battle_history) > 5:
                    self.battle_history = self.battle_history[-5:]
                
                return narrative
            
            # Fallback if generation failed
            return self._generate_fallback_narrative(player, move_quality)
            
        except Exception as e:
            logging.error(f"Error generating narrative: {e}")
            return self._generate_fallback_narrative(player, move_quality)
    
    def _create_dynamic_prompt(self, game, player, move_column, move_quality):
        """
        Create a dynamic prompt based on game state and move quality.
        
        Args:
            game: The Connect Four game
            player: Player number (1 or 2)
            move_column: The column where the move was made
            move_quality: Quality of the move ('good', 'bad', 'neutral')
            
        Returns:
            str: Formatted prompt for the LLM
        """
        # Get player names from theme
        player_name = self.theme_context[f"player{player}_name"]
        opponent_name = self.theme_context[f"player{3-player}_name"]
        
        # Determine game phase based on number of pieces
        filled_cells = sum(1 for row in game.board for cell in row if cell != 0)
        total_cells = len(game.board) * len(game.board[0])
        
        if filled_cells < total_cells * 0.3:
            game_phase = "opening"
        elif filled_cells < total_cells * 0.6:
            game_phase = "midgame"
        else:
            game_phase = "endgame"
        
        # Get appropriate descriptors for the move quality
        if move_quality == "good":
            descriptors = self.theme_context["good_descriptors"]
            quality_description = (
                "This was a GOOD move that created a strategic advantage, "
                "such as setting up a winning position or blocking the opponent."
            )
        elif move_quality == "bad":
            descriptors = self.theme_context["bad_descriptors"]
            quality_description = (
                "This was a BAD move that missed opportunities or created vulnerabilities, "
                "like playing on the edge when center columns are available."
            )
        else:
            descriptors = self.theme_context["neutral_descriptors"]
            quality_description = (
                "This was a NEUTRAL move that made standard progress without "
                "creating significant advantages or disadvantages."
            )
        
        # Build previous narrative context if available
        narrative_history = ""
        if self.battle_history:
            narrative_history = "Previous moves:\n"
            for i, prev in enumerate(self.battle_history[-3:]):
                player_key = f"player{prev['player']}_name"
                player_name = self.themes[self.current_theme][player_key]
                move_quality = prev['quality'].upper()
                narrative_text = prev['narrative']
                narrative_history += f"{i+1}. {player_name} ({move_quality} move): {narrative_text}\n"
        
        # Create prompt with specific instructions
        prompt = f"""### Instruction:
You are an expert battle narrator for a Connect Four game with a {self.current_theme} theme.
The game is in the {game_phase} phase with {filled_cells} pieces on the board.
The {player_name} just made a move in column {move_column + 1}.

{quality_description}

Create a vivid, engaging narration (1-2 sentences) that:
1. Is COMPLETELY DIFFERENT from this previous narration: "{self.last_narrative}"
2. Clearly reflects the {move_quality.upper()} quality of the move
3. Creates dramatic tension appropriate to the {self.current_theme} setting
4. Emphasizes how this move impacts the overall battle
5. Uses varied language and AVOIDS generic descriptions or phrases like "mystical energies"
6. Reflects the game's {game_phase} phase

{narrative_history}

### Response:
"""
        return prompt
    
    def _generate_fallback_narrative(self, player, move_quality):
        """
        Generate a fallback narrative when LLM generation fails.
        
        Args:
            player: Player number (1 or 2)
            move_quality: Quality of the move ('good', 'bad', 'neutral')
            
        Returns:
            str: Fallback narrative
        """
        import random
        
        player_name = self.theme_context[f"player{player}_name"]
        piece_name = self.theme_context["piece_names"][player - 1]
        
        if move_quality == "good":
            templates = [
                f"The {player_name} make a brilliant strategic placement, turning the tide in their favor.",
                f"With tactical precision, the {player_name} strengthen their position on the battlefield.",
                f"A masterful move by the {player_name} threatens to break through enemy lines."
            ]
        elif move_quality == "bad":
            templates = [
                f"The {player_name} hesitate, placing their {piece_name} in a precarious position.",
                f"An uncertain move by the {player_name} fails to advance their strategy.",
                f"The {player_name} make a questionable choice, potentially exposing a weakness."
            ]
        else:
            templates = [
                f"The {player_name} make a measured placement, maintaining the balance of power.",
                f"With careful consideration, the {player_name} position their {piece_name} on the grid.",
                f"The {player_name} continue their steady advance across the battlefield."
            ]
        
        return random.choice(templates)


def test_dynamic_battle_narrator():
    """Test the dynamic battle narrator with different move qualities"""
    logging.info("Testing dynamic battle narrator...")
    
    # Create narrator and game
    narrator = DynamicBattleNarrator()
    success = narrator.load()
    
    if not success:
        logging.warning("Could not load model. Using fallback mode.")
    
    # Create game
    game = ConnectFourGame()
    
    # Test with different themes
    for theme in ["fantasy", "sci-fi", "western"]:
        print(f"\n\n===== Testing {theme.upper()} Theme =====\n")
        narrator.set_theme(theme)
        game.reset()
        
        # Scenario 1: Good move - Center column in opening
        print("\n--- GOOD MOVE: Center column in opening ---")
        player = Player.ONE.value
        game.make_move(3)  # Player ONE makes move in center
        narrative = narrator.generate_narrative(game, player, 3)
        print(f"Board state:\n{game}")
        print(f"Narrative: {narrative}\n")
        
        # Scenario 2: Bad move - Edge column when center is available
        print("\n--- BAD MOVE: Edge column when center is available ---")
        player = Player.TWO.value
        game.make_move(0)  # Player TWO makes move on edge
        narrative = narrator.generate_narrative(game, player, 0)
        print(f"Board state:\n{game}")
        print(f"Narrative: {narrative}\n")
        
        # Scenario 3: Good move - Blocking opponent's win
        print("\n--- GOOD MOVE: Blocking opponent's potential win ---")
        # Set up a potential win scenario
        player = Player.ONE.value
        game.make_move(4)  # Player ONE makes move
        player = Player.TWO.value
        game.make_move(1)  # Player TWO makes move
        player = Player.ONE.value
        game.make_move(5)  # Player ONE makes move
        # This move blocks a potential horizontal win
        player = Player.TWO.value
        game.make_move(2)  # Player TWO makes blocking move
        narrative = narrator.generate_narrative(game, player, 2)
        print(f"Board state:\n{game}")
        print(f"Narrative: {narrative}\n")
        
        # Scenario 4: Neutral move - Standard development
        print("\n--- NEUTRAL MOVE: Standard development ---")
        player = Player.ONE.value
        game.make_move(3)  # Player ONE makes standard move
        narrative = narrator.generate_narrative(game, player, 3)
        print(f"Board state:\n{game}")
        print(f"Narrative: {narrative}\n")
        
        # Scenario 5: Good move - Setting up a win
        print("\n--- GOOD MOVE: Setting up a win ---")
        player = Player.TWO.value
        game.make_move(3)  # Player TWO makes move
        player = Player.ONE.value
        game.make_move(4)  # Player ONE sets up win
        narrative = narrator.generate_narrative(game, player, 4)
        print(f"Board state:\n{game}")
        print(f"Narrative: {narrative}\n")
        
        # Scenario 6: Winning move
        print("\n--- WINNING MOVE: Completing a winning sequence ---")
        player = Player.TWO.value
        game.make_move(4)  # Player TWO makes move
        # This move should complete a win
        player = Player.ONE.value
        game.make_move(5)  # Player ONE wins
        
        # Check if we actually won
        winner = game.check_win()
        if winner:
            print(f"Winner detected: Player {winner}")
            
        narrative = narrator.generate_narrative(game, player, 5)
        print(f"Board state:\n{game}")
        print(f"Narrative: {narrative}\n")
        
        # Give time between tests to avoid overwhelming
        time.sleep(1)


if __name__ == "__main__":
    test_dynamic_battle_narrator() 