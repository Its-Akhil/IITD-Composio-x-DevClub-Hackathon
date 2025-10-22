"""
Content calendar API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import (
    ContentItem, ContentStatus, ScriptGenerationRequest, 
    ScriptGenerationResponse, CaptionRequest, CaptionResponse
)
from app.services.sheets_service import SheetsService
from app.services.llm_service import LLMService
from app.core.security import get_api_key
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

sheets_service = SheetsService()
llm_service = LLMService()

@router.get("/test")
async def test_gemini_api(api_key: str = Depends(get_api_key)):
    """Test Gemini API connection"""
    try:
        response = await llm_service._generate_content("Say 'Hello World' in 2 words")
        return {
            "status": "success",
            "message": "Gemini API is working",
            "response": response,
            "model": "gemini-2.5-flash"
        }
    except Exception as e:
        logger.error(f"Gemini API test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/generate-script", response_model=ScriptGenerationResponse)
async def generate_script(
    request: ScriptGenerationRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate script variants for content"""
    try:
        logger.info(f"Generating script for topic: {request.topic}")
        result = await llm_service.generate_script(request)
        return result
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-caption", response_model=CaptionResponse)
async def generate_caption(
    request: CaptionRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate platform-specific caption with hashtags"""
    try:
        logger.info(f"Generating caption for platform: {request.platform}")
        result = await llm_service.generate_caption(request)
        return result
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
