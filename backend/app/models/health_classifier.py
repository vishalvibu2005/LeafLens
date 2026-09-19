from __future__ import annotations

from pathlib import Path
import numpy as np


class HealthClassifier:
    """
    Keras-based Healthy/Diseased classifier.

    Loads:
        backend/models/health/health_model_v2.keras
    """

    def __init__(self, model_dir: str):
        self.weights_path = (
            Path(model_dir)
            / "health"
            / "health_model_v2.keras"
        )

        self.classes = [
            "Healthy",
            "Diseased"
        ]

        self.input_size = 224

        # Used by analysis_service.py
        self.confidence_threshold = 0.50

        self._model = None
        self._try_load()

    def _try_load(self):
        if not self.weights_path.exists():
            print(
                f"Health model not found: {self.weights_path}"
            )
            return

        try:
            import tensorflow as tf

            self._model = tf.keras.models.load_model(
                self.weights_path
            )

            print(
                f"Health V2 model loaded: {self.weights_path}"
            )

        except Exception as exc:
            print(
                f"Failed to load Health V2 model: {exc}"
            )
            self._model = None

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def predict(self, leaf_crop_bgr: np.ndarray):
        if self._model is None:
            return None

        import cv2

        # BGR -> RGB
        image = cv2.cvtColor(
            leaf_crop_bgr,
            cv2.COLOR_BGR2RGB
        )

        # Resize to training size
        image = cv2.resize(
            image,
            (self.input_size, self.input_size)
        )

        # IMPORTANT:
        # EfficientNet expects 0-255 input.
        # Do NOT divide by 255 here.
        image = image.astype(np.float32)

        image = np.expand_dims(
            image,
            axis=0
        )

        probabilities = self._model.predict(
            image,
            verbose=0
        )[0]

        ranked = sorted(
            zip(self.classes, probabilities),
            key=lambda x: float(x[1]),
            reverse=True
        )

        label, confidence = ranked[0]

        return {
            "label": label,
            "confidence": round(
                float(confidence),
                4
            ),
            "top3": [
                {
                    "label": name,
                    "confidence": round(
                        float(score),
                        4
                    )
                }
                for name, score in ranked[:3]
            ]
        }