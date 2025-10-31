import asyncio
import time
import logging
from typing import List, Dict, Any, Union
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from app.models import BaseModel

logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self, max_workers: int = 4):
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.request_count = 0
        self.total_inference_time = 0.0
    
    async def predict(
        self, 
        model: BaseModel, 
        data: Union[List, Dict[str, Any]]
    ) -> Any:
        """
        Perform inference asynchronously
        """
        loop = asyncio.get_event_loop()
        start_time = time.time()
        
        try:
            # Run inference in thread pool to avoid blocking
            prediction = await loop.run_in_executor(
                self.thread_pool,
                model.predict,
                data
            )
            
            inference_time = time.time() - start_time
            self.request_count += 1
            self.total_inference_time += inference_time
            
            logger.info(f"Inference completed in {inference_time:.3f}s")
            return prediction
        
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise
    
    async def batch_predict(
        self,
        model: BaseModel,
        data: List[Union[List, Dict[str, Any]]],
        batch_size: int = 32
    ) -> List[Any]:
        """
        Perform batch inference asynchronously
        """
        predictions = []
        total_start_time = time.time()
        
        # Process in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_prediction = await self.predict(model, batch)
            
            if hasattr(batch_prediction, 'tolist'):
                batch_predictions = batch_prediction.tolist()
            else:
                batch_predictions = batch_prediction
            
            # Handle single prediction vs batch prediction
            if isinstance(batch_predictions, list) and len(batch_predictions) == len(batch):
                predictions.extend(batch_predictions)
            else:
                predictions.append(batch_predictions)
        
        total_time = time.time() - total_start_time
        logger.info(f"Batch inference completed: {len(predictions)} items in {total_time:.3f}s")
        
        return predictions
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get inference statistics
        """
        avg_time = (self.total_inference_time / self.request_count 
                   if self.request_count > 0 else 0)
        
        return {
            "total_requests": self.request_count,
            "total_inference_time": self.total_inference_time,
            "average_inference_time": avg_time,
            "requests_per_second": (self.request_count / self.total_inference_time 
                                  if self.total_inference_time > 0 else 0)
        }