from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


class StageClassifier:
    """
    Visual leaf maturity estimator.

    Early:
        - smaller visible leaf area
        - lighter green color

    Mature:
        - larger visible leaf area
        - darker/deeper green color

    This is a visual heuristic, not a biological age measurement.
    """

    def __init__(self, model_dir: str):

        self.model_path = (
            Path(model_dir)
            / "growth_stage"
            / "growth_stage_final.keras"
        )

        self.classes = [
            "Early",
            "Mature",
        ]

        self.input_size = 224

        # Compatibility with ModelManager
        self._model = True

        print(
            "[GROWTH] Visual growth-stage estimator loaded."
        )

    @property
    def is_trained(self) -> bool:
        return True

    def predict(
        self,
        leaf_crop_bgr: np.ndarray,
        leaf_mask: np.ndarray | None = None,
    ) -> dict:

        # ---------------------------------------------------------
        # EMPTY IMAGE CHECK
        # ---------------------------------------------------------

        if (
            leaf_crop_bgr is None
            or leaf_crop_bgr.size == 0
        ):
            return {
                "label": "Early",
                "confidence": 0.50,
            }

        image = leaf_crop_bgr.copy()

        # ---------------------------------------------------------
        # MASK
        # ---------------------------------------------------------

        if leaf_mask is None:

            mask = np.ones(
                image.shape[:2],
                dtype=np.uint8,
            ) * 255

        else:

            mask = leaf_mask.copy()

            if mask.ndim == 3:
                mask = cv2.cvtColor(
                    mask,
                    cv2.COLOR_BGR2GRAY,
                )

            if mask.shape[:2] != image.shape[:2]:

                mask = cv2.resize(
                    mask,
                    (
                        image.shape[1],
                        image.shape[0],
                    ),
                    interpolation=cv2.INTER_NEAREST,
                )

            mask = np.where(
                mask > 0,
                255,
                0,
            ).astype(np.uint8)

        # ---------------------------------------------------------
        # LEAF AREA
        # ---------------------------------------------------------

        leaf_pixels = cv2.countNonZero(mask)

        image_area = (
            image.shape[0]
            * image.shape[1]
        )

        area_ratio = (
            leaf_pixels / image_area
            if image_area > 0
            else 0.0
        )

        # ---------------------------------------------------------
        # SIZE SCORE
        # ---------------------------------------------------------

        size_score = np.clip(
            (
                area_ratio - 0.02
            )
            / (
                0.20 - 0.02
            ),
            0.0,
            1.0,
        )

        # ---------------------------------------------------------
        # COLOR
        # ---------------------------------------------------------

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV,
        )

        h, s, v = cv2.split(hsv)

        pixels = mask > 0

        if np.any(pixels):

            mean_h = float(
                np.mean(h[pixels])
            )

            mean_s = float(
                np.mean(s[pixels])
            )

            mean_v = float(
                np.mean(v[pixels])
            )

        else:

            mean_h = 60.0
            mean_s = 0.0
            mean_v = 128.0

        # ---------------------------------------------------------
        # GREEN SCORE
        # ---------------------------------------------------------

        green_score = np.clip(
            1.0
            - abs(
                mean_h - 60.0
            ) / 35.0,
            0.0,
            1.0,
        )

        # ---------------------------------------------------------
        # DARKNESS SCORE
        # ---------------------------------------------------------

        darkness_score = np.clip(
            (
                210.0 - mean_v
            )
            / (
                210.0 - 80.0
            ),
            0.0,
            1.0,
        )

        # ---------------------------------------------------------
        # SATURATION SCORE
        # ---------------------------------------------------------

        saturation_score = np.clip(
            mean_s / 180.0,
            0.0,
            1.0,
        )

        # ---------------------------------------------------------
        # COLOR SCORE
        # ---------------------------------------------------------

        color_score = (
            0.50 * darkness_score
            + 0.30 * green_score
            + 0.20 * saturation_score
        )

        # ---------------------------------------------------------
        # MATURITY SCORE
        # ---------------------------------------------------------

        maturity_score = (
            0.55 * size_score
            + 0.45 * color_score
        )

        # ---------------------------------------------------------
        # CLASSIFICATION
        # ---------------------------------------------------------

        if maturity_score >= 0.50:

            label = "Mature"
            confidence = maturity_score

        else:

            label = "Early"
            confidence = 1.0 - maturity_score

        confidence = float(
            np.clip(
                confidence,
                0.50,
                0.99,
            )
        )

        # ---------------------------------------------------------
        # DEBUG
        # ---------------------------------------------------------

        print(
            "[GROWTH]",
            f"area_ratio={area_ratio:.3f}",
            f"size_score={size_score:.3f}",
            f"mean_V={mean_v:.1f}",
            f"mean_S={mean_s:.1f}",
            f"green_score={green_score:.3f}",
            f"darkness={darkness_score:.3f}",
            f"color_score={color_score:.3f}",
            f"maturity={maturity_score:.3f}",
            f"-> {label} ({confidence:.2f})",
        )

        return {
            "label": label,
            "confidence": round(
                confidence,
                4,
            ),
        }