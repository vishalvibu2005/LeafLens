"""Shape, color, and texture feature extraction for a segmented leaf."""
from __future__ import annotations

import math

import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.color import rgb2gray
from skimage.util import img_as_ubyte


def shape_features(contour, hull_area: float) -> dict:
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    x, y, w, h = cv2.boundingRect(contour)

    aspect_ratio = (h / w) if w > 0 else 0.0
    circularity = (4 * math.pi * area / (perimeter ** 2)) if perimeter > 0 else 0.0
    solidity = (area / hull_area) if hull_area > 0 else 0.0
    extent = (area / (w * h)) if (w * h) > 0 else 0.0
    equivalent_diameter = math.sqrt(4 * area / math.pi) if area > 0 else 0.0

    return {
        "area": round(area, 2),
        "perimeter": round(perimeter, 2),
        "width": int(w),
        "height": int(h),
        "aspect_ratio": round(aspect_ratio, 3),
        "circularity": round(min(circularity, 1.0), 3),
        "solidity": round(min(solidity, 1.0), 3),
        "extent": round(min(extent, 1.0), 3),
        "convex_hull_area": round(hull_area, 2),
        "equivalent_diameter": round(equivalent_diameter, 2),
    }


def color_features(image_bgr: np.ndarray, mask: np.ndarray) -> dict:
    if mask.shape[:2] != image_bgr.shape[:2]:
        mask = cv2.resize(
            mask,
            (image_bgr.shape[1], image_bgr.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

    mask_bool = mask > 0

    if not np.any(mask_bool):
        mask_bool = np.ones(mask.shape, dtype=bool)

    b, g, r = cv2.split(image_bgr)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)

    def m(channel):
        return float(np.mean(channel[mask_bool]))

    mean_r, mean_g, mean_b = m(r), m(g), m(b)
    dominant = "Green"
    if mean_r > mean_g and mean_r > mean_b:
        dominant = "Red/Brown"
    elif mean_b > mean_g and mean_b > mean_r:
        dominant = "Blue"

    green_intensity = mean_g - (mean_r + mean_b) / 2

    return {
        "rgb": {"r": round(mean_r, 1), "g": round(mean_g, 1), "b": round(mean_b, 1)},
        "hsv": {"h": round(m(h) * 2, 1), "s": round(m(s) / 255 * 100, 1), "v": round(m(v) / 255 * 100, 1)},
        "lab": {"l": round(m(l_ch), 1), "a": round(m(a_ch), 1), "b": round(m(b_ch), 1)},
        "dominant_color": dominant,
        "green_intensity": round(green_intensity, 2),
    }


def texture_features(image_bgr: np.ndarray, mask: np.ndarray) -> dict:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    x, y, w, h = cv2.boundingRect(mask)
    if w == 0 or h == 0:
        crop = gray
    else:
        crop = gray[y:y + h, x:x + w]

    if crop.size == 0:
        crop = gray

    crop = img_as_ubyte(crop / 255.0) if crop.dtype != np.uint8 else crop
    glcm = graycomatrix(
        crop,
        distances=[1],
        angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
        levels=256,
        symmetric=True,
        normed=True,
    )

    def prop(name):
        return float(np.mean(graycoprops(glcm, name)))

    contrast = prop("contrast")
    dissimilarity = prop("dissimilarity")
    homogeneity = prop("homogeneity")
    energy = prop("energy")
    correlation = prop("correlation")

    # Shannon entropy of the GLCM (optional metric requested by the spec).
    glcm_mean = np.mean(glcm, axis=(2, 3))
    p = glcm_mean / (glcm_mean.sum() + 1e-12)
    entropy = float(-np.sum(p[p > 0] * np.log2(p[p > 0])))

    return {
        "contrast": round(contrast, 3),
        "dissimilarity": round(dissimilarity, 3),
        "homogeneity": round(homogeneity, 3),
        "energy": round(energy, 3),
        "correlation": round(correlation, 3) if not math.isnan(correlation) else 0.0,
        "entropy": round(entropy, 3),
    }
