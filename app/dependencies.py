from fastapi import Header, HTTPException, Depends
from typing import Optional
import os

from core.model_manager import ModelManager
from config.settings import get_settings

settings = get_settings()
model_manager = ModelManager()

async def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if settings.require_api_key:
        if not api_key or api_key != settings.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key"
            )
    return api_key

async def get_model_manager() -> ModelManager:
    return model_manager

async def validate_model_name(model_name: str, model_manager: ModelManager = Depends(get_model_manager)):
    if model_name not in model_manager.loaded_models:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found or not loaded"
        )
    return model_name