from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API Settings
    app_name: str = "MLauncher"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    debug: bool = False
    
    # Security
    api_key: Optional[str] = None
    require_api_key: bool = False
    allowed_origins: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]
    
    # Model Settings
    model_cache_size: int = 10
    default_batch_size: int = 32
    max_request_size: int = 100  # MB
    
    # Database
    database_url: str = "sqlite:///./mlauncher.db"
    
    # Cloud Storage
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    gcs_bucket: Optional[str] = None
    azure_storage_connection_string: Optional[str] = None
    
    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    # Kubernetes
    namespace: str = "mlauncher"
    deployment_name: str = "mlauncher-api"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings():
    return Settings()