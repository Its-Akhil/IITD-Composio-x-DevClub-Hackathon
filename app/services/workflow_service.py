"""
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
from app.services.linkedin_service import LinkedInService
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
        self.linkedin_service = LinkedInService()
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
            
            if not self.video_service:
                raise WorkflowError("Video service not available")
            
            # Use the video_prompt if provided, otherwise use the script
            video_prompt = content.video_prompt or selected_script
            
            video_request = VideoRequest(
                prompt=video_prompt,
                num_frames=16,
                height=256,
                width=256
            )
            
            # generate_video will load the model if needed
            video_response = await self.video_service.generate_video(video_request)
            steps_completed.append("video_generation")
            
            video_url = f"http://localhost:8000{video_response.video_url}"
            logger.info(f"[{workflow_id}] Video generated: {video_url}")
            
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
            
            caption_text = f"{caption_response.caption}\n\n{' '.join(['#' + tag for tag in caption_response.hashtags])}"
            logger.info(f"[{workflow_id}] Caption generated")
            
            # Save all generated content to Google Sheets
            if self.sheets_service.configured:
                await self.sheets_service.update_content_status(
                    row_id=content.id,
                    status=ContentStatus.REVIEW,
                    video_url=video_url,
                    caption=caption_text,
                    script=selected_script,
                    workflow_id=workflow_id
                )
                logger.info(f"[{workflow_id}] All content data saved to Google Sheets")
            
            # Step 5: Send for approval (unless skipped)
            if not skip_approval:
                current_step = "approval_request"
                logger.info(f"[{workflow_id}] Step 5: Sending approval request")
                
                if self.slack_service.configured:
                    # Generate approval URL with all parameters
                    from urllib.parse import urlencode
                    approval_params = {
                        'workflow_id': workflow_id,
                        'content_id': str(content.id),
                        'platform': content.platform
                    }
                    approval_url = f"http://localhost:8000/frontend/approve.html?{urlencode(approval_params)}"
                    
                    await self.slack_service.send_approval_request(
                        topic=content.topic,
                        video_url=video_url,
                        caption=caption_text,
                        content_id=content.id,
                        workflow_id=workflow_id,
                        platform=content.platform,
                        script=selected_script,
                        approval_url=approval_url
                    )
                    steps_completed.append("approval_request")
                    logger.info(f"[{workflow_id}] Approval request sent to Slack with URL: {approval_url}")
                else:
                    logger.warning("Slack not configured, skipping approval")
            
            # Step 6: Publish (if auto_publish or skip_approval)
            if auto_publish or skip_approval:
                current_step = "publishing"
                platform = content.platform.lower()
                logger.info(f"[{workflow_id}] Step 6: Publishing to {platform}")
                
                post_result = None
                
                # Publish to the appropriate platform
                if platform == "linkedin":
                    if self.linkedin_service.configured:
                        try:
                            post_result = await self.linkedin_service.create_post(
                                text=caption_text,
                                video_url=video_url if video_url else None
                            )
                            steps_completed.append(f"publishing_{platform}")
                            logger.info(f"[{workflow_id}] Published to LinkedIn: {post_result['post_url']}")
                        except Exception as e:
                            logger.error(f"LinkedIn publishing failed: {e}")
                            errors.append(f"LinkedIn publish: {str(e)}")
                    else:
                        logger.warning("LinkedIn not configured, skipping publish")
                        errors.append("LinkedIn not configured")
                
                elif platform in ["wordpress", "blog"]:
                    if self.wordpress_service.configured:
                        try:
                            post_result = await self.wordpress_service.create_post(
                                title=content.topic,
                                content="",
                                video_url=video_url,
                                caption=caption_text,
                                tags=caption_response.hashtags,
                                status="publish"
                            )
                            steps_completed.append(f"publishing_{platform}")
                            logger.info(f"[{workflow_id}] Published to WordPress: {post_result['post_url']}")
                        except Exception as e:
                            logger.error(f"WordPress publishing failed: {e}")
                            errors.append(f"WordPress publish: {str(e)}")
                    else:
                        logger.warning("WordPress not configured, skipping publish")
                        errors.append("WordPress not configured")
                
                else:
                    # Default to WordPress for other platforms (instagram, youtube, tiktok)
                    # These would need their own integrations
                    logger.warning(f"Platform '{platform}' not directly supported, creating WordPress draft")
                    if self.wordpress_service.configured:
                        try:
                            post_result = await self.wordpress_service.create_post(
                                title=f"{content.topic} [{platform.upper()}]",
                                content="",
                                video_url=video_url,
                                caption=caption_text,
                                tags=caption_response.hashtags,
                                status="draft"  # Create as draft for manual posting
                            )
                            steps_completed.append(f"draft_created_{platform}")
                            logger.info(f"[{workflow_id}] Created draft for {platform}: {post_result['post_url']}")
                        except Exception as e:
                            logger.error(f"Draft creation failed: {e}")
                            errors.append(f"Draft creation: {str(e)}")
                
                # Update sheets with post ID if published
                if post_result and self.sheets_service.configured:
                    try:
                        await self.sheets_service.update_content_status(
                            content.id,
                            ContentStatus.PUBLISHED,
                            video_url=video_url,
                            post_id=str(post_result.get('post_id', ''))
                        )
                    except Exception as e:
                        logger.error(f"Failed to update sheets: {e}")

            
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
