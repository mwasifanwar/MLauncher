from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from typing import List

from app.schemas import InferenceRequest, InferenceResponse, BatchInferenceRequest, BatchInferenceResponse
from core.model_manager import ModelManager
from app.dependencies import get_model_manager, validate_model_name

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/predict", response_model=InferenceResponse)
async def predict(
    request: InferenceRequest,
    model_manager: ModelManager = Depends(get_model_manager),
    model_name: str = Depends(validate_model_name)
):
    """
    Perform single inference with the specified model
    """
    try:
        start_time = time.time()
        
        model = model_manager.get_model(request.model_name, request.version)
        prediction = model.predict(request.data)
        
        inference_time = time.time() - start_time
        
        return InferenceResponse(
            prediction=prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            model_name=request.model_name,
            version=request.version,
            inference_time=inference_time
        )
    
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@router.post("/batch_predict", response_model=BatchInferenceResponse)
async def batch_predict(
    request: BatchInferenceRequest,
    model_manager: ModelManager = Depends(get_model_manager),
    model_name: str = Depends(validate_model_name)
):
    """
    Perform batch inference with the specified model
    """
    try:
        start_time = time.time()
        
        model = model_manager.get_model(request.model_name)
        
        # Process in batches
        batch_size = request.batch_size
        predictions = []
        batch_count = 0
        
        for i in range(0, len(request.data), batch_size):
            batch = request.data[i:i + batch_size]
            batch_prediction = model.predict(batch)
            predictions.extend(
                batch_prediction.tolist() if hasattr(batch_prediction, 'tolist') 
                else batch_prediction
            )
            batch_count += 1
        
        total_time = time.time() - start_time
        
        return BatchInferenceResponse(
            predictions=predictions,
            model_name=request.model_name,
            total_time=total_time,
            batch_count=batch_count
        )
    
    except Exception as e:
        logger.error(f"Batch inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch inference failed: {str(e)}")

@router.get("/models/{model_name}/info")
async def get_model_info(
    model_name: str,
    model_manager: ModelManager = Depends(get_model_manager),
    _: str = Depends(validate_model_name)
):
    """
    Get information about a loaded model
    """
    model = model_manager.get_model(model_name)
    
    return {
        "name": model_name,
        "type": getattr(model, 'model_type', 'unknown'),
        "loaded": True,
        "input_shape": getattr(model, 'input_shape', None),
        "output_shape": getattr(model, 'output_shape', None)
    }