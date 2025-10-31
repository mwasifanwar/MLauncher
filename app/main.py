from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import make_asgi_app, Counter, Histogram, generate_latest
from typing import Dict, Any

from config.settings import get_settings
from core.model_manager import ModelManager
from core.security import verify_api_key
from app.routes import inference, models, monitoring

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['method', 'endpoint'])

settings = get_settings()
model_manager = ModelManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models
    await model_manager.load_models()
    print("🚀 MLauncher started successfully!")
    yield
    # Shutdown: Cleanup resources
    await model_manager.unload_models()
    print("👋 MLauncher shutdown complete")

app = FastAPI(
    title="MLauncher",
    description="Enterprise ML Model Deployment Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Add prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    logging.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response

# Include routers
app.include_router(
    inference.router,
    prefix="/api/v1",
    tags=["inference"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    models.router,
    prefix="/api/v1",
    tags=["models"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    monitoring.router,
    prefix="/api/v1",
    tags=["monitoring"]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to MLauncher",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": len(model_manager.loaded_models),
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers
    )