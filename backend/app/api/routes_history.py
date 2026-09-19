from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import history_service

router = APIRouter()


@router.get("/history")
def get_history(
    search: str | None = None,
    leaf_type: str | None = None,
    growth_stage: str | None = None,
    health_status: str | None = None,
    sort: str = Query("newest", pattern="^(newest|oldest)$"),
    db: Session = Depends(get_db),
):
    return history_service.list_history(db, search, leaf_type, growth_stage, sort, health_status)


@router.get("/history/{analysis_id}")
def get_history_item(analysis_id: str, db: Session = Depends(get_db)):
    analysis = history_service.get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Analysis not found."})
    return history_service.serialize_analysis(analysis)


@router.delete("/history/{analysis_id}")
def delete_history_item(analysis_id: str, db: Session = Depends(get_db)):
    ok = history_service.delete_analysis(db, analysis_id)
    if not ok:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Analysis not found."})
    return {"deleted": True}


@router.delete("/history")
def delete_all(db: Session = Depends(get_db)):
    count = history_service.delete_all_history(db)
    return {"deleted": count}


@router.get("/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    return history_service.dashboard_stats(db)
