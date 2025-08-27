from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FeatureState:
    screen_reading_enabled: bool = False
    chat_moderation_enabled: bool = False
    tts_enabled: bool = True
    stt_enabled: bool = True
    selected_personality: str = "Analytical Expert"
    last_commentary: Optional[str] = None


state = FeatureState()
