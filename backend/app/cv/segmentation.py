"""Classical leaf segmentation: HSV/LAB thresholding, Otsu, morphology.

This is used both as the primary segmentation method (since no trained
YOLO segmentation weights ship with this project by default — see
app/models/detector.py) and as an IPCV-viva-friendly demonstration
alongside any learned detector.
"""
from __future__ import annotations

import cv2
import numpy as np


def hsv_green_mask(image_bgr: np.ndarray) -> np.ndarray:
    """Threshold likely leaf/plant pixels in HSV space.

    Broad green + yellow-green + brown (senescent leaf) hue range.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    lower1 = np.array([15, 25, 25])
    upper1 = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower1, upper1)
    return mask


def lab_mask(image_bgr: np.ndarray) -> np.ndarray:
    """Threshold using the LAB 'a' channel (green-red axis)."""
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    a_channel = lab[:, :, 1]
    _, mask = cv2.threshold(a_channel, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return mask


def otsu_gray_mask(image_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return mask


def combine_masks(*masks: np.ndarray) -> np.ndarray:
    combined = masks[0].copy()
    for m in masks[1:]:
        combined = cv2.bitwise_or(combined, m)
    return combined


def clean_mask(mask: np.ndarray) -> np.ndarray:
    """Morphological opening + closing to remove noise and fill small holes."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=2)
    return closed


def largest_component_mask(mask: np.ndarray) -> np.ndarray:
    """Keep only the largest connected component (assumed to be the leaf)."""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1:
        return mask
    largest_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    out = np.zeros_like(mask)
    out[labels == largest_label] = 255
    return out


def segment_leaf(image_bgr: np.ndarray) -> dict:
    """Full classical segmentation pipeline.

    Returns the binary mask plus a boolean indicating whether a
    plausible leaf-sized region was found at all.
    """
    hsv_m = hsv_green_mask(image_bgr)
    lab_m = lab_mask(image_bgr)
    combined = combine_masks(hsv_m, lab_m)
    cleaned = clean_mask(combined)
    main = largest_component_mask(cleaned)

    total_pixels = image_bgr.shape[0] * image_bgr.shape[1]
    leaf_pixels = int(np.count_nonzero(main))
    coverage = leaf_pixels / total_pixels if total_pixels else 0.0

    # A very small isolated region is more likely noise than a real leaf.
    found = coverage >= 0.01

    return {
        "hsv_mask": hsv_m,
        "lab_mask": lab_m,
        "otsu_mask": otsu_gray_mask(image_bgr),
        "combined_mask": combined,
        "mask": main,
        "coverage": coverage,
        "found": found,
    }


def find_leaf_instances(mask: np.ndarray, min_area_ratio: float = 0.008) -> list[dict]:
    """Split a binary mask into individual leaf-instance components.

    This is what powers multi-leaf detection when no learned instance
    segmentation model (e.g. YOLO11-seg) is installed: each sufficiently
    large connected component is treated as one leaf instance. It is a
    real classical-CV technique, not a placeholder.
    """
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    total = mask.shape[0] * mask.shape[1]
    instances = []
    for label_id in range(1, num_labels):
        area = stats[label_id, cv2.CC_STAT_AREA]
        if area / total < min_area_ratio:
            continue
        x = int(stats[label_id, cv2.CC_STAT_LEFT])
        y = int(stats[label_id, cv2.CC_STAT_TOP])
        w = int(stats[label_id, cv2.CC_STAT_WIDTH])
        h = int(stats[label_id, cv2.CC_STAT_HEIGHT])
        inst_mask = np.zeros_like(mask)
        inst_mask[labels == label_id] = 255
        instances.append({
            "bbox": {"x": x, "y": y, "width": w, "height": h},
            "mask": inst_mask,
            "area": int(area),
        })
    instances.sort(key=lambda d: d["area"], reverse=True)
    return instances


def apply_mask_overlay(image_bgr: np.ndarray, mask: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    overlay = image_bgr.copy()
    color_layer = np.zeros_like(image_bgr)
    color_layer[:, :] = (52, 199, 89)  # emerald-ish BGR
    mask_bool = mask > 0
    overlay[mask_bool] = cv2.addWeighted(image_bgr, 1 - alpha, color_layer, alpha, 0)[mask_bool]
    return overlay
