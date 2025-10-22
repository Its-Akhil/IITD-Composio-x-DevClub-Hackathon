import os
import json

# Create the complete Python backend project structure

project_structure = """
ai-social-factory/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── models.py                  # Pydantic models
│   ├── database.py                # Database connection (SQLite)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── video.py          # Video generation endpoints
│   │   │   ├── workflow.py       # Workflow management endpoints
│   │   │   ├── content.py        # Content calendar endpoints
│   │   │   └── analytics.py      # Analytics endpoints
│   │   └── dependencies.py       # Shared dependencies
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_service.py      # ModelScope video generation
│   │   ├── llm_service.py        # Gemini API integration
│   │   ├── sheets_service.py     # Google Sheets integration
│   │   ├── slack_service.py      # Slack webhooks
│   │   ├── wordpress_service.py  # WordPress publishing
│   │   └── workflow_service.py   # Workflow orchestration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py           # API key management
│   │   ├── logging.py            # Logging configuration
│   │   └── exceptions.py         # Custom exceptions
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py         # File operations
│       └── validators.py         # Input validators
├── tests/
│   ├── __init__.py
│   ├── test_video_service.py
│   ├── test_llm_service.py
│   └── test_workflow.py
├── scripts/
│   ├── download_model.py         # Download ModelScope model
│   ├── setup_db.py               # Initialize database
│   └── test_apis.py              # Test external APIs
├── generated_videos/             # Video output directory
├── local_t2v_model/              # Cached model directory
├── logs/                         # Application logs
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
└── docker-compose.yml
"""

print("AI SOCIAL FACTORY - PYTHON BACKEND PROJECT")
print("=" * 70)
print("\nProject Structure:")
print(project_structure)
print("\n" + "=" * 70)
print("GENERATING BACKEND FILES...\n")

# Track all files to be created
files_to_create = {}

# 1. Main FastAPI application
files_to_create['app/main.py'] = '''"""
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

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize video service at startup
video_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global video_service
    
    # Startup
    logger.info("Starting AI Social Factory...")
    try:
        video_service = VideoService()
        await video_service.load_model()
        logger.info("Video model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load video model: {e}")
        logger.warning("Running without video generation capability")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Social Factory...")
    if video_service:
        await video_service.cleanup()

# Create FastAPI app
app = FastAPI(
    title="AI Social Factory API",
    description="Automated content generation and publishing platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for generated videos
app.mount("/videos", StaticFiles(directory="generated_videos"), name="videos")

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
        reload=settings.DEBUG
    )
'''

# 2. Configuration management
files_to_create['app/config.py'] = '''"""
Configuration management using Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Social Factory"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    API_KEY: str = "change-this-in-production"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5678"]
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = 0.9
    
    # Video Generation
    VIDEO_MODEL_PATH: str = "./local_t2v_model"
    VIDEO_OUTPUT_DIR: str = "./generated_videos"
    VIDEO_NUM_FRAMES: int = 16
    VIDEO_HEIGHT: int = 256
    VIDEO_WIDTH: int = 256
    USE_GPU: bool = True
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = "./credentials.json"
    GOOGLE_SHEETS_SPREADSHEET_ID: str = ""
    GOOGLE_SHEETS_SHEET_NAME: str = "Content_Calendar"
    
    # Slack
    SLACK_WEBHOOK_URL: str = ""
    SLACK_BOT_TOKEN: str = ""
    SLACK_CHANNEL: str = "#content-review"
    
    # WordPress
    WORDPRESS_SITE_URL: str = ""
    WORDPRESS_USERNAME: str = ""
    WORDPRESS_APP_PASSWORD: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./ai_social_factory.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Workflow
    MAX_CONCURRENT_VIDEOS: int = 3
    VIDEO_GENERATION_TIMEOUT: int = 180  # seconds
    APPROVAL_TIMEOUT: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
'''

# 3. Pydantic models
files_to_create['app/models.py'] = '''"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContentStatus(str, Enum):
    """Content status enum"""
    PENDING = "Pending"
    GENERATING = "Generating"
    REVIEW = "Review"
    APPROVED = "Approved"
    PUBLISHED = "Published"
    FAILED = "Failed"
    REJECTED = "Rejected"

class VideoRequest(BaseModel):
    """Video generation request"""
    prompt: str = Field(..., min_length=10, max_length=500)
    num_frames: int = Field(default=16, ge=8, le=32)
    height: int = Field(default=256, ge=128, le=512)
    width: int = Field(default=256, ge=128, le=512)
    negative_prompt: Optional[str] = None
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class VideoResponse(BaseModel):
    """Video generation response"""
    video_id: str
    video_url: str
    status: str
    prompt: str
    num_frames: int
    resolution: str
    generation_time: float
    created_at: datetime

class ScriptVariant(BaseModel):
    """Script variant model"""
    variant_id: str
    script: str
    style: str
    duration_estimate: int  # seconds

class ScriptGenerationRequest(BaseModel):
    """Script generation request"""
    topic: str = Field(..., min_length=3, max_length=200)
    platform: str = Field(default="general")
    num_variants: int = Field(default=3, ge=1, le=5)
    target_duration: int = Field(default=10, ge=5, le=60)

class ScriptGenerationResponse(BaseModel):
    """Script generation response"""
    topic: str
    variants: List[ScriptVariant]
    metadata: Dict[str, Any]

class CaptionRequest(BaseModel):
    """Caption generation request"""
    script: str
    platform: str = Field(..., regex="^(instagram|youtube|tiktok|linkedin|twitter)$")
    include_hashtags: bool = True
    max_length: Optional[int] = None

class CaptionResponse(BaseModel):
    """Caption generation response"""
    caption: str
    hashtags: List[str]
    platform: str
    character_count: int

class ContentItem(BaseModel):
    """Content calendar item"""
    id: Optional[int] = None
    date: datetime
    topic: str
    video_prompt: str
    status: ContentStatus
    video_url: Optional[str] = None
    platform: str
    approved_by: Optional[str] = None
    post_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class WorkflowRequest(BaseModel):
    """Workflow execution request"""
    content_id: int
    skip_approval: bool = False
    auto_publish: bool = False

class WorkflowResponse(BaseModel):
    """Workflow execution response"""
    workflow_id: str
    content_id: int
    status: str
    steps_completed: List[str]
    current_step: str
    errors: List[str]
    started_at: datetime
    completed_at: Optional[datetime] = None

class AnalyticsRequest(BaseModel):
    """Analytics query request"""
    start_date: datetime
    end_date: datetime
    platforms: Optional[List[str]] = None
    status_filter: Optional[List[ContentStatus]] = None

class AnalyticsResponse(BaseModel):
    """Analytics response"""
    total_videos: int
    successful: int
    failed: int
    pending: int
    success_rate: float
    avg_generation_time: float
    platform_breakdown: Dict[str, int]
    daily_stats: List[Dict[str, Any]]
'''

# 4. Video Service (ModelScope integration)
files_to_create['app/services/video_service.py'] = '''"""
Video generation service using ModelScope text-to-video model
"""
import torch
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio
from functools import lru_cache

from diffusers import DiffusionPipeline
from app.config import settings
from app.models import VideoRequest, VideoResponse
from app.core.exceptions import VideoGenerationError

logger = logging.getLogger(__name__)

class VideoService:
    """Video generation service"""
    
    def __init__(self):
        self.pipe = None
        self.model_loaded = False
        self.gpu_available = torch.cuda.is_available()
        self.device = "cuda" if self.gpu_available and settings.USE_GPU else "cpu"
        self.output_dir = Path(settings.VIDEO_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"VideoService initialized - Device: {self.device}")
    
    async def load_model(self):
        """Load ModelScope text-to-video model"""
        try:
            logger.info("Loading ModelScope text-to-video model...")
            
            model_path = Path(settings.VIDEO_MODEL_PATH)
            
            if model_path.exists():
                logger.info(f"Loading model from {model_path}")
                self.pipe = DiffusionPipeline.from_pretrained(
                    str(model_path),
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            else:
                logger.info("Downloading model from HuggingFace...")
                self.pipe = DiffusionPipeline.from_pretrained(
                    "damo-vilab/text-to-video-ms-1.7b",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None
                )
                # Cache for future use
                logger.info(f"Saving model to {model_path}")
                model_path.mkdir(exist_ok=True, parents=True)
                self.pipe.save_pretrained(str(model_path))
            
            self.pipe.to(self.device)
            self.model_loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise VideoGenerationError(f"Model loading failed: {str(e)}")
    
    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """Generate video from text prompt"""
        if not self.model_loaded:
            raise VideoGenerationError("Model not loaded")
        
        start_time = datetime.now()
        video_id = str(uuid.uuid4())
        output_path = self.output_dir / f"{video_id}.mp4"
        
        try:
            logger.info(f"Generating video: {video_id}")
            logger.info(f"Prompt: {request.prompt}")
            
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._generate_video_sync,
                request.prompt,
                request.num_frames,
                request.height,
                request.width,
                request.negative_prompt
            )
            
            # Save video
            video_frames = result.frames
            self.pipe.save_videos_grid(video_frames, str(output_path))
            
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Video generated in {generation_time:.2f}s: {video_id}")
            
            return VideoResponse(
                video_id=video_id,
                video_url=f"/videos/{video_id}.mp4",
                status="success",
                prompt=request.prompt,
                num_frames=request.num_frames,
                resolution=f"{request.width}x{request.height}",
                generation_time=generation_time,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise VideoGenerationError(f"Generation failed: {str(e)}")
    
    def _generate_video_sync(
        self,
        prompt: str,
        num_frames: int,
        height: int,
        width: int,
        negative_prompt: Optional[str] = None
    ):
        """Synchronous video generation (runs in thread pool)"""
        return self.pipe(
            prompt,
            num_frames=num_frames,
            height=height,
            width=width,
            negative_prompt=negative_prompt,
            num_inference_steps=25
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up VideoService...")
        if self.pipe:
            del self.pipe
            if self.device == "cuda":
                torch.cuda.empty_cache()
        self.model_loaded = False
'''

print("File generation progress:")
print(f"✓ Generated {len(files_to_create)} core files")
print("\nContinuing with remaining services...")
