from __future__ import annotations

import io
import logging

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.model_manager import ModelManager, get_model_manager
from app.services import analysis_service, history_service
from app.utils.config import get_settings
from app.utils.validation import validate_upload, ValidationError

logger = logging.getLogger("leaflens")
router = APIRouter()


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    manager: ModelManager = Depends(get_model_manager),
):
    settings = get_settings()
    raw = await file.read()

    try:
        image = validate_upload(raw, file.filename, file.content_type, settings.max_upload_bytes)
    except ValidationError as e:
        logger.warning("Upload validation failed: %s", e.code)
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})

    try:
        analysis = analysis_service.run_full_analysis(db, image, file.filename, manager)
    except Exception:
        logger.exception("Analysis failed")
        raise HTTPException(
            status_code=500,
            detail={"code": "ANALYSIS_FAILED", "message": "Analysis failed while processing this image."},
        )

    if analysis.status == "no_leaf_detected":
        raise HTTPException(
            status_code=422,
            detail={
                "code": "NO_LEAF_DETECTED",
                "message": "No clear leaf detected. Try a closer image, better lighting, "
                           "a less cluttered background, or a more clearly visible leaf.",
            },
        )

    logger.info("Analysis completed: %s (%d leaves)", analysis.id, analysis.leaf_count)
    return history_service.serialize_analysis(analysis)
