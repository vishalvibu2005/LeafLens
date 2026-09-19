"""Loads all models once at startup and exposes their availability.

Never reload models per-request — routes and services pull from this
singleton instead.
"""
from __future__ import annotations

from functools import lru_cache

from app.models.detector import LeafDetector
from app.models.leaf_classifier import LeafClassifier
from app.models.health_classifier import HealthClassifier
from app.models.stage_classifier import StageClassifier
from app.utils.config import get_settings


class ModelManager:
    def __init__(self):
        settings = get_settings()
        self.detector = LeafDetector(settings.model_dir)
        self.leaf_classifier = LeafClassifier(settings.model_dir)
        self.health_classifier = HealthClassifier(settings.model_dir)
        self.stage_classifier = StageClassifier(settings.model_dir)

    def availability(self) -> dict:
        return {
            "detector": self.detector.is_trained,
            "detector_mode": self.detector.mode,
            "leaf_classifier": self.leaf_classifier.is_trained,
            "health_classifier": self.health_classifier.is_trained,
            "stage_classifier": self.stage_classifier.is_trained,
        }


@lru_cache
def get_model_manager() -> ModelManager:
    return ModelManager()
