from fastapi import APIRouter, Depends
from prometheus_client import generate_latest
import psutil
import time

from app.schemas import HealthResponse
from core.model_manager import ModelManager
from app.dependencies import get_model_manager

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(
    model_manager: ModelManager = Depends(get_model_manager)
):
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        models_loaded=len(model_manager.loaded_models),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    return generate_latest()

@router.get("/system")
async def system_info():
    """
    System information and resource usage
    """
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "boot_time": psutil.boot_time(),
        "process_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
    }