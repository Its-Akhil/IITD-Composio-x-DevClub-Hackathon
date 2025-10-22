# Continue with WordPress, Workflow Service, and API Routes

# 8. WordPress Service
wordpress_service = '''"""
WordPress REST API integration service
"""
import logging
import base64
import aiohttp
from typing import Optional, Dict, Any
from app.config import settings
from app.core.exceptions import WordPressServiceError

logger = logging.getLogger(__name__)

class WordPressService:
    """WordPress REST API service"""
    
    def __init__(self):
        self.site_url = settings.WORDPRESS_SITE_URL
        self.username = settings.WORDPRESS_USERNAME
        self.app_password = settings.WORDPRESS_APP_PASSWORD
        self.configured = all([self.site_url, self.username, self.app_password])
        
        if self.configured:
            # Create Basic Auth header
            credentials = f"{self.username}:{self.app_password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self.auth_header = f"Basic {encoded}"
            logger.info("WordPress service initialized")
        else:
            logger.warning("WordPress not configured")
    
    async def create_post(
        self,
        title: str,
        content: str,
        video_url: str,
        caption: str,
        categories: Optional[list] = None,
        tags: Optional[list] = None,
        status: str = "publish"
    ) -> Dict[str, Any]:
        """Create a new WordPress post"""
        if not self.configured:
            raise WordPressServiceError("WordPress not configured")
        
        # Embed video in content
        video_embed = f"""
        <video controls width="100%">
            <source src="{video_url}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <p>{caption}</p>
        """
        
        full_content = video_embed + content
        
        endpoint = f"{self.site_url}/wp-json/wp/v2/posts"
        
        payload = {
            "title": title,
            "content": full_content,
            "status": status,
            "categories": categories or [1],  # Default to Uncategorized
            "tags": tags or [],
            "meta": {
                "ai_generated": True,
                "video_url": video_url,
                "generation_timestamp": "2025-10-21T17:00:00"
            }
        }
        
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        post_id = data.get('id')
                        post_url = data.get('link')
                        logger.info(f"Post created: {post_id} - {post_url}")
                        return {
                            "post_id": post_id,
                            "post_url": post_url,
                            "status": "published"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"WordPress API error: {error_text}")
                        raise WordPressServiceError(f"Post creation failed: {error_text}")
        except Exception as e:
            logger.error(f"Failed to create WordPress post: {e}")
            raise WordPressServiceError(f"Post creation failed: {str(e)}")
    
    async def update_post(self, post_id: int, updates: Dict[str, Any]):
        """Update existing WordPress post"""
        if not self.configured:
            raise WordPressServiceError("WordPress not configured")
        
        endpoint = f"{self.site_url}/wp-json/wp/v2/posts/{post_id}"
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=updates, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Post {post_id} updated successfully")
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise WordPressServiceError(f"Update failed: {error_text}")
        except Exception as e:
            logger.error(f"Failed to update post: {e}")
            raise WordPressServiceError(f"Update failed: {str(e)}")
'''

# 9. Workflow Service (Orchestration)
workflow_service = '''"""
Workflow orchestration service
Coordinates the entire content generation and publishing pipeline
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models import ContentItem, ContentStatus, WorkflowResponse
from app.models import VideoRequest, ScriptGenerationRequest, CaptionRequest
from app.services.video_service import VideoService
from app.services.llm_service import LLMService
from app.services.sheets_service import SheetsService
from app.services.slack_service import SlackService
from app.services.wordpress_service import WordPressService
from app.core.exceptions import WorkflowError

logger = logging.getLogger(__name__)

class WorkflowService:
    """Main workflow orchestration service"""
    
    def __init__(self):
        self.video_service = None
        self.llm_service = LLMService()
        self.sheets_service = SheetsService()
        self.slack_service = SlackService()
        self.wordpress_service = WordPressService()
        self.active_workflows: Dict[str, Dict] = {}
        logger.info("WorkflowService initialized")
    
    def set_video_service(self, video_service: VideoService):
        """Set video service (injected from main app)"""
        self.video_service = video_service
    
    async def process_content_item(
        self,
        content: ContentItem,
        skip_approval: bool = False,
        auto_publish: bool = False
    ) -> WorkflowResponse:
        """Process a single content item through the full pipeline"""
        workflow_id = f"wf_{content.id}_{datetime.now().timestamp()}"
        started_at = datetime.now()
        steps_completed = []
        errors = []
        current_step = "initialized"
        
        try:
            # Step 1: Analyze trend
            current_step = "trend_analysis"
            logger.info(f"[{workflow_id}] Step 1: Analyzing trend for '{content.topic}'")
            
            try:
                trend_insights = await self.llm_service.analyze_trend(content.topic)
                steps_completed.append("trend_analysis")
                logger.info(f"[{workflow_id}] Trend analysis complete")
            except Exception as e:
                logger.warning(f"Trend analysis failed: {e}, continuing...")
                trend_insights = {}
            
            # Step 2: Generate scripts
            current_step = "script_generation"
            logger.info(f"[{workflow_id}] Step 2: Generating scripts")
            
            script_request = ScriptGenerationRequest(
                topic=content.topic,
                platform=content.platform,
                num_variants=3,
                target_duration=10
            )
            
            script_response = await self.llm_service.generate_scripts(script_request)
            steps_completed.append("script_generation")
            
            # Use variant A for video generation
            selected_script = script_response.variants[0].script
            logger.info(f"[{workflow_id}] Script generated: {selected_script[:100]}...")
            
            # Step 3: Generate video
            current_step = "video_generation"
            logger.info(f"[{workflow_id}] Step 3: Generating video")
            
            if not self.video_service or not self.video_service.model_loaded:
                raise WorkflowError("Video service not available")
            
            # Use the video_prompt if provided, otherwise use the script
            video_prompt = content.video_prompt or selected_script
            
            video_request = VideoRequest(
                prompt=video_prompt,
                num_frames=16,
                height=256,
                width=256
            )
            
            video_response = await self.video_service.generate_video(video_request)
            steps_completed.append("video_generation")
            
            video_url = f"http://localhost:8000{video_response.video_url}"
            logger.info(f"[{workflow_id}] Video generated: {video_url}")
            
            # Update Google Sheets with video URL
            if self.sheets_service.configured:
                await self.sheets_service.update_content_status(
                    content.id,
                    ContentStatus.REVIEW,
                    video_url=video_url
                )
            
            # Step 4: Generate caption
            current_step = "caption_generation"
            logger.info(f"[{workflow_id}] Step 4: Generating caption")
            
            caption_request = CaptionRequest(
                script=selected_script,
                platform=content.platform,
                include_hashtags=True
            )
            
            caption_response = await self.llm_service.generate_caption(caption_request)
            steps_completed.append("caption_generation")
            
            caption_text = f"{caption_response.caption}\\n\\n{' '.join(['#' + tag for tag in caption_response.hashtags])}"
            logger.info(f"[{workflow_id}] Caption generated")
            
            # Step 5: Send for approval (unless skipped)
            if not skip_approval:
                current_step = "approval_request"
                logger.info(f"[{workflow_id}] Step 5: Sending approval request")
                
                if self.slack_service.configured:
                    await self.slack_service.send_approval_request(
                        topic=content.topic,
                        video_url=video_url,
                        caption=caption_text,
                        content_id=content.id
                    )
                    steps_completed.append("approval_request")
                    logger.info(f"[{workflow_id}] Approval request sent to Slack")
                else:
                    logger.warning("Slack not configured, skipping approval")
            
            # Step 6: Publish (if auto_publish or skip_approval)
            if auto_publish or skip_approval:
                current_step = "publishing"
                logger.info(f"[{workflow_id}] Step 6: Publishing to WordPress")
                
                if self.wordpress_service.configured:
                    post_result = await self.wordpress_service.create_post(
                        title=content.topic,
                        content="",
                        video_url=video_url,
                        caption=caption_text,
                        tags=caption_response.hashtags,
                        status="publish"
                    )
                    steps_completed.append("publishing")
                    
                    # Update sheets with post ID
                    if self.sheets_service.configured:
                        await self.sheets_service.update_content_status(
                            content.id,
                            ContentStatus.PUBLISHED,
                            video_url=video_url,
                            post_id=str(post_result['post_id'])
                        )
                    
                    logger.info(f"[{workflow_id}] Published: {post_result['post_url']}")
                else:
                    logger.warning("WordPress not configured, skipping publish")
            
            completed_at = datetime.now()
            
            return WorkflowResponse(
                workflow_id=workflow_id,
                content_id=content.id,
                status="completed" if not errors else "completed_with_warnings",
                steps_completed=steps_completed,
                current_step=current_step,
                errors=errors,
                started_at=started_at,
                completed_at=completed_at
            )
            
        except Exception as e:
            logger.error(f"[{workflow_id}] Workflow failed at step '{current_step}': {e}")
            errors.append(f"{current_step}: {str(e)}")
            
            # Log error to sheets
            if self.sheets_service.configured:
                try:
                    await self.sheets_service.update_content_status(
                        content.id,
                        ContentStatus.FAILED
                    )
                    await self.sheets_service.log_error(content.id, str(e))
                except:
                    pass
            
            return WorkflowResponse(
                workflow_id=workflow_id,
                content_id=content.id,
                status="failed",
                steps_completed=steps_completed,
                current_step=current_step,
                errors=errors,
                started_at=started_at,
                completed_at=datetime.now()
            )
    
    async def process_all_pending(self) -> List[WorkflowResponse]:
        """Process all pending content items from Google Sheets"""
        logger.info("Processing all pending content items...")
        
        if not self.sheets_service.configured:
            raise WorkflowError("Google Sheets not configured")
        
        pending_items = await self.sheets_service.get_pending_content()
        logger.info(f"Found {len(pending_items)} pending items")
        
        results = []
        for item in pending_items:
            try:
                result = await self.process_content_item(item, skip_approval=False)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process content {item.id}: {e}")
        
        return results
'''

print("✓ WordPress Service")
print("✓ Workflow Service")
print("\nGenerating API routes...")
