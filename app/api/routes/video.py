"""
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
