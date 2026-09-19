"""Leaf detector.

Preferred: a trained YOLO11 segmentation model, loaded from
MODEL_DIR/leaf_detector/best.pt if present.

Fallback (always available, no external weights required): classical
connected-component instance splitting on the HSV/LAB segmentation mask.
This keeps the application fully functional out of the box while still
allowing a real trained detector to be dropped in later without any
application code changes.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from app.cv import segmentation


class LeafDetector:
    def __init__(self, model_dir: str):
        self.weights_path = Path(model_dir) / "leaf_detector" / "best.pt"
        self._yolo = None
        self.mode = "classical"
        self._try_load_yolo()

    def _try_load_yolo(self) -> None:
        if not self.weights_path.exists():
            return
        try:
            from ultralytics import YOLO
            self._yolo = YOLO(str(self.weights_path))
            self.mode = "yolo"
        except Exception:
            self._yolo = None
            self.mode = "classical"

    @property
    def is_trained(self) -> bool:
        return self._yolo is not None

    def detect(self, image_bgr: np.ndarray) -> dict:
        """Return leaf instances plus the full-image segmentation mask."""

        seg = segmentation.segment_leaf(image_bgr)

        if self._yolo is not None:
            results = self._yolo(
                image_bgr,
                verbose=False,
            )[0]

            instances = []

            for i, box in enumerate(results.boxes):
                x1, y1, x2, y2 = [
                    int(v)
                    for v in box.xyxy[0].tolist()
                ]

                conf = float(box.conf[0])

                inst_mask = np.zeros(
                    image_bgr.shape[:2],
                    dtype=np.uint8
                )

                if results.masks is not None:
                    m = (
                        results.masks.data[i]
                        .cpu()
                        .numpy()
                    )

                    m = (
                        m * 255
                    ).astype(np.uint8)

                    inst_mask = m

                instances.append({
                    "id": i + 1,
                    "confidence": round(conf, 4),
                    "bbox": {
                        "x": x1,
                        "y": y1,
                        "width": x2 - x1,
                        "height": y2 - y1
                    },
                    "mask": inst_mask,
                })

            return {
                "instances": instances,
                "seg": seg
            }

        # Classical fallback
        raw_instances = (
            segmentation.find_leaf_instances(
                seg["mask"]
            )
        )

        instances = []

        for i, inst in enumerate(raw_instances):

            coverage_score = min(
                1.0,
                inst["area"]
                / (
                    image_bgr.shape[0]
                    * image_bgr.shape[1]
                )
                * 6
            )

            confidence = round(
                0.55 + 0.4 * coverage_score,
                4
            )

            instances.append({
                "id": i + 1,
                "confidence": min(
                    confidence,
                    0.97
                ),
                "bbox": inst["bbox"],
                "mask": inst["mask"],
            })

        return {
            "instances": instances,
            "seg": seg
        }