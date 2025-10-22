"""
Slack integration service for approval workflows
"""
import logging
import aiohttp
from typing import Dict, Any
from app.config import settings
from app.core.exceptions import SlackServiceError

logger = logging.getLogger(__name__)

class SlackService:
    """Slack webhook service"""
    
    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        self.channel = settings.SLACK_CHANNEL
        self.configured = bool(self.webhook_url)
        
        if self.configured:
            logger.info("Slack service initialized")
        else:
            logger.warning("Slack webhook URL not configured")
    
    async def send_approval_request(
        self,
        topic: str,
        video_url: str = None,
        caption: str = "",
        content_id: int = None,
        workflow_id: str = None,
        post_id: str = None,
        platform: str = "wordpress",
        script: str = None,
        approval_url: str = None,
        message: str = None
    ) -> Dict[str, Any]:
        """Send approval request to Slack channel with interactive buttons"""
        if not self.configured:
            logger.warning("Slack not configured, skipping approval request")
            return {}
        
        # Use custom message if provided, otherwise build default
        if message:
            message_text = message
        else:
            # Use provided approval_url or build one
            if not approval_url:
                from urllib.parse import urlencode
                approval_params = {
                    'workflow_id': workflow_id or '',
                    'content_id': str(content_id) if content_id else '',
                    'platform': platform or 'wordpress'
                }
                if post_id:
                    approval_params['post_id'] = str(post_id)
                
                approval_url = f"http://localhost:8000/frontend/approve.html?{urlencode(approval_params)}"
            
            # Truncate caption and script for display
            caption_preview = caption[:150] + "..." if len(caption) > 150 else caption
            script_preview = script[:200] + "..." if script and len(script) > 200 else (script or "")
            
            message_text = (
                f"🎬 *New Content Ready for Approval*\n\n"
                f"*Topic:* {topic}\n"
                f"*Platform:* {platform.upper()}\n"
                f"*Content ID (Row):* {content_id}\n"
                f"*Workflow ID:* `{workflow_id}`\n\n"
                f"*Caption:*\n{caption_preview}\n\n"
            )
            
            if script_preview:
                message_text += f"*Script:*\n{script_preview}\n\n"
            
            if video_url:
                message_text += f"*Video:* {video_url}\n\n"
            
            # Add the approval link - prominently displayed
            message_text += (
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ *CLICK TO APPROVE:*\n"
                f"{approval_url}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💾 *All content saved to Google Sheets!*\n"
                f"_Click the link above - all fields are pre-filled!_"
            )
        
        payload = {
            "channel": self.channel,
            "text": message_text,
            "mrkdwn": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        # Slack webhooks return "ok" as text, not JSON
                        response_text = await response.text()
                        logger.info(f"Approval request sent for workflow {workflow_id}: {response_text}")
                        return {"status": "sent", "response": response_text}
                    else:
                        error_text = await response.text()
                        logger.error(f"Slack webhook failed (status {response.status}): {error_text[:200]}")
                        return {}
        except Exception as e:
            logger.error(f"Failed to send Slack approval request: {e}")
            return {}
    
    async def send_notification(self, message: str, level: str = "info"):
        """Send simple notification"""
        if not self.configured:
            return
        
        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "🚨"
        }
        
        payload = {
            "channel": self.channel,
            "text": f"{emoji_map.get(level, 'ℹ️')} {message}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json=payload)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
