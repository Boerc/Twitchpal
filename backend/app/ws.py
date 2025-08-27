from typing import List, Dict, Any
from fastapi import WebSocket
from asyncio import Lock


class WebSocketManager:
    def __init__(self) -> None:
        self._active_connections: List[WebSocket] = []
        self._lock: Lock = Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self._active_connections:
                self._active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        dead: List[WebSocket] = []
        for connection in list(self._active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        if dead:
            async with self._lock:
                for d in dead:
                    if d in self._active_connections:
                        self._active_connections.remove(d)
