## Using the `speech_to_text` module
- Try `record_and_transcribe` by running `python -m speech_to_text.record_and_transcribe`
- Import: `from speech_to_text/record_and_transcribe import record_and_transcribe`
- Specify the following parameters in the function
    - Recording duration `duration`, 5 seconds default
    - Model size `model_size`, `base`, `small`, `tiny`

### Details: 
- When you the function is run, the device microphone is automatically turned on for the set duration and begins recording the player's audio.
- The function returns a `transcription` as string of the player's audio message
- NB: No need to handle the audio file or memory. The function deletes the audio file after transcription
- Then pass this trancription as the ai prompt finstead of waiting for a text prompt 

