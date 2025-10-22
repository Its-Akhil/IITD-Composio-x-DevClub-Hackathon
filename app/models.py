"""
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
    platform: str = Field(..., pattern="^(instagram|youtube|tiktok|linkedin|twitter|wordpress)$")
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
