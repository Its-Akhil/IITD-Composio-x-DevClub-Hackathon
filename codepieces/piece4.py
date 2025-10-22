# Generate API routes and remaining core files

# 10. Video API Routes
video_routes = '''"""
Video generation API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models import VideoRequest, VideoResponse
from app.services.video_service import VideoService
from app.core.security import get_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# This will be injected from main.py
_video_service: VideoService = None

def get_video_service():
    """Dependency to get video service"""
    if _video_service is None:
        raise HTTPException(status_code=503, detail="Video service not initialized")
    return _video_service

def set_video_service(service: VideoService):
    """Set video service instance"""
    global _video_service
    _video_service = service

@router.post("/generate", response_model=VideoResponse)
async def generate_video(
    request: VideoRequest,
    api_key: str = Depends(get_api_key),
    video_service: VideoService = Depends(get_video_service)
):
    """Generate video from text prompt"""
    try:
        logger.info(f"Video generation request: {request.prompt[:50]}...")
        result = await video_service.generate_video(request)
        return result
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def video_service_status(video_service: VideoService = Depends(get_video_service)):
    """Get video service status"""
    return {
        "model_loaded": video_service.model_loaded,
        "gpu_available": video_service.gpu_available,
        "device": video_service.device
    }
'''

# 11. Workflow API Routes
workflow_routes = '''"""
Workflow management API routes
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from app.models import WorkflowRequest, WorkflowResponse, ContentItem
from app.services.workflow_service import WorkflowService
from app.core.security import get_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global workflow service instance
workflow_service = WorkflowService()

@router.post("/execute", response_model=WorkflowResponse)
async def execute_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Execute workflow for a specific content item"""
    try:
        # Get content item from sheets
        content_items = await workflow_service.sheets_service.get_pending_content()
        content = next((c for c in content_items if c.id == request.content_id), None)
        
        if not content:
            raise HTTPException(status_code=404, detail=f"Content {request.content_id} not found")
        
        logger.info(f"Starting workflow for content {request.content_id}")
        
        result = await workflow_service.process_content_item(
            content,
            skip_approval=request.skip_approval,
            auto_publish=request.auto_publish
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-all")
async def process_all_pending(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Process all pending content items"""
    try:
        logger.info("Processing all pending content...")
        
        # Run in background
        background_tasks.add_task(workflow_service.process_all_pending)
        
        return {
            "status": "processing",
            "message": "Started processing all pending content in background"
        }
        
    except Exception as e:
        logger.error(f"Failed to start processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get workflow status"""
    status = workflow_service.active_workflows.get(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

def get_workflow_service():
    """Get workflow service instance"""
    return workflow_service
'''

# 12. Content API Routes
content_routes = '''"""
Content calendar API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import ContentItem, ContentStatus
from app.services.sheets_service import SheetsService
from app.core.security import get_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

sheets_service = SheetsService()

@router.get("/pending", response_model=List[ContentItem])
async def get_pending_content(api_key: str = Depends(get_api_key)):
    """Get all pending content items"""
    try:
        items = await sheets_service.get_pending_content()
        return items
    except Exception as e:
        logger.error(f"Failed to fetch pending content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{content_id}/status")
async def update_content_status(
    content_id: int,
    status: ContentStatus,
    video_url: str = None,
    post_id: str = None,
    api_key: str = Depends(get_api_key)
):
    """Update content item status"""
    try:
        await sheets_service.update_content_status(
            content_id,
            status,
            video_url=video_url,
            post_id=post_id
        )
        return {"status": "updated", "content_id": content_id}
    except Exception as e:
        logger.error(f"Failed to update status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''

# 13. Analytics API Routes
analytics_routes = '''"""
Analytics and reporting API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import List, Dict
from app.models import AnalyticsRequest, AnalyticsResponse
from app.services.sheets_service import SheetsService
from app.core.security import get_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

sheets_service = SheetsService()

@router.get("/summary")
async def get_analytics_summary(
    days: int = 7,
    api_key: str = Depends(get_api_key)
):
    """Get analytics summary for the last N days"""
    try:
        # This is a simplified version
        # In production, you'd query a proper database
        
        all_content = await sheets_service.get_pending_content()
        
        # Calculate basic stats
        total = len(all_content)
        pending = sum(1 for c in all_content if c.status.value == "Pending")
        
        return {
            "total_content": total,
            "pending": pending,
            "period_days": days,
            "success_rate": 0.85  # Placeholder
        }
        
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-stats")
async def get_daily_stats(
    start_date: str,
    end_date: str,
    api_key: str = Depends(get_api_key)
):
    """Get daily statistics"""
    return {
        "message": "Daily stats endpoint",
        "start_date": start_date,
        "end_date": end_date
    }
'''

# 14. Core security
security_code = '''"""
Security utilities for API authentication
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )
'''

# 15. Core logging
logging_code = '''"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    logger.info("Logging configured")
'''

# 16. Core exceptions
exceptions_code = '''"""
Custom exception classes
"""

class AIFactoryException(Exception):
    """Base exception for AI Social Factory"""
    pass

class VideoGenerationError(AIFactoryException):
    """Video generation failed"""
    pass

class LLMServiceError(AIFactoryException):
    """LLM service error"""
    pass

class SheetsServiceError(AIFactoryException):
    """Google Sheets service error"""
    pass

class SlackServiceError(AIFactoryException):
    """Slack service error"""
    pass

class WordPressServiceError(AIFactoryException):
    """WordPress service error"""
    pass

class WorkflowError(AIFactoryException):
    """Workflow execution error"""
    pass
'''

# Store all API routes and core files
api_files = {
    'app/api/routes/video.py': video_routes,
    'app/api/routes/workflow.py': workflow_routes,
    'app/api/routes/content.py': content_routes,
    'app/api/routes/analytics.py': analytics_routes,
    'app/core/security.py': security_code,
    'app/core/logging.py': logging_code,
    'app/core/exceptions.py': exceptions_code
}

print("✓ Video API routes")
print("✓ Workflow API routes")
print("✓ Content API routes")
print("✓ Analytics API routes")
print("✓ Core security module")
print("✓ Core logging module")
print("✓ Core exceptions module")
print(f"\nTotal API and core files: {len(api_files)}")
print("\nGenerating database, utilities, and configuration files...")