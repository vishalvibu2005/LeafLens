from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def gen_uuid() -> str:
    return uuid.uuid4().hex


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=gen_uuid)
    image_path = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    mode = Column(String, default="production")  # "production" or "demo"
    status = Column(String, default="completed")
    leaf_count = Column(Integer, default=0)

    leaf_results = relationship("LeafResult", back_populates="analysis", cascade="all, delete-orphan")


class LeafResult(Base):
    __tablename__ = "leaf_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    leaf_index = Column(Integer, nullable=False)

    detection_confidence = Column(Float, nullable=True)
    bbox_x = Column(Integer, nullable=True)
    bbox_y = Column(Integer, nullable=True)
    bbox_w = Column(Integer, nullable=True)
    bbox_h = Column(Integer, nullable=True)

    type_label = Column(String, nullable=True)
    type_confidence = Column(Float, nullable=True)
    type_is_demo = Column(Boolean, default=True)
    type_top3_json = Column(Text, nullable=True)

    stage_label = Column(String, nullable=True)
    stage_confidence = Column(Float, nullable=True)
    stage_is_demo = Column(Boolean, default=True)

    # Nullable so historical analyses remain intact after the health feature is added.
    health_label = Column(String, nullable=True)
    health_confidence = Column(Float, nullable=True)
    health_is_demo = Column(Boolean, default=True)
    health_top3_json = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="leaf_results")
    features = relationship("Features", back_populates="leaf_result", uselist=False, cascade="all, delete-orphan")


class Features(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    leaf_result_id = Column(Integer, ForeignKey("leaf_results.id"), nullable=False)

    area = Column(Float)
    perimeter = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    aspect_ratio = Column(Float)
    circularity = Column(Float)
    solidity = Column(Float)
    extent = Column(Float)
    convex_hull_area = Column(Float)
    equivalent_diameter = Column(Float)

    mean_r = Column(Float)
    mean_g = Column(Float)
    mean_b = Column(Float)
    dominant_color = Column(String)

    texture_contrast = Column(Float)
    texture_homogeneity = Column(Float)
    texture_energy = Column(Float)
    texture_correlation = Column(Float)

    leaf_result = relationship("LeafResult", back_populates="features")
