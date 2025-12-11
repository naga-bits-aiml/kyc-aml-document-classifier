"""
FastAPI inference API for KYC/AML Document Classifier.

Provides endpoints for document classification with health checks.
"""

import os
import json
import tempfile
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from inference.inference_engine import InferenceEngine
from inference.download_models import download_models


# Load configurations
PROJECT_ROOT = Path(__file__).resolve().parent.parent
with open(PROJECT_ROOT / "conf" / "app_config.json", 'r') as f:
    app_config = json.load(f)

with open(PROJECT_ROOT / "conf" / "logging_config.json", 'r') as f:
    logging_config = json.load(f)


def setup_logging():
    """Setup application logging with rotation and cleanup"""
    log_config = logging_config['logging']
    
    # Create logs directory
    logs_dir = PROJECT_ROOT / log_config['log_directory']
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with current date
    log_filename = log_config['log_file_pattern'].format(
        date=datetime.now().strftime('%Y_%m_%d')
    )
    log_file_path = logs_dir / log_filename
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root logger level
    root_logger.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=log_config['format'],
        datefmt=log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
    )
    
    handlers = []
    
    # File handler with rotation
    if log_config['file']['enabled']:
        file_handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when=log_config['rotation']['when'],
            interval=log_config['rotation']['interval'],
            backupCount=log_config['rotation']['backup_count'],
            encoding=log_config['rotation']['encoding']
        )
        file_handler.setLevel(getattr(logging, log_config['file']['level']))
        file_handler.setFormatter(formatter)
        
        # Custom suffix for rotated files (YYYY_MM_DD format)
        file_handler.suffix = "%Y_%m_%d"
        
        handlers.append(file_handler)
    
    # Console handler
    if log_config['console']['enabled']:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_config['console']['level']))
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    return logs_dir


# Setup logging
LOGS_DIR = setup_logging()
logger = logging.getLogger(__name__)

# Global inference engine
engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)"""
    global engine
    
    # Startup
    logger.info("="*60)
    logger.info(f"🚀 Starting {app_config['app_name']} v{app_config['version']}")
    logger.info("="*60)
    logger.info(f"Logs directory: {LOGS_DIR}")
    
    # Download models if not present
    logger.info("📥 Checking models...")
    success = download_models()
    
    if not success:
        logger.error("❌ Failed to download required models!")
        logger.warning("⚠️  Application may not work correctly")
    else:
        # Initialize inference engine
        try:
            logger.info("🔧 Initializing inference engine...")
            engine = InferenceEngine()
            logger.info("✅ Application ready!")
            logger.info("="*60)
        except Exception as e:
            logger.error(f"❌ Failed to initialize inference engine: {e}", exc_info=True)
            logger.warning("⚠️  Application may not work correctly")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("👋 Shutting down application...")
    engine = None


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=app_config['app_name'],
    version=app_config['version'],
    description="Document classification API for KYC/AML identity documents",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    return response


@app.get("/")
def root():
    """Root endpoint"""
    logger.debug("Root endpoint accessed")
    return {
        "app": app_config['app_name'],
        "version": app_config['version'],
        "status": "running",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "predict": "/predict"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    logger.debug("Health check accessed")
    return {
        "status": "healthy" if engine is not None else "initializing",
        "model_loaded": engine is not None
    }


@app.get("/info")
def info():
    """Get model information"""
    logger.debug("Info endpoint accessed")
    if engine is None:
        logger.warning("Info endpoint accessed but model not loaded")
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    return {
        "app": app_config['app_name'],
        "version": app_config['version'],
        "model": {
            "classes": engine.class_names,
            "num_classes": len(engine.class_names),
            "confidence_threshold": engine.confidence_threshold,
            "card_detection_enabled": engine.enable_card_detection,
            "device": str(engine.device)
        },
        "preprocessing": app_config['preprocessing']
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Classify uploaded document image.
    
    Args:
        file: Image file (jpg, jpeg, png, bmp, tiff)
    
    Returns:
        Classification result with predicted class and confidence
    """
    logger.info(f"Prediction request received for file: {file.filename}")
    
    if engine is None:
        logger.error("Prediction attempted but model not initialized")
        raise HTTPException(status_code=503, detail="Model not initialized yet")
    
    # Validate file type
    suffix = os.path.splitext(file.filename)[1].lower()
    supported_formats = app_config['preprocessing']['supported_formats']
    
    if suffix.lstrip('.') not in supported_formats:
        logger.warning(f"Unsupported file type: {suffix} for file: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported formats: {', '.join(supported_formats)}"
        )
    
    # Process image
    tmp_path = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        logger.debug(f"Processing image: {file.filename} (size: {len(contents)} bytes)")
        
        # Run inference
        result = engine.predict(tmp_path)
        
        # Log prediction result
        if result.get('success'):
            logger.info(
                f"Prediction successful - File: {file.filename}, "
                f"Class: {result['predicted_class']}, "
                f"Confidence: {result['confidence']:.4f}"
            )
        else:
            logger.error(f"Prediction failed - File: {file.filename}, Error: {result.get('error')}")
        
        # Add metadata
        result['filename'] = file.filename
        result['file_size'] = len(contents)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Prediction error for file {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.debug(f"Cleaned up temporary file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {tmp_path}: {e}")


@app.get("/classes")
def get_classes():
    """Get list of supported document classes"""
    logger.debug("Classes endpoint accessed")
    if engine is None:
        logger.warning("Classes endpoint accessed but model not loaded")
        raise HTTPException(status_code=503, detail="Model not initialized yet")
    
    return {
        "classes": engine.class_names,
        "num_classes": len(engine.class_names)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=app_config['api']['host'],
        port=app_config['api']['port'],
        log_level="info"
    )