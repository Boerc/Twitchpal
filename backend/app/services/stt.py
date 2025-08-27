from typing import Optional

from ..config import settings

try:
    from google.cloud import speech
except Exception:  # pragma: no cover
    speech = None  # type: ignore


def transcribe_audio(wav_bytes: bytes, language_code: str = "en-US") -> Optional[str]:
    if not settings.enable_google_stt or speech is None:
        return None
    try:
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=wav_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        response = client.recognize(config=config, audio=audio)
        for result in response.results:
            if result.alternatives:
                return result.alternatives[0].transcript
    except Exception:
        return None
    return None
