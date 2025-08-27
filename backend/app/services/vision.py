from typing import Optional
import os

try:
    import google.generativeai as genai
    from google.generativeai import types as genai_types
except Exception:  # pragma: no cover
    genai = None  # type: ignore

from ..config import settings


def _ensure_configured() -> None:
    if genai is None:
        return
    api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def analyze_image(image_bytes: bytes, system_prompt: str) -> Optional[str]:
    try:
        _ensure_configured()
        if genai is None or not (settings.google_api_key or os.getenv("GOOGLE_API_KEY")):
            return None
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=system_prompt,
            safety_settings={
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            },
        )
        image_part = genai_types.Part.from_data(mime_type="image/png", data=image_bytes)
        prompt = [image_part, "Provide a concise, entertaining commentary relevant to the image."]
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip() if resp else None
        if text:
            # keep it short
            if len(text) > 280:
                text = text[:277] + "..."
        return text or None
    except Exception:
        return None
