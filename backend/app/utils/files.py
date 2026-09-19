from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from app.utils.config import get_settings


def save_upload(image_bgr: np.ndarray, filename: str) -> str:
    settings = get_settings()
    path = Path(settings.upload_dir) / filename
    cv2.imwrite(str(path), image_bgr)
    return str(path)


def save_processed(image_bgr: np.ndarray, analysis_id: str, stage: str) -> str:
    settings = get_settings()
    folder = Path(settings.processed_dir) / analysis_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{stage}.png"
    cv2.imwrite(str(path), image_bgr)
    return str(path)


def processed_url(analysis_id: str, stage: str) -> str:
    return f"/media/processed/{analysis_id}/{stage}.png"


def upload_url(filename: str) -> str:
    return f"/media/uploads/{filename}"
