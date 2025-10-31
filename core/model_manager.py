import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from app.models import BaseModel, ModelFactory

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self):
        self.loaded_models: Dict[str, Dict[str, BaseModel]] = {}
        self.model_configs: Dict[str, Dict] = {}
    
    async def load_models(self):
        """
        Load all models from configuration
        """
        # Load from config file or environment
        config_path = Path("config/models.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                model_configs = json.load(f)
            
            for config in model_configs:
                await self.load_model(
                    name=config["name"],
                    path=config["path"],
                    model_type=config["type"],
                    version=config.get("version", "latest")
                )
    
    async def load_model(
        self, 
        name: str, 
        path: str, 
        model_type: str, 
        version: str = "latest"
    ) -> BaseModel:
        """
        Load a single model
        """
        try:
            model_config = {
                "path": path,
                "type": model_type
            }
            
            model = ModelFactory.create_model(model_config)
            model.load()
            
            if name not in self.loaded_models:
                self.loaded_models[name] = {}
            
            self.loaded_models[name][version] = model
            self.model_configs[f"{name}:{version}"] = model_config
            
            logger.info(f"Model {name}:{version} loaded successfully")
            return model
        
        except Exception as e:
            logger.error(f"Failed to load model {name}:{version}: {str(e)}")
            raise
    
    async def unload_model(self, name: str, version: str = "latest") -> bool:
        """
        Unload a model from memory
        """
        try:
            if name in self.loaded_models and version in self.loaded_models[name]:
                del self.loaded_models[name][version]
                
                if not self.loaded_models[name]:
                    del self.loaded_models[name]
                
                config_key = f"{name}:{version}"
                if config_key in self.model_configs:
                    del self.model_configs[config_key]
                
                logger.info(f"Model {name}:{version} unloaded successfully")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Failed to unload model {name}:{version}: {str(e)}")
            return False
    
    async def unload_models(self):
        """
        Unload all models
        """
        for name in list(self.loaded_models.keys()):
            for version in list(self.loaded_models[name].keys()):
                await self.unload_model(name, version)
    
    def get_model(self, name: str, version: str = "latest") -> BaseModel:
        """
        Get a loaded model
        """
        if name not in self.loaded_models:
            raise KeyError(f"Model {name} not found")
        
        if version not in self.loaded_models[name]:
            raise KeyError(f"Version {version} of model {name} not found")
        
        return self.loaded_models[name][version]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all loaded models with their versions
        """
        models_list = []
        for name, versions in self.loaded_models.items():
            for version, model in versions.items():
                models_list.append({
                    "name": name,
                    "version": version,
                    "type": getattr(model, 'model_type', 'unknown'),
                    "loaded": True
                })
        return models_list