"""
speech_to_text.py

A simple and efficient speech-to-text module using Whisper library.

This module provides a `SpeechToText` class that leverages `faster-whisper` 
for transcribing speech from an audio file with optimizations for speed.

Dependencies:
- faster-whisper
- pydub
- numpy
"""
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pydub import AudioSegment

SAMPLE_RATE = 16000  # Whisper's required sample rate
PCM_NORMALIZATION_FACTOR = 32768.0 # Normalize 16-bit PCM audio samples

class SpeechToText:
    """
    A simple speech-to-text wrapper using the Whisper model.
    """

    def __init__(self, model: WhisperModel):
        """
        Initializes the Whisper model for transcription.

        Args:
            model (WhisperModel): A shared Whisper model instance.
        """
        self.model = model

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes speech from an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            str: The transcribed text.
        """
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(SAMPLE_RATE).set_channels(1)
        audio_bytes = np.array(audio.get_array_of_samples(),
                               dtype=np.float32) / PCM_NORMALIZATION_FACTOR
        segments, _ = self.model.transcribe(audio_bytes, word_timestamps=False)
        return " ".join(segment.text for segment in segments)

class SpeechStreamToText:
    """
    A class to stream and transcribe speech in real time using the Whisper model.
    """

    def __init__(self, model: WhisperModel):
        """
        Initializes the Whisper model for real-time speech recognition.

        Args:
            model (WhisperModel): A shared Whisper model instance.
        """
        self.model = model

    def transcribe(self, duration: int = 5) -> str:
        """
        Captures live audio and transcribes it in real time.

        Args:
            duration (int): Length of the recording in seconds.

        Returns:
            str: The transcribed text.
        """
        print("Listening...")
        audio_data = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                            channels=1, dtype="int16")
        sd.wait()

        # Convert audio data to floating point for Whisper
        audio_bytes = audio_data.astype(np.float32) / PCM_NORMALIZATION_FACTOR

        print("Transcribing...")
        segments, _ = self.model.transcribe(audio_bytes, word_timestamps=False)
        return " ".join(segment.text for segment in segments)

if __name__ == "__main__":
    # int 8 makes inference faster using 8-bit integers instead of floating point.
    # Note to self: test "cuda" instead of "auto" to see which is faster

    # Test recorded audio transcription
    whisper_model = WhisperModel("tiny", device="auto", compute_type="int8")  # Load model
    stt = SpeechToText(whisper_model)
    SPEECH = "assets/audio/Sunset.m4a"
    TEXT = stt.transcribe(SPEECH)
    print("Transcription:", TEXT)

    # Test real-time streaming transcription
    # stream_stt = SpeechStreamToText(whisper_model)
    # print("Streaming Transcription:", stream_stt.transcribe(duration=1))
