"""Contour extraction and geometric measurement using OpenCV."""
from __future__ import annotations

import cv2
import numpy as np


def find_largest_contour(mask: np.ndarray):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)


def contour_geometry(contour) -> dict:
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    x, y, w, h = cv2.boundingRect(contour)
    hull = cv2.convexHull(contour)
    hull_area = float(cv2.contourArea(hull))

    return {
        "area": area,
        "perimeter": perimeter,
        "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
        "hull": hull,
        "hull_area": hull_area,
    }


def draw_contour_overlay(image_bgr: np.ndarray, contour, hull) -> np.ndarray:
    out = image_bgr.copy()
    cv2.drawContours(out, [contour], -1, (46, 204, 113), 2)      # leaf contour, green
    cv2.drawContours(out, [hull], -1, (52, 152, 219), 2)          # convex hull, blue
    x, y, w, h = cv2.boundingRect(contour)
    cv2.rectangle(out, (x, y), (x + w, y + h), (241, 196, 15), 2)  # bbox, yellow
    return out


def draw_detection_overlay(image_bgr: np.ndarray, detections: list[dict]) -> np.ndarray:
    out = image_bgr.copy()
    for det in detections:
        b = det["bbox"]
        x, y, w, h = b["x"], b["y"], b["width"], b["height"]
        cv2.rectangle(out, (x, y), (x + w, y + h), (46, 204, 113), 2)
        label = f"Leaf {det['id']} - {det['confidence'] * 100:.1f}%"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(out, (x, y - th - 10), (x + tw + 6, y), (46, 204, 113), -1)
        cv2.putText(out, label, (x + 3, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return out
