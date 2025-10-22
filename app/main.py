"""
AI Social Factory - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.core.logging import setup_logging
from app.api.routes import video, workflow, content, analytics
from app.services.video_service import VideoService
from app.services.auto_processor import AutoProcessor

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize services at startup
video_service = None
auto_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global video_service, auto_processor
    
    # Startup
    logger.info("Starting AI Social Factory...")
    try:
        video_service = VideoService()
        # Set the video service in the video router
        video.set_video_service(video_service)
        # Set the video service in the workflow router
        workflow.set_video_service(video_service)
        # Don't load model on startup - let it load on first request
        # This prevents blocking and allows the API to start without the model
        logger.info("Video service initialized (model will load on first request)")
    except Exception as e:
        logger.error(f"Failed to initialize video service: {e}")
        logger.warning("Running without video generation capability")
        video_service = None
    
    # Start auto-processor for Google Sheets
    try:
        from app.api.routes.workflow import get_workflow_service
        workflow_service = get_workflow_service()
        auto_processor = AutoProcessor(workflow_service)
        
        # Start auto-processing in background
        import asyncio
        asyncio.create_task(auto_processor.start())
        logger.info("Auto-processor started for Google Sheets monitoring")
    except Exception as e:
        logger.error(f"Failed to start auto-processor: {e}")
        auto_processor = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Social Factory...")
    
    # Stop auto-processor
    if auto_processor:
        try:
            await auto_processor.stop()
        except:
            pass
    
    if video_service and hasattr(video_service, 'cleanup'):
        try:
            await video_service.cleanup()
        except:
            pass

# Create FastAPI app
app = FastAPI(
    title="AI Social Factory API",
    description="Automated content generation and publishing platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for local file:// and localhost)
    allow_credentials=False,  # Set to False when using wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files for generated videos
app.mount("/videos", StaticFiles(directory="generated_videos"), name="videos")

# Mount frontend static files (HTML, CSS, JS)
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Mount SaaS frontend (studio.html, dashboard.html, etc.)
app.mount("/saas", StaticFiles(directory="saas-frontend", html=True), name="saas-frontend")

# Include routers
app.include_router(video.router, prefix="/api/v1/video", tags=["video"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Social Factory API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "video_service": video_service is not None,
        "model_loaded": video_service.model_loaded if video_service else False
    }

@app.get("/api/v1/status")
async def system_status():
    """Detailed system status"""
    return {
        "services": {
            "video_generation": video_service is not None,
            "llm": True,  # Add actual check
            "google_sheets": True,  # Add actual check
            "slack": True,  # Add actual check
            "wordpress": True  # Add actual check
        },
        "resources": {
            "gpu_available": video_service.gpu_available if video_service else False,
            "disk_space": "check_disk_space()",  # Implement
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_excludes=[
            "generated_videos/*",
            "logs/*",
            "*.log",
            "*.mp4",
            "*.db",
            "*.db-journal",
            "__pycache__/*",
            ".git/*",
            "venv/*",
            "local_t2v_model/*",
            ".pytest_cache/*"
        ]
    )
