"""
AI Model Loader Module - Handles loading and using AI models for narrative generation

This module is currently too large (1500+ lines) and should be refactored into multiple smaller modules:

REFACTORING PLAN:
----------------
1. Create a directory structure for better organization:
   ai/
    ├── __init__.py
    ├── narrators/
    │   ├── __init__.py
    │   ├── base_narrator.py         # Abstract base class for narrators
    │   ├── local_llm_narrator.py    # Extract LocalLLMNarrator class
    │   ├── simple_narrator.py       # Extract SimpleModel and EnhancedSimpleModel
    │   └── fallback_narrator.py     # Extract fallback narrative generation
    ├── loaders/
    │   ├── __init__.py
    │   ├── model_loader.py          # Refactored to be smaller and focused
    │   └── unified_loader.py        # Extract UnifiedModelLoader
    └── utils/
        ├── __init__.py
        ├── caching.py               # Extract caching functionality
        ├── memory_management.py     # Extract memory management code
        └── text_generation.py       # Extract text generation utilities

2. Break down the large classes:
   - LocalLLMNarrator: Split into smaller classes or components
   - UnifiedModelLoader: Focus on model loading only
   - Extract common utilities like timeout handling into shared components

3. Improve interfaces:
   - Create consistent interfaces for all narrators
   - Standardize parameter names and types
   - Add type hints for all function signatures

4. Reduce duplicate code:
   - Consolidate similar methods
   - Create utility functions for common operations
   - Use inheritance effectively

This refactoring will improve:
- Code maintainability
- Testability
- Performance (by making components more focused)
- Code reuse and extension
"""

import os
import gc
import logging
import time
import random
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import torch
from PyQt6.QtCore import QObject, pyqtSignal

# Try to import transformers for local LLM support
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers library not found. Local LLM will not be available.")


class SimpleModel:
    """
    Simple fallback model used when advanced models can't be loaded.
    Provides basic narrative generation capabilities.
    """
    
    def __init__(self):
        """Initialize the simple model"""
        self.responses = {
            "fantasy": [
                "The Crystal Lords place their rune stone carefully on the grid.",
                "Shadow Keepers strike back with a powerful dark crystal!",
                "The magical grid glimmers as the next piece falls into place.",
                "A strategic move threatens to disrupt the mystical balance.",
                "Arcane energies swirl as the crystal aligns with others."
            ],
            "sci-fi": [
                "The Quantum Collective deploys a probability matrix node.",
                "Void Syndicate counters with an antimatter projection!",
                "Subspace fluctuations indicate a potential winning strategy.",
                "Dimensional calculations suggest this move has a 87.3% success rate.",
                "The temporal field shifts as the pieces align in sequence."
            ],
            "western": [
                "The Desperados stake their claim with determination.",
                "The Lawmen counter with a strategic move.",
                "Dust settles as the next piece drops into the frontier.",
                "A tumbleweed rolls by as tension builds in this standoff.",
                "The saloon goes quiet as the next move is calculated."
            ]
        }
        
        # Default responses when theme isn't recognized
        self.default_responses = [
            "A strategic move is made.",
            "The battle continues as the next piece falls.",
            "The game intensifies with this calculated placement.",
            "A tactical decision shapes the board state.",
            "The balance of power shifts with this move."
        ]
    
    def generate(self, prompt, theme="default"):
        """Generate a simple response based on theme"""
        theme = theme.lower() if isinstance(theme, str) else "default"
        
        # Get responses for the theme or use default
        responses = self.responses.get(theme, self.default_responses)
        
        # Select a response based on a hash of the prompt
        # This ensures some consistency for similar prompts
        prompt_hash = sum(ord(c) for c in prompt) if prompt else 0
        index = prompt_hash % len(responses)
        
        return responses[index]


class EnhancedSimpleModel(SimpleModel):
    """
    Enhanced version of the simple model with more varied responses
    and basic context awareness.
    """
    
    def __init__(self):
        """Initialize the enhanced simple model"""
        super().__init__()
        
        # Add more responses to each theme
        self.responses["fantasy"].extend([
            "Mystical energies converge as the Crystal Lords make their move.",
            "The Shadow Keepers cast a dark enchantment on the board.",
            "Ancient runes glow ominously as the pieces align.",
            "A whispering prophecy guides the next strategic placement.",
            "The ethereal board shifts and adapts to the new configuration."
        ])
        
        self.responses["sci-fi"].extend([
            "Quantum probability waves collapse into a new configuration.",
            "The Void Syndicate deploys a strategic algorithm to counter.",
            "Holographic projections calculate optimal trajectories.",
            "Subspace anomalies detected as pieces form a pattern.",
            "The AI core suggests this move has tactical advantages."
        ])
        
        self.responses["western"].extend([
            "Under the desert sun, a calculated move changes the game.",
            "The sheriff narrows his eyes as the outlaw makes a bold play.",
            "Gold dust glimmers as a token falls into a strategic position.",
            "The frontier town holds its breath as the standoff continues.",
            "A strategic play worthy of the wildest tales of the West."
        ])
    
    def generate(self, prompt, theme="default"):
        """Generate an enhanced response with better context awareness"""
        # Basic context extraction from prompt
        context = {}
        if "threat" in prompt.lower():
            context["situation"] = "threat"
        elif "winning" in prompt.lower():
            context["situation"] = "advantage"
        elif "opening" in prompt.lower():
            context["situation"] = "opening"
        else:
            context["situation"] = "neutral"
            
        # Call parent implementation and add context-specific modifier
        base_response = super().generate(prompt, theme)
        
        # Add context-specific additions
        if context["situation"] == "threat":
            return base_response + " Danger looms on the horizon."
        elif context["situation"] == "advantage":
            return base_response + " Victory seems within reach."
        elif context["situation"] == "opening":
            return base_response + " The battle has just begun."
        
        return base_response


class LocalLLMNarrator:
    """
    Generates battle narratives using a local LLM like Mistral 7B.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the local LLM narrator.
        
        Args:
            model_path (str): Path to the local LLM model. If None, will try to use
                a default model path from environment variable LOCAL_LLM_PATH.
        """
        self.model_path = model_path or os.environ.get("LOCAL_LLM_PATH")
        
        # Always expand user path to ensure we can load the model properly
        if self.model_path and '~' in self.model_path:
            self.model_path = os.path.expanduser(self.model_path)
            logging.info(f"Expanded model path to: {self.model_path}")
            
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.current_theme = "fantasy"
        self.theme_context = {}
        self.battle_history = []
        self.last_narrative = ""  # Track last narrative to avoid repetition
        self.story_context = ""  # Holds the 4-5 sentence story context
        self.player_faction = ""  # Dynamic faction name for player
        self.computer_faction = ""  # Dynamic faction name for computer
        self.story_generated = False  # Whether a story has been generated
        
    def load(self):
        """
        Load the local LLM model.
        
        Returns:
            bool: True if loading was successful, False otherwise
        """
        if not HAS_TRANSFORMERS:
            logging.error("Cannot load local LLM: transformers library not installed")
            return False
            
        if not self.model_path:
            logging.error("No model path specified for local LLM")
            return False
            
        try:
            logging.info(f"Loading local LLM from {self.model_path}")
            
            # Check if model path exists
            model_path = os.path.expanduser(self.model_path)
            if not os.path.exists(model_path):
                logging.error(f"Model path does not exist: {self.model_path}")
                return False
            
            # Configure loading with memory optimization options
            cpu_optimized_options = {
                "device_map": "auto",
                "low_cpu_mem_usage": True,
            }
            
            # Get max context length if specified in environment
            max_context_length = os.environ.get("MAX_CONTEXT_LENGTH")
            if max_context_length:
                try:
                    max_context_length = int(max_context_length)
                    logging.info(f"Using maximum context length of {max_context_length}")
                except ValueError:
                    max_context_length = None
                    logging.warning("Invalid MAX_CONTEXT_LENGTH, using model default")
            
            # Load model using only CPU options for stability
            logging.info("Loading model optimized for CPU performance")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **cpu_optimized_options
            )
                
            # Load tokenizer with performance options
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                use_fast=True,  # Use fast tokenizer
                model_max_length=max_context_length if max_context_length else 2048
            )
            
            # Set up text generation pipeline with optimized parameters
            pipeline_config = {
                "max_new_tokens": 100,  # Limit token generation
                "pad_token_id": self.tokenizer.eos_token_id,
                "num_return_sequences": 1,
                "no_repeat_ngram_size": 3
            }
            
            # Add max length if specified
            if max_context_length:
                pipeline_config["max_length"] = max_context_length
            
            # Create pipeline with optimized settings
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                **pipeline_config
            )
            
            # Initialize theme context
            self._initialize_theme_context(self.current_theme)
            
            logging.info("Model successfully loaded!")
            return True
            
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_theme(self, theme):
        """
        Set the current theme for narrative generation.
        
        Args:
            theme (str): The theme to use for narrative generation
        """
        if theme.lower() != self.current_theme:
            self.current_theme = theme.lower()
            self.battle_history = []
            self.story_generated = False  # Reset story context for new theme
            self._initialize_theme_context(theme)
    
    def _initialize_theme_context(self, theme):
        """
        Initialize context information for the specified theme.
        
        Args:
            theme (str): The theme to initialize
        """
        if theme.lower() == "fantasy":
            self.theme_context = {
                "player1_name": "Crystal Lords",
                "player2_name": "Shadow Keepers",
                "board_name": "Crystal Grid",
                "piece_name_p1": "crystal",
                "piece_name_p2": "obsidian shard",
                "setting": "mystical realm",
                "action_verbs": ["summon", "conjure", "enchant", "channel", "manifest"],
                "descriptors": ["arcane", "mystical", "ethereal", "magical", "ancient"]
            }
        elif theme.lower() in ["scifi", "sci-fi"]:
            self.theme_context = {
                "player1_name": "Quantum Collective",
                "player2_name": "Void Syndicate",
                "board_name": "Probability Matrix",
                "piece_name_p1": "quantum token",
                "piece_name_p2": "void fragment",
                "setting": "deep space",
                "action_verbs": ["deploy", "calculate", "generate", "project", "materialize"],
                "descriptors": ["quantum", "subspace", "dimensional", "molecular", "temporal"]
            }
        elif theme.lower() == "western":
            self.theme_context = {
                "player1_name": "Desperados",
                "player2_name": "Lawmen",
                "board_name": "Frontier Town",
                "piece_name_p1": "gold coin",
                "piece_name_p2": "silver badge",
                "setting": "wild west",
                "action_verbs": ["draw", "shoot", "stake", "claim", "wrangle"],
                "descriptors": ["dusty", "rugged", "weathered", "sun-baked", "frontier"]
            }
        else:
            # Generic theme as fallback
            self.theme_context = {
                "player1_name": "Player One",
                "player2_name": "Player Two",
                "board_name": "Game Board",
                "piece_name_p1": "token",
                "piece_name_p2": "token",
                "setting": "arena",
                "action_verbs": ["place", "position", "set", "drop", "move"],
                "descriptors": ["strategic", "tactical", "calculated", "precise", "clever"]
            }
    
    def generate_narrative(self, game_state, current_player, 
                           move_column=None, game_phase="midgame"):
        """
        Generate a narrative description for the current game state using the local LLM.
        
        Args:
            game_state: The current game state (board representation)
            current_player: The current player (1 or 2)
            move_column: The column of the last move (if applicable)
            game_phase: The current phase of the game ('opening', 'midgame', 'endgame')
            
        Returns:
            str: The generated narrative description
        """
        # Enhanced diagnostic logging
        logging.info(f"Generate narrative called with game_phase: {game_phase}")
        logging.info(f"Story generated status: {self.story_generated}")
        
        if not self.generator:
            logging.warning("Generator not available, using fallback narrative")
            return self._generate_fallback_narrative(current_player, move_column)
        
        # Check if we need to generate the story context - IMPROVED DETECTION
        if game_phase == "opening":
            logging.info("Opening phase detected - generating or using story context")
            
            # For new games or theme changes, we should generate a fresh story
            if not self.story_generated:
                logging.info("Story not yet generated - creating new story context")
                try:
                    # Generate faction names first
                    self._generate_faction_names()
                    
                    # Then generate story context
                    self._generate_story_context()
                    self.story_generated = True
                    
                    # For the first move, return the story intro
                    if len(self.battle_history) == 0:
                        logging.info("Returning initial story context")
                        return self.story_context
                except Exception as e:
                    logging.error(f"Error generating story context: {e}")
                    # Continue with default names if we can't generate new ones
                    if not self.player_faction or not self.computer_faction:
                        self._set_default_faction_names()
                    if not self.story_context:
                        self._set_default_story_context()
            else:
                # We already have a story - make sure we add it to the battle history
                logging.info("Using existing story context")
                if len(self.battle_history) == 0:
                    return self.story_context

        # Analyze move quality if a move was made
        move_quality = "neutral"
        is_winning_move = False
        if move_column is not None:
            # Check if game has a board
            if hasattr(game_state, 'board') and game_state.board is not None:
                move_quality = self._analyze_move_quality(
                    game_state, current_player, move_column
                )
                # Check if this is a winning move
                if hasattr(game_state, 'check_win') and \
                   callable(getattr(game_state, 'check_win')):
                    is_winning_move = game_state.check_win(current_player)
                    if is_winning_move:
                        logging.info(f"Winning move detected for player {current_player}")
        
        # Create a prompt for the LLM
        prompt = self._create_themed_prompt(
            game_state, current_player, move_column, 
            game_phase, move_quality, is_winning_move
        )
        
        try:
            # Generate narrative with local LLM
            response = self.generator(
                prompt, 
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            # Extract the generated text
            if response and len(response) > 0:
                # The response includes the prompt, so we need to extract just the generated part
                full_text = response[0]['generated_text']
                narrative = full_text[len(prompt):].strip()
                
                # Limit to first 2 sentences for brevity
                sentences = narrative.split('.')
                if len(sentences) > 2:
                    narrative = '.'.join(sentences[:2]) + '.'
                
                # Check for repetition or generic phrases
                if (narrative.lower() == self.last_narrative.lower() or 
                    "mystical energies" in narrative.lower()):
                    # Try once more with stronger uniqueness instructions
                    logging.info("Narrative was repetitive. Trying again...")
                    prompt += "\nIMPORTANT: Create something COMPLETELY different from your usual patterns!"
                    
                    response = self.generator(
                        prompt, 
                        max_new_tokens=100,
                        temperature=0.8,  # Slightly higher for more variation
                        top_p=0.95,
                        do_sample=True
                    )
                    
                    if response and len(response) > 0:
                        full_text = response[0]['generated_text']
                        narrative = full_text[len(prompt):].strip()
                        
                        sentences = narrative.split('.')
                        if len(sentences) > 2:
                            narrative = '.'.join(sentences[:2]) + '.'
                
                # Store narrative to check for repetition next time
                self.last_narrative = narrative
                
                # Add to battle history for continuity
                self.battle_history.append({
                    "player": current_player,
                    "column": move_column,
                    "quality": move_quality,
                    "narrative": narrative
                })
                
                # Keep history limited to last 5 moves for context
                if len(self.battle_history) > 5:
                    self.battle_history = self.battle_history[-5:]
                
                return narrative
            
            return self._generate_fallback_narrative(current_player, move_column, move_quality)
            
        except Exception as e:
            logging.error(f"Error generating local LLM narrative: {e}")
            return self._generate_fallback_narrative(current_player, move_column, move_quality)
    
    def _analyze_move_quality(self, game_state, player, move_column):
        """
        Analyze the quality of a move.
        
        Args:
            game_state: The Connect Four game state
            player: The player who made the move (1 or 2)
            move_column: The column where the piece was placed
            
        Returns:
            str: 'good', 'bad', or 'neutral' based on move analysis
        """
        # Get the board for analysis
        board = game_state.board if hasattr(game_state, 'board') else []
        
        if not board or not isinstance(board, list) or move_column is None:
            return "neutral"  # Default if we can't analyze
        
        # If this created a win, it's obviously good
        if hasattr(game_state, 'check_winner'):
            if game_state.check_winner() == player:
                return "good"
        
        # Find row where the piece was placed
        row = None
        for r in range(len(board) - 1, -1, -1):
            if board[r][move_column] == player:
                row = r
                break
                
        if row is None:
            return "neutral"  # Couldn't find the piece
            
        # Check if move blocked opponent's win or created a winning threat
        if self._check_blocking_move(board, player, row, move_column):
            return "good"
            
        if self._check_winning_opportunity(board, player, row, move_column):
            return "good"
            
        # Check if it's a center move (generally better in Connect Four)
        if self._is_center_column(move_column, board[0]):
            return "neutral"
            
        # Check if it's an edge move (generally worse)
        if self._is_edge_column(move_column, board[0]):
            # But if limited options remain, it's neutral
            available_columns = sum(1 for col in range(len(board[0])) 
                                  if any(row[col] == 0 for row in board))
            if available_columns <= 2:
                return "neutral"
            return "bad"
        
        # Default to neutral
        return "neutral"
    
    def _create_themed_prompt(self, game_state, current_player, 
                             move_column=None, game_phase="midgame",
                             move_quality="neutral", is_winning_move=False):
        """
        Create a themed prompt for the LLM.
        
        Args:
            game_state: Current game state
            current_player: Current player (1 or 2)
            move_column: Column of the last move
            game_phase: Current game phase
            move_quality: Quality of the move ('good', 'bad', 'neutral')
            is_winning_move: Whether this is a winning move
            
        Returns:
            str: Formatted prompt
        """
        # Set faction names based on player number
        if current_player == 1:
            active_faction = self.player_faction or self.theme_context["player1_name"]
            opposing_faction = self.computer_faction or self.theme_context["player2_name"]
        else:
            active_faction = self.computer_faction or self.theme_context["player2_name"]
            opposing_faction = self.player_faction or self.theme_context["player1_name"]
        
        # Analyze the board state
        board_analysis = self._analyze_board_state(game_state, current_player)
        
        # Determine move quality impact on narrative
        if is_winning_move:
            move_quality_description = (
                f"just made a WINNING MOVE that will defeat the {opposing_faction}"
            )
            narrative_directive = (
                f"Dramatically describe how the {active_faction} has achieved victory and "
                f"the {opposing_faction} has been defeated. Make it emotionally impactful."
            )
        elif move_quality == "good":
            move_quality_description = (
                f"made a STRONG strategic move that gives them an advantage over the {opposing_faction}"
            )
            narrative_directive = (
                f"Show how the {active_faction} is gaining the upper hand in the conflict, "
                f"while the {opposing_faction} faces new challenges or setbacks."
            )
        elif move_quality == "bad":
            move_quality_description = (
                f"made a POOR tactical decision that creates an opportunity for the {opposing_faction}"
            )
            narrative_directive = (
                f"Describe how the {active_faction}'s mistake or oversight has created an "
                f"advantage for the {opposing_faction}, shifting the momentum of the battle."
            )
        else:
            move_quality_description = (
                f"made a standard move that maintains the current balance with the {opposing_faction}"
            )
            narrative_directive = (
                f"Focus on the tension between the {active_faction} and {opposing_faction}, "
                f"the strategic positioning, or the anticipation of future developments."
            )
        
        # Get last few narratives for context
        narrative_history = ""
        if self.battle_history:
            recent_narratives = [h["narrative"] for h in self.battle_history[-3:]]
            if recent_narratives:
                narrative_history = "Previous battle developments:\n"
                for i, narr in enumerate(recent_narratives):
                    narrative_history += f"{i+1}. {narr}\n"
                narrative_history += "\n"
        
        # Get board state for context
        filled_cells = sum(1 for row in game_state.board for cell in row if cell != 0)
        total_cells = len(game_state.board) * len(game_state.board[0])
        progress = int((filled_cells / total_cells) * 100)
        
        # Create prompt with story-focused instructions
        prompt = (
            f"### Instruction:\n"
            f"You are narrating an epic {self.current_theme} battle in the form of a Connect Four game. "
            f"Continue the developing story with a 1-2 sentence narrative that builds on previous events.\n\n"
            
            f"### Story Context:\n{self.story_context}\n\n"
            
            f"### Current Situation:\n"
            f"- The {active_faction} {move_quality_description}\n"
            f"- {narrative_directive}\n"
            f"- Battle progress: {progress}% of the battlefield is occupied\n"
            f"- Board status: {board_analysis}\n\n"
            
            f"### Previous Events:\n{narrative_history}\n"
            
            f"### Important Guidelines:\n"
            f"1. NEVER repeat the same phrases or descriptions from previous narratives\n"
            f"2. Focus on advancing the story and building tension\n"
            f"3. Use vivid, specific language appropriate to the {self.current_theme} theme\n"
            f"4. Keep the story coherent with previous events\n"
            f"5. Use varied sentence structures and vocabulary\n\n"
            
            f"### Response (1-2 sentences only):\n"
        )
        
        return prompt
    
    def _check_winning_opportunity(self, board, player, row, col):
        """Check if a move creates a winning opportunity (3 in a row with space for 4)"""
        directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal down-right
            (1, -1)   # diagonal down-left
        ]
        
        rows = len(board)
        cols = len(board[0]) if rows > 0 else 0
        
        for dr, dc in directions:
            count = 1  # Start with 1 for the current piece
            
            # Count in positive direction
            r, c = row + dr, col + dc
            while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            # Count in negative direction
            r, c = row - dr, col - dc
            while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            # If we have 3 in a row and potential for 4, it's a strong move
            if count >= 3:
                return True
        
        return False
    
    def _check_blocking_move(self, board, player, row, col):
        """Check if a move blocks the opponent from winning"""
        opponent = 3 - player  # In Connect Four, players are 1 and 2
        
        # Temporarily modify the board to see if the opponent would have won
        board[row][col] = opponent
        
        # Check if this would be a winning move for the opponent
        would_opponent_win = self._check_winning_opportunity(board, opponent, row, col)
        
        # Restore the board
        board[row][col] = player
        
        return would_opponent_win
    
    def _is_center_column(self, col, row):
        """Check if a column is in the center third of the board"""
        cols = len(row)
        center_start = cols // 3
        center_end = cols - center_start
        return center_start <= col < center_end
    
    def _is_edge_column(self, col, row):
        """Check if a column is on the edge of the board"""
        cols = len(row)
        return col == 0 or col == cols - 1
    
    def _analyze_board_state(self, game_state, current_player):
        """
        Analyze the board state to provide context for the narrative.
        
        Args:
            game_state: The current game state
            current_player: The current player (1 or 2)
            
        Returns:
            str: A text description of the board state
        """
        # Count pieces
        board = game_state.board if hasattr(game_state, 'board') else []
        
        if not board or not isinstance(board, list):
            return "The battle is just beginning."
        
        player_count = sum(1 for row in board for cell in row if cell == current_player)
        opponent_count = sum(1 for row in board for cell in row if cell == 3 - current_player)
        
        # Determine board control
        if player_count > opponent_count:
            control = f"The {self.theme_context[f'player{current_player}_name']} currently dominate the {self.theme_context['board_name']}."
        elif opponent_count > player_count:
            control = f"The {self.theme_context[f'player{3-current_player}_name']} currently control more of the {self.theme_context['board_name']}."
        else:
            control = f"The battle on the {self.theme_context['board_name']} is evenly matched."
        
        return control
    
    def _generate_fallback_narrative(self, player, move_column=None, move_quality="neutral"):
        """
        Generate a fallback narrative when the LLM is unavailable.
        
        Args:
            player: The player number (1 or 2) or Player enum
            move_column: The column of the move (if applicable)
            move_quality: Quality of the move ('good', 'bad', 'neutral')
            
        Returns:
            str: A simple narrative description
        """
        # Convert player to int if it's an enum or other object
        player_num = player
        if hasattr(player, 'value'):  # Handle Player enum
            player_num = player.value
        elif not isinstance(player, int):
            # Try to convert to string then extract number
            try:
                player_str = str(player)
                if "ONE" in player_str:
                    player_num = 1
                elif "TWO" in player_str:
                    player_num = 2
                else:
                    player_num = 1  # Default to player 1
            except:
                player_num = 1  # Default to player 1
        
        try:
            # Fix the bug with player key access - make sure player_num is 1 or 2
            player_num = 1 if player_num == 1 else 2
            
            # Check if theme_context has been initialized properly
            if not self.theme_context:
                self._initialize_theme_context(self.current_theme)
                
            # Use themed content or default fallbacks if keys don't exist
            player_name = self.theme_context.get(f"player{player_num}_name", f"Player {player_num}")
            piece_name = self.theme_context.get(f"piece_name_p{player_num}", "piece")
            board_name = self.theme_context.get("board_name", "board")
            
            # Default values if action_verbs is missing
            default_actions = ["places", "moves", "drops", "positions", "sets"]
            action_verbs = self.theme_context.get("action_verbs", default_actions)
            action = random.choice(action_verbs)
            
            # Default values if descriptors is missing
            default_descriptors = ["strategic", "tactical", "calculated", "precise", "clever"]
            descriptors = self.theme_context.get("descriptors", default_descriptors)
            descriptor = random.choice(descriptors)
            
        except Exception as e:
            logging.error(f"Error getting narrative elements: {e}")
            # Use default values if theme context fails
            player_name = "Player" if player_num == 1 else "Opponent"
            piece_name = "piece" 
            board_name = "board"
            action = "places"
            descriptor = "strategic"
        
        # Different templates based on move quality
        if move_quality == "good":
            templates = [
                f"The {player_name} make a brilliant strategic placement, turning the tide in their favor.",
                f"With tactical precision, the {player_name} strengthen their position on the {board_name}.",
                f"A masterful move by the {player_name} threatens to break through enemy lines."
            ]
        elif move_quality == "bad":
            templates = [
                f"The {player_name} hesitate, placing their {piece_name} in a precarious position.",
                f"An uncertain move by the {player_name} fails to advance their strategy.",
                f"The {player_name} make a questionable choice, potentially exposing a weakness."
            ]
        else:
            if move_column is not None:
                return f"The {player_name} {action} their {descriptor} {piece_name} in position {move_column + 1} of the {board_name}."
            else:
                return f"The {player_name} carefully consider their next move on the {descriptor} {board_name}."
                
        return random.choice(templates)

    def _generate_faction_names(self):
        """Generate unique, thematic faction names for player and computer"""
        if not self.generator:
            # Use defaults if no generator
            self._set_default_faction_names()
            return
            
        # First check if we already have faction names
        if self.player_faction and self.computer_faction:
            logging.info(f"Using existing faction names: {self.player_faction} vs {self.computer_faction}")
            return
            
        # Use super short prompts for better performance
        if self.current_theme == "fantasy":
            self.player_faction = "Ember Guardians"
            self.computer_faction = "Frost Dominion"
            return
        elif self.current_theme in ["sci-fi", "scifi"]:
            self.player_faction = "Nova Alliance"
            self.computer_faction = "Nexus Collective" 
            return
        elif self.current_theme == "western":
            self.player_faction = "Frontier Rangers"
            self.computer_faction = "Dustland Outlaws"
            return
        else:
            # Default names
            self.player_faction = "Team Alpha"
            self.computer_faction = "Team Omega"
            return

    def _generate_story_context(self):
        """Generate a story context for the battle"""
        if not self.generator:
            # Use defaults if no generator
            self._set_default_story_context()
            return
            
        # If we already have a story context, just return
        if self.story_context:
            return
            
        # Skip the LLM and use predefined content for better performance
        self._set_default_story_context()
        self.story_generated = True
        logging.info(f"Using default story context for better performance")
        return

    def _set_default_story_context(self):
        """Create a default story context based on the current theme"""
        if self.current_theme == "fantasy":
            self.story_context = """In the mystical realm of Crystalia, two ancient factions vie for control of the sacred Crystal Grid. The Crystal Lords, wielders of radiant magic, face off against the Shadow Keepers, masters of dark arcane arts. Whoever controls the Grid will harness its ancient power and determine the fate of the realm. As magical energies swirl, the battle begins with both sides summoning their ethereal forces."""
        elif self.current_theme in ["sci-fi", "scifi"]:
            self.story_context = """Aboard the quantum station Nexus-7, the final battle for control of the Probability Matrix unfolds. The Quantum Collective seeks to stabilize the dimensional rift, while the Void Syndicate intends to harness its chaotic energy. Their advanced technology allows them to materialize subspace tokens that can alter the very fabric of reality. As the station's AI monitors the proceedings, the first tactical calculations begin."""
        elif self.current_theme == "western":
            self.story_context = """On the dusty frontier of New Horizon, the Desperados and Lawmen face off for control of the town. Gold and silver stakes mark their territorial claims on the strategic points of the settlement. The saloon has gone quiet, the wind carries tumbleweeds down the empty street, and the sun beats down mercilessly as both sides prepare their opening moves in this high-stakes showdown."""
        else:
            self.story_context = """The arena is set for an epic strategic confrontation between two skilled opponents. Player One and Player Two have studied each other's tactics and prepared their strategies carefully. The spectators have gathered to witness this battle of wits and foresight. As the signal is given, the opening moves begin, and the first pieces fall into position."""
        
        # Mark that we have generated a story
        self.story_generated = True
        return self.story_context
        
    def _set_default_faction_names(self):
        """Set default faction names based on the current theme"""
        if self.current_theme == "fantasy":
            self.player_faction = "Ember Guardians"
            self.computer_faction = "Frost Dominion"
        elif self.current_theme in ["sci-fi", "scifi"]:
            self.player_faction = "Nova Alliance"
            self.computer_faction = "Nexus Collective"
        elif self.current_theme == "western":
            self.player_faction = "Frontier Rangers"
            self.computer_faction = "Dustland Outlaws"
        else:
            self.player_faction = "Team Alpha"
            self.computer_faction = "Team Omega"
        return


class UnifiedModelLoader(QObject):
    """
    Unified model loader that can handle both local LLM models and NPU models.
    Provides a single interface for narrative generation regardless of the 
    underlying model being used.
    """
    # Signal to notify when model is loaded
    modelLoaded = pyqtSignal(bool)
    
    def __init__(self, model_type="auto", model_path=None):
        """
        Initialize the unified model loader.
        
        Args:
            model_type (str): Type of model to load ('local_llm', 'npu', or 'auto')
            model_path (str, optional): Path to the model (for local LLM)
        """
        super().__init__()
        
        # Initialize cache system with improved structure
        self.cache = {}
        self.cache_history = []  # Track order of cache entries
        self.max_cache_size = 100  # Store up to 100 responses
        self.current_theme = "fantasy"
        self.model_path = model_path
        self.model = None
        self.battle_narrator = None
        self.is_loaded = False
        
        # Enhanced session cache to learn from past games
        self.session_memory = {}  # Store successful narratives by theme
        
        if model_type == "auto":
            # Check if local LLM should be used
            use_local_llm = os.environ.get("USE_LOCAL_LLM", "false").lower() == "true"
            if use_local_llm and (model_path or os.environ.get("LOCAL_LLM_PATH")):
                model_type = "local_llm"
            else:
                model_type = "npu"
                
        self.model_type = model_type
        
        logging.info(f"Initializing {model_type} model loader")
    
    def load_model(self):
        """Start loading the model in a background thread"""
        threading.Thread(target=self._load_model_worker, daemon=True).start()
    
    def _load_model_worker(self):
        """Worker function to load model in background thread"""
        try:
            logging.info(f"Loading {self.model_type} model...")
            
            if self.model_type == "local_llm":
                # Load local LLM model
                self._load_local_llm()
            else:
                # Load NPU model or fallback
                self._load_npu_model()
                
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            self._load_fallback_model()
    
    def _load_local_llm(self):
        """Load a local LLM model"""
        if not HAS_TRANSFORMERS:
            logging.warning("Transformers not available, falling back to simpler model")
            self._load_fallback_model()
            return
            
        # Check if path is set
        if not self.model_path:
            logging.warning("No model path provided for local LLM")
            self._load_fallback_model()
            return
        
        # Load the model - Add more diagnostics and fix potential path issues
        try:
            logging.info(f"Attempting to load local LLM from: {self.model_path}")
            
            # Expand user path if it contains ~
            expanded_path = os.path.expanduser(self.model_path)
            if expanded_path != self.model_path:
                logging.info(f"Expanded model path to: {expanded_path}")
                self.model_path = expanded_path
            
            # Check if path exists
            if not os.path.exists(self.model_path):
                logging.error(f"Model path does not exist: {self.model_path}")
                self._load_fallback_model()
                return
            
            # Create battle narrator with the model path
            # First create a fallback model that's available immediately
            self._load_fallback_model()
            
            # Initialize battle narrator - even without loading the model
            # This ensures the battle_narrator object exists early in initialization
            self.battle_narrator = LocalLLMNarrator(self.model_path)
            
            # Make it available through the model as well (for consistency)
            self.model = self.battle_narrator
            
            # Set initial loaded state to True so the game can start
            # The model will load in the background
            self.is_loaded = True
            
            # Tell the game master we're loaded (we'll use the fallback model until real loading is done)
            self.modelLoaded.emit(True)
            
            # Now actually load the LLM model (this can take some time)
            logging.info("Loading local LLM - this may take a moment...")
            
            # Start a background thread for actually loading the model
            threading.Thread(target=self._load_llm_in_background, daemon=True).start()
            
        except Exception as e:
            logging.error(f"Error setting up local LLM: {e}")
            self._load_fallback_model()
            
    def _load_llm_in_background(self):
        """Load the actual LLM model in a background thread"""
        try:
            # Attempt to load the model
            if self.battle_narrator:
                load_success = self.battle_narrator.load()
                
                if load_success:
                    logging.info("Local LLM successfully loaded!")
                    # Emit the signal again to tell components the real model is loaded
                    self.modelLoaded.emit(True)
                else:
                    logging.error("Failed to load local LLM")
            else:
                logging.error("Battle narrator not initialized properly")
        except Exception as e:
            logging.error(f"Error loading LLM in background: {e}")
    
    def _load_npu_model(self):
        """Load an NPU-optimized model"""
        # Simulate loading advanced model (would link to actual NPU model)
        time.sleep(1)  # Simulate loading time
        
        # For now we just use the enhanced model as NPU model
        # This would be replaced with actual NPU model loading
        self.model = EnhancedSimpleModel()
        self.is_loaded = True
        self.is_advanced_model = True
        logging.info("NPU model loaded successfully")
        self.modelLoaded.emit(True)
    
    def _load_fallback_model(self):
        """Load a fallback model when others fail"""
        logging.info("Loading fallback model...")
        time.sleep(0.5)  # Simulate loading time
        
        self.model = SimpleModel()
        self.is_loaded = True
        self.is_advanced_model = False
        logging.info("Fallback model loaded successfully")
        self.modelLoaded.emit(True)
    
    def set_theme(self, theme):
        """
        Set the current theme for narrative generation.
        
        Args:
            theme (str): The theme to use for narrative generation
        """
        self.current_theme = theme
        
        # If using battle narrator, update its theme
        if hasattr(self.model, 'set_theme'):
            self.model.set_theme(theme)
    
    def generate_narrative(self, prompt_or_game_state):
        """
        Generate a narrative based on a prompt or game state.
        
        Args:
            prompt_or_game_state: Context prompt or game state for narrative generation
            
        Returns:
            str: The generated narrative
        """
        # Enhanced diagnostic logging
        logging.info(f"Generate narrative called with: {type(prompt_or_game_state)}")
        logging.info(f"Model loaded: {self.is_loaded}, Model type: {type(self.model).__name__}")
        
        # Check if model is loaded
        if not self.is_loaded or not self.model:
            logging.warning("Model not loaded, returning fallback narrative")
            return "The battle continues while the strategic systems initialize..."
        
        # Import random locally if not already imported globally
        import random
        
        # Handle based on input type
        if isinstance(prompt_or_game_state, str):
            prompt = prompt_or_game_state
            
            # Check if we have cached this prompt
            if prompt in self.cache:
                logging.info("Using cached response for prompt")
                return self.cache[prompt]
            
            # Generate based on model type
            if isinstance(self.model, LocalLLMNarrator):
                logging.info("Using LocalLLMNarrator but with string prompt - fallback")
                # For LLM, we need a game state, but we don't have one
                # Return a fallback response
                response = self._generate_fallback_text(prompt)
            else:
                logging.info(f"Using {type(self.model).__name__} with string prompt")
                # Use the simple/enhanced model
                response = self.model.generate(prompt, self.current_theme)
            
            # Cache the response
            self.cache[prompt] = response
            self.cache_history.append(prompt)
            self._manage_cache()
            
            return response
            
        else:
            # Assume it's a game state object
            if hasattr(prompt_or_game_state, 'current_player'):
                current_player = prompt_or_game_state.current_player
            else:
                current_player = 1  # Default to player 1
                
            # Get the last move if it exists
            last_move = None
            if hasattr(prompt_or_game_state, 'last_move_column'):
                last_move = prompt_or_game_state.last_move_column
            
            # Create a cache key from game state
            board_str = str(prompt_or_game_state.board) if hasattr(prompt_or_game_state, 'board') else "no_board"
            move_count = sum(1 for row in prompt_or_game_state.board for cell in row if cell != 0) if hasattr(prompt_or_game_state, 'board') else 0
            # Include move count in cache key to ensure different stages are cached separately
            cache_key = f"state_{board_str[:50]}_{current_player}_{last_move}_{move_count}_{self.current_theme}"
            
            # Check if we have a narrative from memory for this theme and move count range
            # This creates groups of similar moves (early, mid, late game) to learn from
            move_phase = "early" if move_count < 10 else "mid" if move_count < 25 else "late"
            memory_key = f"{self.current_theme}_{move_phase}"
            
            # Only use memory for non-critical moves (not winning/game-deciding moves)
            can_use_memory = memory_key in self.session_memory and last_move is not None and move_count > 5
            
            # Return cached response if available and it's not a critical move
            if cache_key in self.cache:
                logging.info("Returning cached narrative response")
                return self.cache[cache_key]
                
            # Handle differently based on model type
            if isinstance(self.model, LocalLLMNarrator):
                logging.info("Using LocalLLMNarrator with game state - proper path")
                # Determine game phase based on move count
                move_count = 0
                if hasattr(prompt_or_game_state, 'board'):
                    move_count = sum(1 for row in prompt_or_game_state.board for cell in row if cell != 0)
                
                game_phase = "opening"
                if move_count > 20:
                    game_phase = "endgame"
                elif move_count > 8:
                    game_phase = "midgame"
                    
                # If the game phase is explicitly set on the game object, use that
                if hasattr(prompt_or_game_state, 'game_phase'):
                    game_phase = prompt_or_game_state.game_phase
                
                # Get the player making the move
                current_player = prompt_or_game_state.current_player
                last_move = prompt_or_game_state.last_move_column
                
                # Generate response with the battle narrator
                response = self.model.generate_narrative(
                    prompt_or_game_state, 
                    current_player,
                    last_move,
                    game_phase
                )
                
                # Store in cache to avoid repeated generation of similar narratives
                self.cache[cache_key] = response
                self.cache_history.append(response)
                
                # Store in memory for learning from past responses
                if memory_key not in self.session_memory:
                    self.session_memory[memory_key] = []
                if response not in self.session_memory[memory_key]:
                    self.session_memory[memory_key].append(response)
                
                # Manage cache size
                self._manage_cache()
                
                # Consider releasing memory when not generating
                self._consider_memory_cleanup()
                
                logging.info(f"Generated narrative: {response[:50]}...")
            else:
                logging.info(f"Using {type(self.model).__name__} with game state")
                # For non-LLM models, create a simple prompt from the game state
                prompt = self._create_prompt_from_game_state(prompt_or_game_state)
                
                # Check if we can use a response from memory
                if can_use_memory and random.random() < 0.3:  # 30% chance to use memory
                    # Select a random narrative from memory that's not the last one used
                    available_responses = [r for r in self.session_memory[memory_key] 
                                          if r != self.cache_history[-1] if self.cache_history]
                    if available_responses:
                        response = random.choice(available_responses)
                        logging.info("Using narrative from session memory")
                    else:
                        response = self.model.generate(prompt, self.current_theme)
                else:
                    response = self.model.generate(prompt, self.current_theme)
            
            # Cache the response
            self.cache[cache_key] = response
            self.cache_history.append(cache_key)
            self._manage_cache()
            
            return response
    
    def _create_prompt_from_game_state(self, game_state):
        """Create a simple prompt from a game state object"""
        # Extract basic information from game state
        try:
            current_player = game_state.current_player
            if hasattr(current_player, 'value'):
                current_player = current_player.value
                
            # Count pieces to determine game phase
            board = game_state.board
            move_count = sum(1 for row in board for cell in row if cell != 0)
            
            if move_count < 10:
                phase = "opening"
            elif move_count < 25:
                phase = "midgame"
            else:
                phase = "endgame"
                
            # Check for threats or winning opportunities
            threat_detected = False
            winning_move = False
            
            # Create a basic prompt
            return f"Generate a {self.current_theme} narrative for player {current_player} in the {phase} phase."
            
        except Exception as e:
            logging.error(f"Error creating prompt from game state: {e}")
            return f"Generate a {self.current_theme} narrative for the next move."
    
    def _generate_fallback_text(self, prompt):
        """Generate fallback text when the main model can't handle the prompt"""
        import random
        
        # Enhanced themed fallback system with more variety
        theme = self.current_theme.lower()
        
        # Get a unique-ish seed from the prompt to ensure some variability
        # This avoids returning the same response over and over
        prompt_hash = sum(ord(c) for c in prompt[:10]) if prompt else random.randint(0, 100)
        random.seed(prompt_hash)
        
        if theme == "fantasy":
            fantasy_responses = [
                "The arcane runes glow as strategies unfold on the magical battlefield.",
                "Ethereal forces shift as the next move materializes on the crystal grid.",
                "The elemental energies dance across the board, awaiting the next command.",
                "Ancient powers converge as the tactical standoff continues.",
                "The enchanted pieces resonate with magical intent as the game progresses.",
                "Whispered prophecies hint at the next strategic maneuver.",
                "The mystic battlefield shimmers with anticipation of the next move.",
                "Spectral advisors observe silently as the magical contest continues.",
                "The fate of the realm hangs in balance as the magical duel intensifies.",
                "Shimmering auras reveal the hidden strategies of each player."
            ]
            return random.choice(fantasy_responses)
        elif theme in ["sci-fi", "scifi"]:
            scifi_responses = [
                "Quantum algorithms calculate optimal move trajectories in the probability matrix.",
                "The holographic interface updates as strategic subroutines execute.",
                "Temporal fluctuations indicate a shift in tactical advantage.",
                "The neural network adapts to emerging patterns in the strategic grid.",
                "Subspace communications relay tactical data between command nodes.",
                "Energy signatures indicate intense computational activity in the matrix core.",
                "Predictive models simulate potential future board states with increasing precision.",
                "Reality distortion fields stabilize as the next move is processed.",
                "The strategic AI compiles vast datasets to determine optimal positioning.",
                "Dimensional analysis reveals hidden patterns in the quantum game field."
            ]
            return random.choice(scifi_responses)
        elif theme == "western":
            western_responses = [
                "Tumbleweed rolls across the dusty frontier as the standoff continues.",
                "The high noon sun casts long shadows as the next move is calculated.",
                "Spurs jingle as the frontier tacticians circle each other warily.",
                "The saloon falls silent as the strategic showdown intensifies.",
                "Dust devils swirl as the territorial dispute unfolds on the board.",
                "The marshal studies the gunslinger's tactics with narrowed eyes.",
                "Gold fever drives both sides to strategic extremes in this territorial dispute.",
                "The old prospector watches silently as the battle for claims continues.",
                "A distant train whistle punctuates the tension of the strategic duel.",
                "The frontier board records another claim in the battle for the golden mesa."
            ]
            return random.choice(western_responses)
        else:
            # Generic responses with more variety
            generic_responses = [
                "The strategic battle continues as positions are fortified.",
                "Both sides maneuver for advantage in this battle of wits.",
                "Tactical considerations shape the developing board position.",
                "The game continues as both players plot their next moves carefully.",
                "A careful assessment of the board reveals multiple strategic possibilities.",
                "The balance of power shifts subtly with each calculated move.",
                "Strategic depth builds as the pieces align in meaningful patterns.",
                "The game state advances as critical decisions are made.",
                "Positional advantages are sought as the contest unfolds.",
                "The strategic contest continues with careful calculation."
            ]
            return random.choice(generic_responses)

    def _manage_cache(self):
        """Manage the cache size by removing oldest entries"""
        # If cache is too big, remove oldest entries
        if len(self.cache) > self.max_cache_size:
            # Remove oldest entries
            overflow = len(self.cache) - self.max_cache_size
            for i in range(overflow):
                if i < len(self.cache_history):
                    key = self.cache_history[i]
                    if key in self.cache:
                        del self.cache[key]
            
            # Update history
            self.cache_history = self.cache_history[overflow:]
            
            logging.info(f"Cache cleaned: removed {overflow} items") 

    def _consider_memory_cleanup(self):
        """
        Occasionally release memory when possible
        This helps prevent memory leaks during long sessions
        """
        # Only run cleanup occasionally (10% chance)
        if random.random() < 0.1:
            try:
                # Force garbage collection
                import gc
                gc.collect()
                
                # If CUDA is available, try to clear the CUDA cache
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logging.info("Performed memory cleanup")
            except Exception as e:
                logging.warning(f"Error during memory cleanup: {e}")
                pass 

    def _generate_with_timeout(self, prompt, timeout=5, context_length=None):
        """
        Generate text with a timeout to prevent hanging.
        
        Args:
            prompt (str): The prompt to send to the model
            timeout (int): Timeout in seconds (default: 5)
            context_length (int): Maximum context length (default: from env or 128)
            
        Returns:
            str: The generated text or a fallback message if generation times out
        """
        # Get timeout from environment variable or use the provided value
        timeout = int(os.environ.get("GENERATION_TIMEOUT", timeout))
        
        # Get context length from environment variable or use the provided value
        context_length = int(os.environ.get("MAX_CONTEXT_LENGTH", context_length or 128))
        
        logging.info(f"Generating with timeout: {timeout}s, context length: {context_length}")
        
        # Ultra-optimized parameters for much better performance
        ultra_params = {
            "max_new_tokens": 30,  # Generate a short response for speed
            "temperature": 0.7,    # Some creativity but not too wild
            "top_p": 0.9,          # Filter out low probability tokens
            "do_sample": True,     # Use sampling for more diverse responses
            "num_beams": 1,        # No beam search for speed
            "early_stopping": True,
            "num_return_sequences": 1,  # Only one sequence for speed
        }
        
        # If prompt is too long, truncate it
        if len(prompt) > context_length * 2:
            original_length = len(prompt)
            prompt = prompt[:context_length * 2]
            logging.warning(f"Truncated prompt from {original_length} to {len(prompt)} chars")
        
        # If timeout is very low, just return a placeholder
        if timeout < 2:
            return "The battle continues with tactical maneuvers from both sides."
        
        try:
            # Use ThreadPoolExecutor to handle timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._generate_text, prompt, ultra_params
                )
                
                try:
                    result = future.result(timeout=timeout)
                    return result
                except TimeoutError:
                    # Cancel the future to stop generation
                    future.cancel()
                    logging.warning(f"Text generation timed out after {timeout} seconds")
                    return "The battle intensifies as both sides maneuver for position."
                
        except Exception as e:
            logging.error(f"Error in _generate_with_timeout: {e}")
            return "The strategic contest continues with careful positioning."

    def cleanup_resources(self):
        """Clean up any resources before application exit"""
        logging.info("Cleaning up model resources")
        try:
            # Clean up the battle narrator if it exists
            if self.battle_narrator is not None:
                # Set to None to allow garbage collection
                narrator = self.battle_narrator
                self.battle_narrator = None
                
                # If the narrator has a cleanup method, call it
                if hasattr(narrator, 'cleanup'):
                    narrator.cleanup()
                
                # Clear any references to large objects
                if hasattr(narrator, 'model'):
                    narrator.model = None
                if hasattr(narrator, 'tokenizer'):
                    narrator.tokenizer = None
                if hasattr(narrator, 'generator'):
                    narrator.generator = None
                
                # Force garbage collection
                try:
                    import gc
                    gc.collect()
                except ImportError:
                    pass
                
            logging.info("Model resources cleaned up successfully")
        except Exception as e:
            logging.error(f"Error cleaning up model resources: {e}")

    def generate_narrative(self, game_state, current_player, 
                          move_column=None, game_phase="midgame"):
        """Generate a narrative for the current game state"""
        try:
            if self.battle_narrator:
                logging.info(f"Generate narrative called with: {type(game_state)}")
                logging.info(f"Model loaded: {self.is_loaded}, Model type: {type(self.battle_narrator).__name__}")
                
                # Use the proper narrator
                if isinstance(game_state, dict) or isinstance(game_state, str):
                    # Simple string or dict prompt - use fallback
                    logging.info("Using unified model loader with simple prompt - fallback path")
                    return self.battle_narrator.generate_narrative(game_state, current_player, 
                                                                  move_column, game_phase)
                else:
                    # Game state object - proper path
                    logging.info("Using unified model loader with game state - proper path")
                    return self.battle_narrator.generate_narrative(game_state, current_player, 
                                                                  move_column, game_phase)
            else:
                logging.warning("No battle narrator available")
                return f"Move made in column {move_column if move_column is not None else 'unknown'}."
        except Exception as e:
            logging.error(f"Error in generate_narrative: {e}")
            return f"The battle continues in column {move_column if move_column is not None else 'unknown'}."
            
    def set_theme(self, theme):
        """Set the current theme for narrative generation"""
        self.current_theme = theme
        if self.battle_narrator and hasattr(self.battle_narrator, 'current_theme'):
            self.battle_narrator.current_theme = theme
            # Re-initialize theme context
            if hasattr(self.battle_narrator, '_initialize_theme_context'):
                self.battle_narrator._initialize_theme_context(theme)
                
    def _generate_with_timeout(self, prompt, timeout=5, context_length=None):
        """
        Generate text with a timeout to prevent hanging.
        
        Args:
            prompt (str): The prompt to send to the model
            timeout (int): Timeout in seconds (default: 5)
            context_length (int): Maximum context length (default: from env or 128)
            
        Returns:
            str: The generated text or a fallback message if generation times out
        """
        # Get timeout from environment variable or use the provided value
        timeout = int(os.environ.get("GENERATION_TIMEOUT", timeout))
        
        # Get context length from environment variable or use the provided value
        context_length = int(os.environ.get("MAX_CONTEXT_LENGTH", context_length or 128))
        
        logging.info(f"Generating with timeout: {timeout}s, context length: {context_length}")
        
        # Ultra-optimized parameters for much better performance
        ultra_params = {
            "max_new_tokens": 30,  # Generate a short response for speed
            "temperature": 0.7,    # Some creativity but not too wild
            "top_p": 0.9,          # Filter out low probability tokens
            "do_sample": True,     # Use sampling for more diverse responses
            "num_beams": 1,        # No beam search for speed
            "early_stopping": True,
            "num_return_sequences": 1,  # Only one sequence for speed
        }
        
        # If prompt is too long, truncate it
        if len(prompt) > context_length * 2:
            original_length = len(prompt)
            prompt = prompt[:context_length * 2]
            logging.warning(f"Truncated prompt from {original_length} to {len(prompt)} chars")
        
        # If timeout is very low, just return a placeholder
        if timeout < 2:
            return "The battle continues with tactical maneuvers from both sides."
        
        try:
            # Use ThreadPoolExecutor to handle timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._generate_text, prompt, ultra_params
                )
                
                try:
                    result = future.result(timeout=timeout)
                    return result
                except TimeoutError:
                    # Cancel the future to stop generation
                    future.cancel()
                    logging.warning(f"Text generation timed out after {timeout} seconds")
                    return "The battle intensifies as both sides maneuver for position."
                
        except Exception as e:
            logging.error(f"Error in _generate_with_timeout: {e}")
            return "The strategic contest continues with careful positioning." 