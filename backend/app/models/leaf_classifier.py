from __future__ import annotations

from pathlib import Path
import numpy as np


class LeafClassifier:

    def __init__(self, model_dir: str):

        self.weights_path = (
            Path(model_dir)
            / "leaf_classifier"
            / "species_model_v2.keras"
        )

        self.classes = [
            "Grape",
            "Peach",
            "Strawberry",
            "Tomato"
        ]

        self.input_size = 224
        self._model = None

        self._try_load()

    def _try_load(self):

        if not self.weights_path.exists():
            print(
                f"Species model not found: {self.weights_path}"
            )
            return

        try:
            import tensorflow as tf

            self._model = tf.keras.models.load_model(
                self.weights_path
            )

            print(
                f"Species V2 model loaded: {self.weights_path}"
            )

        except Exception as exc:
            print(
                f"Failed to load Species V2 model: {exc}"
            )
            self._model = None

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def predict(self, leaf_crop_bgr: np.ndarray):

        if self._model is None:
            return None

        import cv2

        image = cv2.cvtColor(
            leaf_crop_bgr,
            cv2.COLOR_BGR2RGB
        )

        image = cv2.resize(
            image,
            (
                self.input_size,
                self.input_size
            )
        )

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
            zip(
                self.classes,
                probabilities
            ),
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