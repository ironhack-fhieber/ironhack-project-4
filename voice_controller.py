import speech_recognition as sr


def transcribe_audio(audio) -> str:
    """
    Transcribes audio data to text using Google's speech recognition API.
    """
    r = sr.Recognizer()
    return r.recognize_google(audio, language='en')


def convert_audio_to_text(audio_file) -> str:
    with sr.AudioFile(audio_file) as source:
        audio_data = sr.Recognizer().record(source)
        text = transcribe_audio(audio_data)
    return text
