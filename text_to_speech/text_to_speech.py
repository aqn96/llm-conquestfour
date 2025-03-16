"""
text_to_speech.py

A simple and efficient text-to-speech module using Coqui TTS library.

This module provides `TextToSpeech` class that leverages Coqui `TTS.api`
for converting text to audio with optimizations for speed.

Dependencies:
- 
"""

class TextToSpeech:
    """
    A simple text-to-speech wrapper using Coqui TTS
    """
    def __init__(self):
        """
        Initializes the TTS system.
        """
        self.local_tts = TTS("")
        