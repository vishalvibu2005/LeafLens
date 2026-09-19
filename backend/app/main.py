from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import routes_health, routes_analysis, routes_history
from app.db.database import init_db
from app.utils.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("leaflens")

settings = get_settings()

app = FastAPI(
    title="LeafLens API",
    description="AI-powered plant leaf detection, leaf type classification, and growth stage analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "Something went wrong. Please try again."},
    )


@app.on_event("startup")
def on_startup():
    init_db()
    from app.models.model_manager import get_model_manager
    manager = get_model_manager()
    logger.info("Model availability: %s", manager.availability())


app.include_router(routes_health.router, prefix="/api", tags=["health"])
app.include_router(routes_analysis.router, prefix="/api", tags=["analysis"])
app.include_router(routes_history.router, prefix="/api", tags=["history"])

app.mount("/media/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/media/processed", StaticFiles(directory=settings.processed_dir), name="processed")


@app.get("/")
def root():
    return {"name": "LeafLens API", "status": "running", "docs": "/docs"}
