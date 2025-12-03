"""
Health check API endpoints.
"""
from fastapi import APIRouter
from app.models.request_models import HealthResponse

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        Simple status response
    """
    return {"status": "ok"}
