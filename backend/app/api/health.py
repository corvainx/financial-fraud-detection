"""
System Health and Model Status Endpoint.
"""

import os
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    model_ready = os.path.exists(settings.MODEL_PATH)
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": settings.DATABASE_URL.split("://")[0],
        "ml_model_loaded": model_ready,
        "thresholds": {
            "flag_threshold": settings.FLAG_THRESHOLD,
            "block_threshold": settings.BLOCK_THRESHOLD
        }
    }
