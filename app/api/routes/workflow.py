"""
Workflow management API routes
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models import WorkflowRequest, WorkflowResponse, ContentItem, ContentStatus
from app.services.workflow_service import WorkflowService
from app.services.video_service import VideoService
from app.core.security import get_api_key
from app.utils.logging_utils import sanitize_for_logging, truncate_html_error
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Global workflow service instance
workflow_service = WorkflowService()

def set_video_service(service: VideoService):
    """Set video service instance for workflow service"""
    global workflow_service
    workflow_service.set_video_service(service)
    logger.info("Video service injected into WorkflowService")

class DirectWorkflowRequest(BaseModel):
    """Direct workflow request without Google Sheets"""
    topic: str
    platform: str = "instagram"
    include_video: bool = True
    require_approval: bool = True

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

@router.post("/execute-direct")
async def execute_direct_workflow(
    request: DirectWorkflowRequest,
    api_key: str = Depends(get_api_key)
):
    """Execute workflow directly with topic (without Google Sheets)"""
    try:
        import uuid
        from datetime import datetime
        from app.models import ScriptGenerationRequest, CaptionRequest
        
        logger.info(f"Starting direct workflow for topic: {request.topic}")
        
        workflow_id = str(uuid.uuid4())
        steps = {}
        
        # Step 1: Generate script
        logger.info("Step 1: Generating script...")
        script_request = ScriptGenerationRequest(
            topic=request.topic,
            platform=request.platform,
            num_variants=3,
            target_duration=30
        )
        script_result = await workflow_service.llm_service.generate_script(script_request)
        steps["script_generation"] = "completed"
        selected_script = script_result.variants[0].script
        
        # Step 2: Generate caption
        logger.info("Step 2: Generating caption...")
        caption_request = CaptionRequest(
            script=selected_script,
            platform=request.platform,
            include_hashtags=True
        )
        caption_result = await workflow_service.llm_service.generate_caption(caption_request)
        steps["caption_generation"] = "completed"
        
        # Step 3: Generate video (if requested)
        video_url = None
        if request.include_video:
            logger.info("Step 3: Generating video...")
            try:
                if workflow_service.video_service is None:
                    logger.warning("Video service not available")
                    steps["video_generation"] = "skipped (service not available)"
                else:
                    from app.models import VideoRequest
                    video_request = VideoRequest(
                        prompt=selected_script[:200],  # Use first 200 chars
                        num_frames=16,
                        height=256,
                        width=256
                    )
                    video_result = await workflow_service.video_service.generate_video(video_request)
                    video_url = video_result.video_url
                    steps["video_generation"] = "completed"
            except Exception as e:
                logger.error(f"Video generation failed: {e}")
                steps["video_generation"] = "failed"
        else:
            steps["video_generation"] = "skipped"
        
        # Step 4: Create WordPress draft post
        wordpress_post_id = None
        wordpress_draft_url = None
        logger.info("Step 4: Creating WordPress draft post...")
        try:
            post_result = await workflow_service.wordpress_service.create_post(
                title=f"{request.topic} - {request.platform.capitalize()}",
                content=f"<p>{caption_result.caption}</p><p>{selected_script}</p>",
                status="draft",  # Always create as draft initially
                tags=caption_result.hashtags
            )
            wordpress_post_id = post_result.get('post_id')
            wordpress_draft_url = post_result.get('post_url')
            steps["wordpress_draft"] = "completed"
            logger.info(f"WordPress draft created: {wordpress_draft_url}")
        except Exception as e:
            # Sanitize error message for safe logging
            error_msg = truncate_html_error(str(e), max_length=200)
            logger.warning(f"WordPress draft creation failed: {error_msg}")
            steps["wordpress_draft"] = "failed (not configured)"
        
        # Step 5: Send Slack approval request
        slack_thread_ts = None
        if request.require_approval:
            logger.info("Step 5: Sending Slack approval request...")
            try:
                # Build approval message
                approval_message = (
                    f"🎬 *New Content Ready for Approval*\n\n"
                    f"*Topic:* {request.topic}\n"
                    f"*Platform:* {request.platform.capitalize()}\n"
                    f"*Caption:* {caption_result.caption}\n"
                    f"*Hashtags:* {' '.join(caption_result.hashtags)}\n"
                )
                if video_url:
                    approval_message += f"*Video:* http://localhost:8000{video_url}\n"
                if wordpress_draft_url:
                    approval_message += f"*WordPress Draft:* {wordpress_draft_url}\n"
                
                approval_message += (
                    f"\n*Script:*\n{selected_script[:200]}...\n\n"
                    f"*Workflow ID:* `{workflow_id}`\n"
                    f"*Post ID:* `{wordpress_post_id}`\n\n"
                    f"Reply with:\n"
                    f"• `approve` or `✅` to publish\n"
                    f"• `reject` or `❌` to cancel\n"
                    f"• `edit: <changes>` to request changes"
                )
                
                slack_result = await workflow_service.slack_service.send_approval_request(
                    topic=request.topic,
                    video_url=f"http://localhost:8000{video_url}" if video_url else None,
                    caption=caption_result.caption,
                    content_id=workflow_id,
                    workflow_id=workflow_id,
                    post_id=wordpress_post_id,
                    message=approval_message
                )
                
                # Slack webhooks don't return thread_ts, just confirmation
                slack_thread_ts = workflow_id  # Use workflow_id as reference
                if slack_result and slack_result.get('status') == 'sent':
                    steps["slack_approval"] = "sent (awaiting response)"
                    logger.info(f"Slack approval request sent: thread {slack_thread_ts}")
                else:
                    steps["slack_approval"] = "failed"
                    logger.warning("Slack approval request returned no confirmation")
            except Exception as e:
                safe_error = sanitize_for_logging(str(e), max_length=200)
                logger.warning(f"Slack approval request failed: {safe_error}")
                steps["slack_approval"] = "failed (not configured)"
        else:
            # Auto-publish if approval not required
            logger.info("Step 5: Auto-publishing (approval not required)...")
            if wordpress_post_id:
                try:
                    await workflow_service.wordpress_service.update_post_status(
                        wordpress_post_id,
                        "publish"
                    )
                    steps["wordpress_publish"] = "auto-published"
                except Exception as e:
                    logger.warning(f"Auto-publish failed: {e}")
                    steps["wordpress_publish"] = "failed"
            
            # Send success notification to Slack
            try:
                await workflow_service.slack_service.send_notification(
                    f"✅ Content auto-published for '{request.topic}'\n"
                    f"Platform: {request.platform}\n"
                    f"WordPress: {wordpress_draft_url or 'N/A'}",
                    "success"
                )
                steps["slack_notification"] = "completed"
            except Exception as e:
                logger.warning(f"Slack notification failed: {e}")
                steps["slack_notification"] = "failed"
        
        return {
            "workflow_id": workflow_id,
            "status": "completed" if not request.require_approval else "pending_approval",
            "topic": request.topic,
            "platform": request.platform,
            "steps": steps,
            "results": {
                "script": selected_script,
                "caption": caption_result.caption,
                "hashtags": caption_result.hashtags,
                "video_url": video_url,
                "wordpress_post_id": wordpress_post_id,
                "wordpress_draft_url": wordpress_draft_url,
                "slack_thread_ts": slack_thread_ts
            },
            "message": (
                "Content created as WordPress draft. Check Slack for approval request!" 
                if request.require_approval 
                else "Workflow executed and auto-published successfully!"
            ),
            "approval_required": request.require_approval
        }
        
    except Exception as e:
        logger.error(f"Direct workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/slack-approval")
async def handle_slack_approval(
    workflow_id: str,
    post_id: str = None,
    content_id: int = None,
    platform: str = "wordpress",
    approved: bool = True,
    user: str = "slack_user",
    comment: Optional[str] = None
    # Removed API key requirement - this is a public approval endpoint from Slack
):
    """Handle Slack approval response and publish to the specified platform"""
    try:
        logger.info(f"Handling approval for workflow {workflow_id}: approved={approved}, platform={platform}")
        
        if approved:
            platform_lower = platform.lower()
            
            # Publish to LinkedIn
            if platform_lower == "linkedin":
                try:
                    # Get content from sheets if content_id provided
                    if not content_id:
                        raise HTTPException(
                            status_code=400, 
                            detail="content_id is required for LinkedIn publishing"
                        )
                    
                    if not workflow_service.sheets_service.configured:
                        raise HTTPException(
                            status_code=500,
                            detail="Google Sheets not configured"
                        )
                    
                    # Get all records from sheets
                    import asyncio
                    records = await asyncio.to_thread(workflow_service.sheets_service.worksheet.get_all_records)
                    logger.info(f"Found {len(records)} records in Google Sheets")
                    
                    # Get the specific row (content_id is the row number, subtract 2 for header + 0-index)
                    if content_id < 2 or content_id - 2 >= len(records):
                        raise HTTPException(
                            status_code=404,
                            detail=f"Content row {content_id} not found in sheets"
                        )
                    
                    content_row = records[content_id - 2]
                    logger.info(f"Content row data: {content_row}")
                    
                    # Extract data from sheets - ALL data should be there already!
                    topic = content_row.get('Topic', '')
                    video_url = content_row.get('Video_URL', '')
                    caption = content_row.get('Caption', '')
                    script = content_row.get('Script', '')
                    
                    if not topic:
                        raise HTTPException(
                            status_code=400,
                            detail="Topic is missing from the content row"
                        )
                    
                    # If caption not in sheets, use topic as fallback
                    if not caption:
                        logger.warning(f"Caption not found in sheets for row {content_id}, using topic")
                        caption = f"Check out this content about {topic}! #AI #Innovation"
                    
                    logger.info(f"Publishing to LinkedIn: {topic}")
                    logger.info(f"Video URL: {video_url}")
                    logger.info(f"Caption (first 100 chars): {caption[:100]}...")
                    
                    # Publish to LinkedIn
                    logger.info(f"Calling LinkedIn API to create post...")
                    result = await workflow_service.linkedin_service.create_post(
                        text=caption,
                        video_url=video_url if video_url else None
                    )
                    logger.info(f"LinkedIn post created successfully: {result.get('post_id')}")
                    
                    # Update sheets with published status
                    logger.info(f"Updating Google Sheets row {content_id} to Published status...")
                    await workflow_service.sheets_service.update_content_status(
                        row_id=content_id,
                        status=ContentStatus.PUBLISHED,
                        post_id=result['post_id'],
                        approved_by=user
                    )
                    logger.info(f"Google Sheets updated successfully for row {content_id}")
                    
                    # Send success notification
                    await workflow_service.slack_service.send_notification(
                        f"✅ Content approved by {user} and published to LinkedIn!\n"
                        f"Post URL: {result['post_url']}\n"
                        f"Topic: {topic}\n"
                        f"Workflow ID: {workflow_id}",
                        "success"
                    )
                    
                    return {
                        "status": "approved",
                        "workflow_id": workflow_id,
                        "content_id": content_id,
                        "post_id": result['post_id'],
                        "post_url": result['post_url'],
                        "platform": "linkedin",
                        "published": True,
                        "message": f"Content '{topic}' approved and published to LinkedIn"
                    }
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Failed to publish to LinkedIn: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise HTTPException(status_code=500, detail=f"LinkedIn publishing failed: {str(e)}")
            
            # Publish to WordPress
            elif platform_lower in ["wordpress", "blog"]:
                try:
                    result = await workflow_service.wordpress_service.update_post_status(
                        post_id,
                        "publish"
                    )
                    
                    # Send success notification
                    await workflow_service.slack_service.send_notification(
                        f"✅ Content approved by {user} and published to WordPress!\n"
                        f"Post ID: {post_id}\n"
                        f"Workflow ID: {workflow_id}",
                        "success"
                    )
                    
                    return {
                        "status": "approved",
                        "workflow_id": workflow_id,
                        "post_id": post_id,
                        "platform": "wordpress",
                        "published": True,
                        "message": "Content approved and published to WordPress"
                    }
                except Exception as e:
                    logger.error(f"Failed to publish to WordPress: {e}")
                    raise HTTPException(status_code=500, detail=f"WordPress publishing failed: {str(e)}")
            
            else:
                return {
                    "status": "error",
                    "message": f"Platform '{platform}' not supported for direct publishing"
                }
        
        else:
            # Rejection
            await workflow_service.slack_service.send_notification(
                f"❌ Content rejected by {user}\n"
                f"Platform: {platform}\n"
                f"Workflow ID: {workflow_id}\n"
                f"Comment: {comment or 'No comment provided'}",
                "error"
            )
            
            # Update sheets if content_id provided
            if content_id and workflow_service.sheets_service.configured:
                await workflow_service.sheets_service.update_content_status(
                    row_id=content_id,
                    status=ContentStatus.REJECTED
                )
            
            return {
                "status": "rejected",
                "workflow_id": workflow_id,
                "platform": platform,
                "published": False,
                "message": "Content rejected"
            }
            
    except Exception as e:
        logger.error(f"Slack approval handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=WorkflowResponse)
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

@router.post("/process-sheets")
async def process_sheets_workflow(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Process all pending content items from Google Sheets"""
    try:
        logger.info("Starting Google Sheets workflow processing...")
        
        # Get pending items from Google Sheets
        pending_items = await workflow_service.sheets_service.get_pending_content()
        
        if not pending_items:
            return {
                "status": "success",
                "message": "No pending content found in Google Sheets",
                "items_processed": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"Found {len(pending_items)} pending items in Google Sheets")
        
        # Process each item
        results = []
        for item in pending_items:
            try:
                logger.info(f"Processing content item {item.id}: {item.topic}")
                
                # Update status to Generating
                await workflow_service.sheets_service.update_content_status(
                    row_id=item.id,
                    status=ContentStatus.GENERATING
                )
                
                # Process the item
                result = await workflow_service.process_content_item(
                    item,
                    skip_approval=False,
                    auto_publish=False
                )
                
                results.append({
                    "content_id": item.id,
                    "topic": item.topic,
                    "status": "success",
                    "workflow_id": result.workflow_id if hasattr(result, 'workflow_id') else str(result)
                })
                
            except Exception as e:
                logger.error(f"Failed to process content {item.id}: {e}")
                
                # Update status to Failed
                await workflow_service.sheets_service.update_content_status(
                    row_id=item.id,
                    status=ContentStatus.FAILED
                )
                
                # Log error
                await workflow_service.sheets_service.log_error(
                    row_id=item.id,
                    error_message=str(e)
                )
                
                results.append({
                    "content_id": item.id,
                    "topic": item.topic,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "message": f"Processed {len(pending_items)} content items from Google Sheets",
            "items_processed": len(pending_items),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Google Sheets workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-slack")
async def test_slack_notification(api_key: str = Depends(get_api_key)):
    """Test Slack notification"""
    try:
        await workflow_service.slack_service.send_notification(
            "🧪 Test notification from AI Social Factory frontend",
            "info"
        )
        return {
            "status": "success",
            "message": "Test notification sent to Slack",
            "timestamp": "2025-10-21T23:00:00Z"
        }
    except Exception as e:
        logger.error(f"Slack test failed: {e}")
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
