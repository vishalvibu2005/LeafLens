from __future__ import annotations

import cv2
import numpy as np


def mask_to_bgr(mask: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)


def crop_to_bbox(image_bgr: np.ndarray, bbox: dict, padding: int = 8) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    x = max(0, bbox["x"] - padding)
    y = max(0, bbox["y"] - padding)
    x2 = min(w, bbox["x"] + bbox["width"] + padding)
    y2 = min(h, bbox["y"] + bbox["height"] + padding)
    return image_bgr[y:y2, x:x2]
