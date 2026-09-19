from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class BBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class TypePrediction(BaseModel):
    label: Optional[str] = None
    confidence: Optional[float] = None
    band: Optional[str] = None
    top3: list[dict] = []
    is_demo: bool = True


class StagePrediction(BaseModel):
    label: Optional[str] = None
    confidence: Optional[float] = None
    band: Optional[str] = None
    is_demo: bool = True


class HealthPrediction(BaseModel):
    label: Optional[str] = None
    confidence: Optional[float] = None
    band: Optional[str] = None
    top3: list[dict] = []
    is_demo: bool = True


class ShapeFeatures(BaseModel):
    area: float
    perimeter: float
    width: int
    height: int
    aspect_ratio: float
    circularity: float
    solidity: float
    extent: float
    convex_hull_area: float
    equivalent_diameter: float


class ColorFeatures(BaseModel):
    rgb: dict
    hsv: dict
    lab: dict
    dominant_color: str
    green_intensity: float


class TextureFeatures(BaseModel):
    contrast: float
    dissimilarity: float
    homogeneity: float
    energy: float
    correlation: float
    entropy: float


class LeafResultOut(BaseModel):
    leaf_id: int
    detection_confidence: float
    bbox: BBox
    type: TypePrediction
    health: HealthPrediction
    growth_stage: StagePrediction
    shape: ShapeFeatures
    color: ColorFeatures
    texture: TextureFeatures
    views: dict


class ImageInfo(BaseModel):
    width: int
    height: int


class AnalysisOut(BaseModel):
    analysis_id: str
    status: str
    mode: str
    created_at: str
    image: ImageInfo
    leaf_count: int
    leaf_results: list[LeafResultOut]
    global_views: dict
    warnings: list[str] = []
