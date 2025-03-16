"""
audio_recorder.py

A simple and efficient module for recording audio from the player's microphone.

This module provides an `AudioRecorder` class that captures and saves audio
for later processing, ensuring optimal resource usage.

Dependencies:
- sounddevice
- numpy
- scipy
"""

import os
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# Default recording parameters
SAMPLE_RATE = 16000  # Whisper-compatible sample rate
CHANNELS = 1  # Mono recording
AUDIO_FORMAT = np.int16  # 16-bit PCM


class AudioRecorder:
    """
    A simple audio recording module for capturing microphone input.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE, channels: int = CHANNELS):
        """
        Initializes the audio recorder.

        Args:
            sample_rate (int): The sample rate of the recording.
            channels (int): The number of audio channels (1 for mono, 2 for stereo).
        """
        self.sample_rate = sample_rate
        self.channels = channels

    def record(self, duration: int = 5) -> str:
        """
        Records audio from the microphone and saves it as a temporary file.

        Args:
            duration (int): Duration of the recording in seconds.

        Returns:
            str: The path to the recorded audio file.
        """
        print(f"Recording for {duration} seconds...")
        audio_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=AUDIO_FORMAT,
        )
        sd.wait()

        # Save recording to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            audio_path = temp_audio.name

        write(audio_path, self.sample_rate, audio_data)
        print(f"Recording saved to: {audio_path}")

        return audio_path

    def delete_audio(self, file_path: str):
        """
        Deletes a recorded audio file.

        Args:
            file_path (str): Path to the audio file.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")


if __name__ == "__main__":
    recorder = AudioRecorder()
    audio_file = recorder.record(duration=5)

    # Delete the audio file after use
    recorder.delete_audio(audio_file)
