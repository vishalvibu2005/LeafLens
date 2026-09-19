from __future__ import annotations

import json

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from app.db import models
from app.utils.config import confidence_band
from app.utils import files as file_utils


def serialize_analysis(analysis: models.Analysis) -> dict:
    leaf_results = []
    for lr in sorted(analysis.leaf_results, key=lambda x: x.leaf_index):
        f = lr.features
        top3 = json.loads(lr.type_top3_json) if lr.type_top3_json else []
        health_top3 = json.loads(lr.health_top3_json) if lr.health_top3_json else []
        leaf_results.append({
            "leaf_id": lr.leaf_index,
            "detection_confidence": lr.detection_confidence,
            "bbox": {"x": lr.bbox_x, "y": lr.bbox_y, "width": lr.bbox_w, "height": lr.bbox_h},
            "type": {
                "label": lr.type_label,
                "confidence": lr.type_confidence,
                "band": confidence_band(lr.type_confidence) if lr.type_confidence is not None else None,
                "top3": top3,
                "is_demo": lr.type_is_demo,
            },
            "growth_stage": {
                "label": lr.stage_label,
                "confidence": lr.stage_confidence,
                "band": confidence_band(lr.stage_confidence) if lr.stage_confidence is not None else None,
                "is_demo": lr.stage_is_demo,
            },
            "health": {
                "label": lr.health_label,
                "confidence": lr.health_confidence,
                "band": confidence_band(lr.health_confidence) if lr.health_confidence is not None else None,
                "top3": health_top3,
                "is_demo": lr.health_is_demo is not False,
            },
            "shape": {
                "area": f.area, "perimeter": f.perimeter, "width": f.width, "height": f.height,
                "aspect_ratio": f.aspect_ratio, "circularity": f.circularity, "solidity": f.solidity,
                "extent": f.extent, "convex_hull_area": f.convex_hull_area,
                "equivalent_diameter": f.equivalent_diameter,
            } if f else {},
            "color": {
                "rgb": {"r": f.mean_r, "g": f.mean_g, "b": f.mean_b} if f else {},
                "dominant_color": f.dominant_color if f else None,
            },
            "texture": {
                "contrast": f.texture_contrast, "homogeneity": f.texture_homogeneity,
                "energy": f.texture_energy, "correlation": f.texture_correlation,
            } if f else {},
            "views": {
                "crop": f"/media/processed/{analysis.id}/leaf{lr.leaf_index}_crop.png",
                "mask": f"/media/processed/{analysis.id}/leaf{lr.leaf_index}_mask.png",
                "contours": f"/media/processed/{analysis.id}/leaf{lr.leaf_index}_contours.png",
            },
        })

    return {
        "analysis_id": analysis.id,
        "status": analysis.status,
        "mode": analysis.mode,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "thumbnail_url": analysis.thumbnail_url,
        "leaf_count": analysis.leaf_count,
        "leaf_results": leaf_results,
        "global_views": {
            "original": f"/media/processed/{analysis.id}/original.png",
            "preprocessed": f"/media/processed/{analysis.id}/preprocessed.png",
            "detection": f"/media/processed/{analysis.id}/detection.png",
            "mask": f"/media/processed/{analysis.id}/mask.png",
        },
    }


def list_history(
    db: Session,
    search: str | None = None,
    leaf_type: str | None = None,
    growth_stage: str | None = None,
    sort: str = "newest",
    health_status: str | None = None,
) -> list[dict]:
    query = db.query(models.Analysis).options(joinedload(models.Analysis.leaf_results))

    if leaf_type or growth_stage or health_status:
        query = query.join(models.LeafResult)
        if leaf_type:
            query = query.filter(models.LeafResult.type_label == leaf_type)
        if growth_stage:
            query = query.filter(models.LeafResult.stage_label == growth_stage)
        if health_status:
            query = query.filter(models.LeafResult.health_label == health_status)

    query = query.order_by(desc(models.Analysis.created_at) if sort != "oldest" else models.Analysis.created_at)
    analyses = query.distinct().all()

    results = [serialize_analysis(a) for a in analyses]

    if search:
        s = search.lower()
        results = [
            r for r in results
            if s in (r["analysis_id"] or "").lower()
            or any(s in (lr["type"]["label"] or "").lower() for lr in r["leaf_results"])
            or any(s in (lr["health"]["label"] or "").lower() for lr in r["leaf_results"])
        ]
    return results


def get_analysis(db: Session, analysis_id: str) -> models.Analysis | None:
    return (
        db.query(models.Analysis)
        .options(joinedload(models.Analysis.leaf_results).joinedload(models.LeafResult.features))
        .filter(models.Analysis.id == analysis_id)
        .first()
    )


def delete_analysis(db: Session, analysis_id: str) -> bool:
    analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not analysis:
        return False
    db.delete(analysis)
    db.commit()
    return True


def delete_all_history(db: Session) -> int:
    count = db.query(models.Analysis).delete()
    db.commit()
    return count


def dashboard_stats(db: Session) -> dict:
    analyses = db.query(models.Analysis).options(joinedload(models.Analysis.leaf_results)).all()
    if not analyses:
        return {"has_data": False}

    total_analyses = len(analyses)
    total_leaves = sum(a.leaf_count for a in analyses)

    type_counts: dict[str, int] = {}
    confidences: list[float] = []
    healthy_leaves = 0
    affected_leaves = 0
    for a in analyses:
        for lr in a.leaf_results:
            if lr.type_label:
                type_counts[lr.type_label] = type_counts.get(lr.type_label, 0) + 1
            if lr.type_confidence is not None:
                confidences.append(lr.type_confidence)
            if lr.health_is_demo is False and lr.health_label:
                if lr.health_label.lower() == "healthy":
                    healthy_leaves += 1
                else:
                    affected_leaves += 1

    most_common = max(type_counts, key=type_counts.get) if type_counts else None
    avg_conf = round(sum(confidences) / len(confidences), 4) if confidences else None

    return {
        "has_data": True,
        "total_analyses": total_analyses,
        "leaves_detected": total_leaves,
        "most_analyzed_type": most_common,
        "average_confidence": avg_conf,
        "healthy_leaves": healthy_leaves,
        "affected_leaves": affected_leaves,
    }
