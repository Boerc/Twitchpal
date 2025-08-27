import os
from pydantic import BaseModel
from typing import List, Optional


class AppSettings(BaseModel):
    environment: str = os.getenv("APP_ENV", "development")
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))
    cors_origins: List[str] = (
        os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    )

    # Auth
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "43200"))  # 30 days

    # Google / Gemini
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    google_project: Optional[str] = os.getenv("GOOGLE_PROJECT")
    google_region: Optional[str] = os.getenv("GOOGLE_REGION", "us-central1")

    # TTS/STT flags
    enable_google_tts: bool = os.getenv("ENABLE_GOOGLE_TTS", "true").lower() == "true"
    enable_google_stt: bool = os.getenv("ENABLE_GOOGLE_STT", "true").lower() == "true"

    # Screenshot
    screenshot_interval_seconds: int = int(os.getenv("SCREENSHOT_INTERVAL_SECONDS", "8"))

    # Twitch
    twitch_enabled: bool = os.getenv("TWITCH_ENABLED", "false").lower() == "true"
    twitch_token: Optional[str] = os.getenv("TWITCH_OAUTH_TOKEN")
    twitch_client_id: Optional[str] = os.getenv("TWITCH_CLIENT_ID")
    twitch_client_secret: Optional[str] = os.getenv("TWITCH_CLIENT_SECRET")
    twitch_channel: Optional[str] = os.getenv("TWITCH_CHANNEL")

    # Privacy
    blur_regions: str = os.getenv("BLUR_REGIONS", "")  # format: x,y,w,h; x,y,w,h


settings = AppSettings()
