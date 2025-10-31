from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class ModelType(str, Enum):
    PYTORCH = "pytorch"
    SKLEARN = "sklearn"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"

class InferenceRequest(BaseModel):
    data: Union[List, Dict[str, Any]] = Field(..., description="Input data for inference")
    model_name: str = Field(..., description="Name of the model to use")
    version: Optional[str] = Field("latest", description="Model version")
    
    class Config:
        schema_extra = {
            "example": {
                "data": [[1.0, 2.0, 3.0, 4.0]],
                "model_name": "iris-classifier",
                "version": "v1.0"
            }
        }

class InferenceResponse(BaseModel):
    prediction: Union[List, Dict[str, Any]] = Field(..., description="Model prediction")
    model_name: str = Field(..., description="Name of the model used")
    version: str = Field(..., description="Model version")
    inference_time: float = Field(..., description="Inference time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": [0],
                "model_name": "iris-classifier",
                "version": "v1.0",
                "inference_time": 0.023
            }
        }

class BatchInferenceRequest(BaseModel):
    data: List[Union[List, Dict[str, Any]]] = Field(..., description="Batch input data")
    model_name: str = Field(..., description="Name of the model to use")
    batch_size: Optional[int] = Field(32, description="Batch size for processing")

class BatchInferenceResponse(BaseModel):
    predictions: List[Union[List, Dict[str, Any]]] = Field(..., description="Batch predictions")
    model_name: str = Field(..., description="Name of the model used")
    total_time: float = Field(..., description="Total processing time in seconds")
    batch_count: int = Field(..., description="Number of batches processed")

class ModelInfo(BaseModel):
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    type: ModelType = Field(..., description="Model type")
    input_shape: Optional[List[int]] = Field(None, description="Expected input shape")
    output_shape: Optional[List[int]] = Field(None, description="Expected output shape")
    description: Optional[str] = Field(None, description="Model description")
    loaded: bool = Field(..., description="Whether model is currently loaded")

class ModelLoadRequest(BaseModel):
    name: str = Field(..., description="Model name")
    path: str = Field(..., description="Path to model file")
    type: ModelType = Field(..., description="Model type")
    version: str = Field(..., description="Model version")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    models_loaded: int = Field(..., description="Number of loaded models")
    timestamp: str = Field(..., description="Current timestamp")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: int = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")