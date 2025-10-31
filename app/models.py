import torch
import torch.nn as nn
import numpy as np
import joblib
from typing import Any, Dict, List, Union
import logging
from pathlib import Path
import onnxruntime as ort

logger = logging.getLogger(__name__)

class BaseModel:
    def __init__(self, model_path: str, model_type: str = "pytorch"):
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.loaded = False
    
    def load(self):
        try:
            if self.model_type == "pytorch":
                self.model = torch.load(self.model_path, map_location='cpu')
                if isinstance(self.model, nn.Module):
                    self.model.eval()
            elif self.model_type == "sklearn":
                self.model = joblib.load(self.model_path)
            elif self.model_type == "onnx":
                self.model = ort.InferenceSession(self.model_path)
            
            self.loaded = True
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, input_data: Union[np.ndarray, List, Dict]) -> Any:
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        try:
            if self.model_type == "pytorch":
                return self._pytorch_predict(input_data)
            elif self.model_type == "sklearn":
                return self._sklearn_predict(input_data)
            elif self.model_type == "onnx":
                return self._onnx_predict(input_data)
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def _pytorch_predict(self, input_data: Union[np.ndarray, List]) -> np.ndarray:
        if isinstance(input_data, list):
            input_data = np.array(input_data)
        
        with torch.no_grad():
            if isinstance(input_data, np.ndarray):
                input_tensor = torch.from_numpy(input_data).float()
            else:
                input_tensor = input_data
            
            output = self.model(input_tensor)
            
            if isinstance(output, torch.Tensor):
                return output.numpy()
            return output
    
    def _sklearn_predict(self, input_data: Union[np.ndarray, List]) -> np.ndarray:
        if isinstance(input_data, list):
            input_data = np.array(input_data)
        return self.model.predict(input_data)
    
    def _onnx_predict(self, input_data: Dict[str, np.ndarray]) -> List[np.ndarray]:
        return self.model.run(None, input_data)

class SampleClassifier(BaseModel):
    def __init__(self, model_path: str):
        super().__init__(model_path, "pytorch")
        self.class_names = ["class_0", "class_1", "class_2"]
    
    def predict_proba(self, input_data: np.ndarray) -> np.ndarray:
        predictions = self.predict(input_data)
        # Convert to probabilities if needed
        if predictions.ndim == 1:
            # Binary classification
            proba = np.column_stack([1 - predictions, predictions])
        else:
            proba = predictions
        return proba

class ModelFactory:
    @staticmethod
    def create_model(model_config: Dict[str, Any]) -> BaseModel:
        model_type = model_config.get("type", "pytorch")
        model_path = model_config["path"]
        
        if model_type == "pytorch":
            return BaseModel(model_path, "pytorch")
        elif model_type == "sklearn":
            return BaseModel(model_path, "sklearn")
        elif model_type == "onnx":
            return BaseModel(model_path, "onnx")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")