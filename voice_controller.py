"""
Voice to Text Controller
"""

import speech_recognition as sr


def transcribe_audio(audio) -> str:
    """Transcribes audio data to text using Google Speech Recognition.

    Args:
        audio: Audio data to transcribe.

    Returns:
        The transcribed text as a string.
    """

    r = sr.Recognizer()
    return r.recognize_google(audio, language='en')


def convert_audio_to_text(audio_file) -> str:
    """Converts an audio file to text using Google Speech Recognition.

    Args:
        audio_file: Path to the audio file.

    Returns:
        The transcribed text as a string.
    """

    with sr.AudioFile(audio_file) as source:
        audio_data = sr.Recognizer().record(source)
        text = transcribe_audio(audio_data)
    return text
