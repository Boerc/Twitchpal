import base64
import io
from typing import List, Tuple

import mss
import numpy as np
import cv2

from ..config import settings


def _parse_blur_regions(config: str) -> List[Tuple[int, int, int, int]]:
    regions: List[Tuple[int, int, int, int]] = []
    if not config:
        return regions
    for chunk in config.split(";"):
        parts = chunk.split(",")
        if len(parts) != 4:
            continue
        try:
            x, y, w, h = [int(p.strip()) for p in parts]
            regions.append((x, y, w, h))
        except Exception:
            continue
    return regions


def capture_screenshot() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
        # Drop alpha channel if present
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img


def apply_privacy_blur(img: np.ndarray) -> np.ndarray:
    regions = _parse_blur_regions(settings.blur_regions)
    blurred = img.copy()
    for (x, y, w, h) in regions:
        roi = blurred[y:y+h, x:x+w]
        if roi.size == 0:
            continue
        roi_blur = cv2.GaussianBlur(roi, (51, 51), 0)
        blurred[y:y+h, x:x+w] = roi_blur
    return blurred


def to_png_bytes(img: np.ndarray, max_width: int = 1280) -> bytes:
    # Downscale for bandwidth
    h, w = img.shape[:2]
    if w > max_width:
        scale = max_width / float(w)
        new_size = (int(w * scale), int(h * scale))
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode('.png', img)
    if not ok:
        raise RuntimeError("Failed to encode image to PNG")
    return buf.tobytes()


def to_base64_data_url(png_bytes: bytes) -> str:
    b64 = base64.b64encode(png_bytes).decode('ascii')
    return f"data:image/png;base64,{b64}"
