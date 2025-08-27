import asyncio
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Body

from .config import settings
from .ws import WebSocketManager
from .state import state
from .auth import authenticate_admin, create_access_token, get_current_user
from .services.screenshot import capture_screenshot, apply_privacy_blur, to_png_bytes, to_base64_data_url
from .services.vision import analyze_image
from .personalities import build_system_prompt

app = FastAPI(title="Stream Companion API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")
ws_manager = WebSocketManager()


@router.post("/login")
async def login(username: str = Body(...), password: str = Body(...)) -> Dict[str, Any]:
    if not authenticate_admin(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/state")
async def get_state(_user: str = Depends(get_current_user)) -> Dict[str, Any]:
    return state.__dict__


@router.post("/toggle")
async def toggle(
    screen_reading_enabled: bool | None = Body(None),
    chat_moderation_enabled: bool | None = Body(None),
    tts_enabled: bool | None = Body(None),
    stt_enabled: bool | None = Body(None),
    selected_personality: str | None = Body(None),
    _user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    if screen_reading_enabled is not None:
        state.screen_reading_enabled = screen_reading_enabled
    if chat_moderation_enabled is not None:
        state.chat_moderation_enabled = chat_moderation_enabled
    if tts_enabled is not None:
        state.tts_enabled = tts_enabled
    if stt_enabled is not None:
        state.stt_enabled = stt_enabled
    if selected_personality:
        state.selected_personality = selected_personality
    return state.__dict__


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keepalive
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)


async def background_loop() -> None:
    await asyncio.sleep(1)
    while True:
        try:
            if state.screen_reading_enabled:
                img = capture_screenshot()
                img = apply_privacy_blur(img)
                png_bytes = to_png_bytes(img)
                data_url = to_base64_data_url(png_bytes)
                system_prompt = build_system_prompt(state.selected_personality)
                commentary = analyze_image(png_bytes, system_prompt) or ""
                if commentary:
                    state.last_commentary = commentary
                await ws_manager.broadcast({
                    "type": "frame",
                    "image": data_url,
                    "commentary": state.last_commentary,
                })
        except Exception:
            pass
        await asyncio.sleep(settings.screenshot_interval_seconds)


@app.on_event("startup")
async def on_startup() -> None:
    asyncio.create_task(background_loop())


app.include_router(router)

