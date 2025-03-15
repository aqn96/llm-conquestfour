"""
Main module
"""
from .speech_to_text import SpeechToText

def main():
    """
    Main function to run the speech to text module
    """
    stt = SpeechToText(model_size="tiny")
    speech = "audio/121st Ave SE.m4a"
    text = stt.transcribe(speech)
    print("Transcription:", text)

if __name__ == "__main__":
    main()
