from typing import Optional
import os

from ..config import settings

# Google Cloud TTS (preferred)
try:
    from google.cloud import texttospeech
except Exception:  # pragma: no cover
    texttospeech = None  # type: ignore

# Local fallback
try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover
    pyttsx3 = None  # type: ignore


def synthesize_speech(text: str) -> Optional[bytes]:
    # Cloud path returns audio bytes (MP3)
    if settings.enable_google_tts and texttospeech is not None and (
        settings.google_project or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    ):
        try:
            client = texttospeech.TextToSpeechClient()
            input_text = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
            return bytes(response.audio_content)
        except Exception:
            pass
    # Local fallback: speak via speakers (no bytes available)
    if pyttsx3 is not None:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            return None
    return None
