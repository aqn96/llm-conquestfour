"""
speech_to_text.py

A simple and efficient speech-to-text module using Whisper.

This module provides a `SpeechToText` class that leverages `faster-whisper` 
for transcribing speech from an audio file with optimizations for speed.

Dependencies:
- faster-whisper
- pydub
- numpy
"""
import numpy as np
from faster_whisper import WhisperModel
from pydub import AudioSegment

PCM_NORMALIZATION_FACTOR = 32768.0 # Normalize 16-bit PCM audio samples

class SpeechToText:
    """
    A simple speech-to-text wrapper using the Whisper model.
    """

    def __init__(self, model_size: str = "base"):
        """
        Initializes the Whisper model for transcription.

        Args:
            model_size (str): The model size to use (tiny, base, or small)
        """
        # int 8 makes inference faster using 8-bit integers instead of floating point.
        # Note to self: test "cuda" instead of "auto" to see which is faster
        self.model = WhisperModel(model_size, device="auto", compute_type="int8")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes speech from an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            str: The transcribed text.
        """
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio_bytes = np.array(audio.get_array_of_samples(),
                               dtype=np.float32) / PCM_NORMALIZATION_FACTOR
        segments, _ = self.model.transcribe(audio_bytes, word_timestamps=False)

        text = " ".join(segment.text for segment in segments)

        return text


if __name__ == "__main__":
    stt = SpeechToText(model_size="tiny")
    SPEECH = "speech_to_text/audio/Sunset.m4a"
    TEXT = stt.transcribe(SPEECH)
    print("Transcription:", TEXT)
