"""
text_to_speech.py

A simple and efficient text-to-speech module using Coqui TTS library.

This module provides `TextToSpeech` class that leverages Coqui `TTS.api`
for converting text to audio with optimizations for speed.

Dependencies:
- 
"""
import os
import platform
import subprocess
import tempfile
from TTS.api import TTS

MODEL = "tts_models/en/ljspeech/tacotron2-DDC"
class TextToSpeech:
    """
     A simple text-to-speech wrapper using the Coqui TTS model.
    """
    def __init__(self, model: str = MODEL):
        """
        Initializes the TTS model.

        Args:
            model (str): The model to use for synthesis.
        """
        self.tts = TTS(model)

    def play_audio(self, file_path: str):
        """
        Plays an audio file based on the operating system.

        Args:
            file_path (str): Path to the audio file.
        """
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", file_path], check=True)
            elif system == "Windows":
                if "ARM" in platform.machine():  # ARM Windows
                    subprocess.run(["powershell", "-c",
                                    f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"],
                                    check=True)
                else:  # Regular Windows
                    subprocess.run(["cmd", "/c", f"start /b {file_path}"], check=True)
            elif system == "Linux":
                if os.system("command -v aplay") == 0:
                    subprocess.run(["aplay", file_path], check=True)
                elif os.system("command -v ffplay") == 0:
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path], check=True)
                else:
                    print("No supported audio player found on Linux.")
            else:
                print(f"Unsupported OS: {system}")
        except Exception as e:
            print(f"Error playing audio: {e}")
        finally:
            # Delete the temp file after playback
            if os.path.exists(file_path):
                os.remove(file_path)

    def speak(self, text: str):
        """
        Converts text to speech, plays it, and removes the file after playback.

        Args:
            text (str): The text to synthesize.
        """
        temp_audio_path = os.path.join(tempfile.gettempdir(), "temp_speech.wav")

        # Generate speech and save to temp file (on disk)
        self.tts.tts_to_file(text=text, file_path=temp_audio_path)

        # Play the speech and delete the file
        self.play_audio(temp_audio_path)

if __name__ == "__main__":
    tts = TextToSpeech()
    tts.speak("Hello! Welcome to the game!")
