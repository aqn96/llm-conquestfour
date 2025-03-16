"""
record_and_transcribe.py

This script integrates the AudioRecorder and SpeechToText modules to:
1. Record audio from the microphone.
2. Convert recorded speech into text using Whisper.

Dependencies:
- audio_recorder.py
- speech_to_text.py
"""

from speech_to_text.audio_recorder import AudioRecorder
from speech_to_text.speech_to_text import SpeechToText

def record_and_transcribe(duration: int = 5, model_size: str = "base"):
    """
    Records audio from the microphone and transcribes it to text.

    Args:
        duration (int): The length of the recording in seconds.
        model_size (str): The Whisper model size to use for transcription.

    Returns:
        str: The transcribed text.
    """
    # Initialize modules
    recorder = AudioRecorder()
    stt = SpeechToText(model_size=model_size)

    # Record audio
    audio_file = recorder.record(duration=duration)

    # Transcribe audio
    transcription = stt.transcribe(audio_file)
    print("Transcription:", transcription)

    # Clean up by deleting the recorded file
    recorder.delete_audio(audio_file)

    return transcription

if __name__ == "__main__":
    record_and_transcribe(duration=5, model_size="tiny")
