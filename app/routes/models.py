from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import logging
from typing import List

from app.schemas import ModelInfo, ModelLoadRequest
from core.model_manager import ModelManager
from app.dependencies import get_model_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/models/load", response_model=ModelInfo)
async def load_model(
    request: ModelLoadRequest,
    background_tasks: BackgroundTasks,
    model_manager: ModelManager = Depends(get_model_manager)
):
    """
    Load a new model into memory
    """
    try:
        await model_manager.load_model(
            name=request.name,
            path=request.path,
            model_type=request.type,
            version=request.version
        )
        
        model = model_manager.get_model(request.name, request.version)
        
        return ModelInfo(
            name=request.name,
            version=request.version,
            type=request.type,
            loaded=True,
            description=f"Model loaded from {request.path}"
        )
    
    except Exception as e:
        logger.error(f"Model loading error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

@router.delete("/models/{model_name}")
async def unload_model(
    model_name: str,
    version: str = "latest",
    model_manager: ModelManager = Depends(get_model_manager)
):
    """
    Unload a model from memory
    """
    try:
        success = await model_manager.unload_model(model_name, version)
        
        if success:
            return {"message": f"Model {model_name} unloaded successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    except Exception as e:
        logger.error(f"Model unloading error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")

@router.get("/models", response_model=List[ModelInfo])
async def list_models(
    model_manager: ModelManager = Depends(get_model_manager)
):
    """
    List all loaded models
    """
    models_info = []
    
    for model_name, model_versions in model_manager.loaded_models.items():
        for version, model in model_versions.items():
            models_info.append(ModelInfo(
                name=model_name,
                version=version,
                type=getattr(model, 'model_type', 'unknown'),
                loaded=True,
                description=f"Loaded model: {model_name}"
            ))
    
    return models_info