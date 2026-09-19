"""Central configuration for LeafLens backend.

All values are sourced from environment variables (see .env.example) so that
nothing about datasets, ports, or storage paths is hardcoded into the
application logic.
"""
from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

import yaml
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "configs"


class Settings(BaseSettings):
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    max_upload_mb: int = 10
    database_url: str = "sqlite:///./leaflens.db"
    model_dir: str = "./models"
    upload_dir: str = "./uploads"
    processed_dir: str = "./processed"
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.processed_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
    return settings


def _load_yaml(name: str) -> dict:
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


@lru_cache
def get_leaf_classes() -> list[str]:
    return _load_yaml("leaf_classes.yaml").get("classes", [])


@lru_cache
def get_growth_stage_classes() -> list[str]:
    return _load_yaml("growth_stages.yaml").get("classes", [])


@lru_cache
def get_health_config() -> dict:
    """Return health-model settings from configuration, never from UI code."""
    data = _load_yaml("health.yaml")
    return {
        "classes": data.get("classes", ["Healthy", "Diseased"]),
        "input_size": data.get("input_size", 224),
        "confidence_threshold": data.get("confidence_threshold", 0.60),
    }


@lru_cache
def get_confidence_thresholds() -> dict:
    data = _load_yaml("thresholds.yaml")
    return {"high": data.get("high", 0.80), "medium": data.get("medium", 0.55)}


def confidence_band(score: float) -> str:
    t = get_confidence_thresholds()
    if score >= t["high"]:
        return "HIGH"
    if score >= t["medium"]:
        return "MEDIUM"
    return "LOW"
