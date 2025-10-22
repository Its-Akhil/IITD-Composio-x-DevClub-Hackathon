"""
Background task for auto-processing Google Sheets content
"""
import asyncio
import logging
from datetime import datetime
from typing import Set
from app.config import settings
from app.services.workflow_service import WorkflowService
from app.services.sheets_service import SheetsService
from app.services.slack_service import SlackService
from app.models import ContentStatus

logger = logging.getLogger(__name__)

class AutoProcessor:
    """
    Background service that polls Google Sheets and automatically processes pending content
    """
    
    def __init__(self, workflow_service: WorkflowService):
        self.workflow_service = workflow_service
        self.sheets_service = workflow_service.sheets_service
        self.slack_service = workflow_service.slack_service
        self.running = False
        self.processed_ids: Set[int] = set()  # Track processed items to avoid duplicates
        
    async def start(self):
        """Start the auto-processing loop in a background task (non-blocking)"""
        if not settings.AUTO_PROCESS_ENABLED:
            logger.info("Auto-processing is disabled")
            return
        
        if not self.sheets_service.configured:
            logger.warning("Google Sheets not configured - auto-processing disabled")
            return
        
        self.running = True
        logger.info(f"Auto-processor started - checking every {settings.SHEETS_POLLING_INTERVAL} seconds")
        
        # Send startup notification to Slack
        if self.slack_service.configured:
            try:
                await self.slack_service.send_notification(
                    f"🤖 Auto-Processor Started\n"
                    f"Monitoring Google Sheets every {settings.SHEETS_POLLING_INTERVAL} seconds\n"
                    f"Ready to process pending content automatically!",
                    "info"
                )
            except:
                pass
        
        # Run the processing loop in the background without blocking
        while self.running:
            try:
                # Create a background task for processing - don't await it!
                asyncio.create_task(self._check_and_process())
            except Exception as e:
                logger.error(f"Error starting check_and_process task: {e}")
            
            # Wait before next check
            await asyncio.sleep(settings.SHEETS_POLLING_INTERVAL)
    
    async def stop(self):
        """Stop the auto-processing loop"""
        self.running = False
        logger.info("Auto-processor stopped")
        
        # Send shutdown notification to Slack
        if self.slack_service.configured:
            try:
                await self.slack_service.send_notification(
                    "🛑 Auto-Processor Stopped",
                    "warning"
                )
            except:
                pass
    
    async def _check_and_process(self):
        """Check for pending items and process them"""
        try:
            # Fetch pending items
            pending_items = await self.sheets_service.get_pending_content()
            
            # Filter out already processed items
            new_items = [item for item in pending_items if item.id not in self.processed_ids]
            
            if not new_items:
                logger.debug("No new pending items found")
                return
            
            logger.info(f"Found {len(new_items)} new pending item(s) in Google Sheets")
            
            # Notify Slack about new items
            if self.slack_service.configured and len(new_items) > 0:
                try:
                    item_list = "\n".join([f"  • Row {item.id}: {item.topic} ({item.platform})" for item in new_items])
                    await self.slack_service.send_notification(
                        f"📋 New Content Detected!\n\n"
                        f"Found {len(new_items)} pending item(s):\n{item_list}\n\n"
                        f"Starting automatic processing...",
                        "info"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send Slack notification: {e}")
            
            # Process each new item in parallel (create tasks, don't await them)
            tasks = []
            for item in new_items:
                # Mark as being processed immediately
                self.processed_ids.add(item.id)
                # Create a background task for each item
                task = asyncio.create_task(self._process_single_item(item))
                tasks.append(task)
            
            # Optionally wait for all tasks to complete (or let them run in background)
            if tasks:
                logger.info(f"Started {len(tasks)} processing task(s) in parallel")
        
        except Exception as e:
            logger.error(f"Error checking for pending items: {e}")
    
    async def _process_single_item(self, item):
        """Process a single content item (runs in background task)"""
        try:
            logger.info(f"Auto-processing Row {item.id}: {item.topic}")
            
            # Update status to Generating
            await self.sheets_service.update_content_status(
                row_id=item.id,
                status=ContentStatus.GENERATING
            )
            
            # Process the item
            result = await self.workflow_service.process_content_item(
                item,
                skip_approval=False,  # Always require approval
                auto_publish=False     # Don't auto-publish, wait for approval
            )
            
            # Send success notification to Slack
            if self.slack_service.configured:
                try:
                    await self.slack_service.send_notification(
                        f"✅ Content Generated Successfully!\n\n"
                        f"*Row {item.id}: {item.topic}*\n"
                        f"Platform: {item.platform}\n"
                        f"Workflow ID: {result.workflow_id if hasattr(result, 'workflow_id') else 'N/A'}\n\n"
                        f"⏳ Awaiting approval to publish to LinkedIn...",
                        "success"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send success notification: {e}")
            
            logger.info(f"Successfully processed Row {item.id}")
            
        except Exception as e:
            logger.error(f"Failed to process Row {item.id}: {e}")
            
            # Update status to Failed
            try:
                await self.sheets_service.update_content_status(
                    row_id=item.id,
                    status=ContentStatus.FAILED
                )
                await self.sheets_service.log_error(
                    row_id=item.id,
                    error_message=str(e)
                )
            except:
                pass
            
            # Send error notification to Slack
            if self.slack_service.configured:
                try:
                    await self.slack_service.send_notification(
                        f"❌ Processing Failed\n\n"
                        f"*Row {item.id}: {item.topic}*\n"
                        f"Platform: {item.platform}\n"
                        f"Error: {str(e)[:200]}\n\n"
                        f"Check Google Sheets for details.",
                        "error"
                    )
                except:
                    pass
    
    def reset_processed_cache(self):
        """Clear the cache of processed IDs (useful for testing)"""
        self.processed_ids.clear()
        logger.info("Processed items cache cleared")
