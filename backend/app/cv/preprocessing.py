"""Classical preprocessing: resize, denoise, color-space conversion, contrast."""
from __future__ import annotations

import cv2
import numpy as np

MAX_SIDE = 1024


def resize_preserve_aspect(image_bgr: np.ndarray, max_side: int = MAX_SIDE) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale >= 1.0:
        return image_bgr
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)


def denoise(image_bgr: np.ndarray, method: str = "gaussian") -> np.ndarray:
    if method == "median":
        return cv2.medianBlur(image_bgr, 5)
    return cv2.GaussianBlur(image_bgr, (5, 5), 0)


def to_hsv(image_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)


def to_lab(image_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)


def enhance_contrast_clahe(image_bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    merged = cv2.merge((l2, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def preprocess_pipeline(image_bgr: np.ndarray) -> dict[str, np.ndarray]:
    """Run the full classical preprocessing pipeline.

    Returns a dict of intermediate stages so the frontend can display each
    step of the pipeline, not just the final result.
    """
    resized = resize_preserve_aspect(image_bgr)
    denoised = denoise(resized, "gaussian")
    enhanced = enhance_contrast_clahe(denoised)
    return {
        "resized": resized,
        "denoised": denoised,
        "enhanced": enhanced,
        "final": enhanced,
    }
