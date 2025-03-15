"""
Text Generation Utilities - Common tools for text generation
"""
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable, Dict, List, Optional, Union

# Default timeout for text generation
DEFAULT_TIMEOUT = 5  # seconds


def generate_with_timeout(
    generate_fn: Callable[[str, Any], str], 
    prompt: str,
    timeout: int = DEFAULT_TIMEOUT,
    **kwargs: Any
) -> str:
    """
    Generate text with a timeout to prevent hanging.
    
    Args:
        generate_fn: The function to call for text generation
        prompt: The prompt to generate from
        timeout: Timeout in seconds
        **kwargs: Additional keyword arguments to pass to generate_fn
        
    Returns:
        str: The generated text or a fallback message if generation times out
    """
    # If timeout is very low, just return a placeholder
    if timeout < 2:
        return "The strategic battle continues with tactical maneuvers."
    
    try:
        # Use ThreadPoolExecutor to handle timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(generate_fn, prompt, **kwargs)
            
            try:
                result = future.result(timeout=timeout)
                return result
            except TimeoutError:
                # Cancel the future to stop generation
                future.cancel()
                logging.warning(f"Text generation timed out after {timeout} seconds")
                return "The battle intensifies as both sides maneuver for position."
            
    except Exception as e:
        logging.error(f"Error in generate_with_timeout: {e}")
        return "The strategic contest continues with careful positioning."


def truncate_prompt(prompt: str, max_tokens: int = 128) -> str:
    """
    Truncate a prompt to a maximum number of estimated tokens.
    
    Args:
        prompt: The prompt to truncate
        max_tokens: Maximum estimated token length
        
    Returns:
        str: The truncated prompt
    """
    # Simple estimation: 1 token ≈ 4 characters for English text
    estimated_char_limit = max_tokens * 4
    
    if len(prompt) <= estimated_char_limit:
        return prompt
    
    # Log that we're truncating
    logging.warning(f"Truncating prompt from {len(prompt)} to ~{estimated_char_limit} chars")
    
    # Keep the first part for context
    truncated = prompt[:estimated_char_limit]
    
    # Try to truncate at a sentence or paragraph boundary if possible
    for ending in [". ", ".\n", "! ", "?\n"]:
        last_period = truncated.rfind(ending)
        if last_period > estimated_char_limit * 0.7:  # At least 70% of the text
            return truncated[:last_period + 1]
    
    return truncated


def select_themed_response(theme: str) -> str:
    """
    Select a themed response from a predefined list.
    
    Args:
        theme: The theme to use
        
    Returns:
        str: A themed response
    """
    if theme.lower() == "fantasy":
        fantasy_responses = [
            "The mystical energies swirl as the battle unfolds on the sacred grid.",
            "Ancient runes glow with arcane power as the strategic duel continues.",
            "The ethereal forces of light and shadow continue their eternal contest.",
            "Crystal shards resonate with magical energy as the tactical placement is made.",
            "The wizards channel elemental forces to guide their strategic formations.",
            "Arcane symbols illuminate the battlefield as the mystical duel progresses.",
            "The eldritch power shifts as the magical tokens align in new patterns.",
            "Enchanted pieces move across the mystical grid, seeking harmony and balance.",
            "The prophesied battle continues, with ancient powers seeking dominance.",
            "Spectral energies flow through the crystal matrix as the duel intensifies."
        ]
        return random.choice(fantasy_responses)
        
    elif theme.lower() in ["sci-fi", "scifi"]:
        scifi_responses = [
            "Quantum algorithms calculate optimal move trajectories in the probability matrix.",
            "The holographic interface updates as strategic subroutines execute.",
            "Temporal fluctuations indicate a shift in tactical advantage.",
            "The neural network adapts to emerging patterns in the strategic grid.",
            "Subspace communications relay tactical data between command nodes.",
            "Energy signatures indicate intense computational activity in the matrix core.",
            "Predictive models simulate potential future board states with precision.",
            "Reality distortion fields stabilize as the next move is processed.",
            "The strategic AI compiles vast datasets to determine optimal positioning.",
            "Dimensional analysis reveals hidden patterns in the quantum game field."
        ]
        return random.choice(scifi_responses)
        
    elif theme.lower() == "western":
        western_responses = [
            "Dust settles as the strategic standoff continues in the frontier town.",
            "The sun beats down on the tactical showdown between the rival factions.",
            "Tumbleweed rolls across the boardwalk as the next move is considered.",
            "Spurs jingle as the gunslingers circle the strategic battlefield.",
            "The saloon falls silent as the tactical maneuver unfolds.",
            "A hawk circles overhead, watching the dusty confrontation below.",
            "The sheriff and outlaws continue their calculated game of wits.",
            "The clock in the town square ticks as the strategic duel progresses.",
            "A gentle breeze stirs the dust as the pieces shift in the frontier battle.",
            "The tactical shootout continues as both sides seek the upper hand."
        ]
        return random.choice(western_responses)
        
    else:
        # Default/generic responses
        generic_responses = [
            "The strategic battle continues with careful positioning.",
            "Both sides analyze the board, seeking optimal positioning.",
            "The tactical contest unfolds with measured, deliberate moves.",
            "The game progresses as both players evaluate their options.",
            "Strategic calculations guide the next move in this tense contest.",
            "The battle of wits continues as the next piece falls into place.",
            "Careful planning and strategic thinking shape the ongoing match.",
            "The board state evolves, reflecting the strategic minds at work.",
            "Tactical considerations drive the progression of this strategic duel.",
            "The next move brings new strategic possibilities to the forefront."
        ]
        return random.choice(generic_responses) 