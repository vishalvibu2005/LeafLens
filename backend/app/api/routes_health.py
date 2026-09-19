from fastapi import APIRouter, Depends

from app.models.model_manager import ModelManager, get_model_manager

router = APIRouter()


@router.get("/health")
def health(manager: ModelManager = Depends(get_model_manager)):
    return {
        "status": "healthy",
        "models": manager.availability(),
    }
