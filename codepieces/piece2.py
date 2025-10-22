# Continue generating remaining service files

# 5. LLM Service (Gemini API)
llm_service = '''"""
LLM service using Google Gemini API
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.config import settings
from app.models import ScriptGenerationRequest, ScriptGenerationResponse, ScriptVariant
from app.models import CaptionRequest, CaptionResponse
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

class LLMService:
    """Google Gemini API service"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured")
            self.configured = False
            return
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.configured = True
        logger.info(f"LLMService initialized with model: {settings.GEMINI_MODEL}")
    
    async def analyze_trend(self, topic: str) -> Dict[str, Any]:
        """Analyze trending topic and provide insights"""
        if not self.configured:
            raise LLMServiceError("Gemini API not configured")
        
        prompt = f"""Analyze the following topic and provide insights for creating engaging social media content:

Topic: {topic}

Provide:
1. Current trends related to this topic
2. Key angles to explore
3. Target audience interests
4. Recommended content style
5. Hashtag suggestions

Format as JSON."""
        
        try:
            response = await self._generate_content(prompt)
            # Parse JSON response
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise LLMServiceError(f"Trend analysis failed: {str(e)}")
    
    async def generate_scripts(
        self,
        request: ScriptGenerationRequest
    ) -> ScriptGenerationResponse:
        """Generate multiple script variants"""
        if not self.configured:
            raise LLMServiceError("Gemini API not configured")
        
        prompt = f"""Generate {request.num_variants} engaging video script variants for social media.

Topic: {request.topic}
Platform: {request.platform}
Target Duration: {request.target_duration} seconds

Requirements:
- Each script should be unique and creative
- Hook viewers in first 2 seconds
- Clear call-to-action
- Platform-appropriate tone
- Suitable for {request.target_duration} second video

Output as JSON array with structure:
[{{"variant_id": "A", "script": "...", "style": "...", "duration_estimate": 10}}]
"""
        
        try:
            response = await self._generate_content(prompt)
            import json
            variants_data = json.loads(response)
            
            variants = [
                ScriptVariant(
                    variant_id=v["variant_id"],
                    script=v["script"],
                    style=v.get("style", "general"),
                    duration_estimate=v.get("duration_estimate", request.target_duration)
                )
                for v in variants_data
            ]
            
            return ScriptGenerationResponse(
                topic=request.topic,
                variants=variants,
                metadata={"platform": request.platform}
            )
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise LLMServiceError(f"Script generation failed: {str(e)}")
    
    async def generate_caption(
        self,
        request: CaptionRequest
    ) -> CaptionResponse:
        """Generate platform-specific caption with hashtags"""
        if not self.configured:
            raise LLMServiceError("Gemini API not configured")
        
        platform_guidelines = {
            "instagram": "Engaging, visual-focused, 2-3 lines, 5-10 hashtags",
            "youtube": "Detailed, SEO-optimized, clear description, 3-5 hashtags",
            "tiktok": "Short, trendy, relatable, 3-5 trending hashtags",
            "linkedin": "Professional, value-driven, thought leadership, 2-3 hashtags",
            "twitter": "Concise, punchy, under 280 chars, 1-2 hashtags"
        }
        
        guideline = platform_guidelines.get(request.platform, "General engaging caption")
        max_length_info = f"Max length: {request.max_length} chars" if request.max_length else ""
        
        prompt = f"""Create an engaging caption for {request.platform}.

Video Script: {request.script}
Style: {guideline}
{max_length_info}
Include Hashtags: {request.include_hashtags}

Output as JSON:
{{"caption": "...", "hashtags": ["tag1", "tag2", ...]}}
"""
        
        try:
            response = await self._generate_content(prompt)
            import json
            data = json.loads(response)
            
            caption = data["caption"]
            hashtags = data.get("hashtags", []) if request.include_hashtags else []
            
            return CaptionResponse(
                caption=caption,
                hashtags=hashtags,
                platform=request.platform,
                character_count=len(caption)
            )
            
        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            raise LLMServiceError(f"Caption generation failed: {str(e)}")
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_sync,
                prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise LLMServiceError(f"API call failed: {str(e)}")
    
    def _generate_sync(self, prompt: str):
        """Synchronous generation (runs in thread pool)"""
        generation_config = {
            "temperature": settings.GEMINI_TEMPERATURE,
            "max_output_tokens": settings.GEMINI_MAX_TOKENS,
        }
        return self.model.generate_content(prompt, generation_config=generation_config)
'''

# 6. Google Sheets Service
sheets_service = '''"""
Google Sheets integration service
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from app.config import settings
from app.models import ContentItem, ContentStatus
from app.core.exceptions import SheetsServiceError

logger = logging.getLogger(__name__)

class SheetsService:
    """Google Sheets API service"""
    
    def __init__(self):
        self.client = None
        self.worksheet = None
        self.configured = False
        
        try:
            self._initialize()
        except Exception as e:
            logger.warning(f"Google Sheets not configured: {e}")
    
    def _initialize(self):
        """Initialize Google Sheets client"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
            scopes=scopes
        )
        
        self.client = gspread.authorize(creds)
        spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
        self.worksheet = spreadsheet.worksheet(settings.GOOGLE_SHEETS_SHEET_NAME)
        self.configured = True
        logger.info("Google Sheets service initialized")
    
    async def get_pending_content(self) -> List[ContentItem]:
        """Get all pending content items"""
        if not self.configured:
            raise SheetsServiceError("Google Sheets not configured")
        
        try:
            records = self.worksheet.get_all_records()
            pending_items = []
            
            for idx, record in enumerate(records, start=2):  # Start at row 2 (after header)
                if record.get('Status') == 'Pending':
                    item = ContentItem(
                        id=idx,
                        date=datetime.strptime(record['Date'], '%Y-%m-%d'),
                        topic=record['Topic'],
                        video_prompt=record['Video_Prompt'],
                        status=ContentStatus.PENDING,
                        platform=record.get('Platform', 'general')
                    )
                    pending_items.append(item)
            
            logger.info(f"Found {len(pending_items)} pending content items")
            return pending_items
            
        except Exception as e:
            logger.error(f"Failed to fetch pending content: {e}")
            raise SheetsServiceError(f"Fetch failed: {str(e)}")
    
    async def update_content_status(
        self,
        row_id: int,
        status: ContentStatus,
        video_url: Optional[str] = None,
        post_id: Optional[str] = None
    ):
        """Update content item status"""
        if not self.configured:
            raise SheetsServiceError("Google Sheets not configured")
        
        try:
            # Update Status column (column D)
            self.worksheet.update_cell(row_id, 4, status.value)
            
            # Update Video_URL if provided (column E)
            if video_url:
                self.worksheet.update_cell(row_id, 5, video_url)
            
            # Update Post_ID if provided (column H)
            if post_id:
                self.worksheet.update_cell(row_id, 8, post_id)
            
            # Update Timestamp (column I)
            self.worksheet.update_cell(row_id, 9, datetime.now().isoformat())
            
            logger.info(f"Updated row {row_id} status to {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            raise SheetsServiceError(f"Update failed: {str(e)}")
    
    async def log_error(self, row_id: int, error_message: str):
        """Log error for a content item"""
        if not self.configured:
            return
        
        try:
            # Add error to a Notes column (assuming column J)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_log = f"[{timestamp}] {error_message}"
            self.worksheet.update_cell(row_id, 10, error_log)
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
'''

# 7. Slack Service
slack_service = '''"""
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
        video_url: str,
        caption: str,
        content_id: int
    ) -> bool:
        """Send approval request to Slack channel"""
        if not self.configured:
            raise SlackServiceError("Slack not configured")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎬 New Video Ready for Approval"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Topic:*\\n{topic}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Content ID:*\\n{content_id}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Caption:*\\n{caption}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Video:* {video_url}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve"
                        },
                        "style": "primary",
                        "value": f"approve_{content_id}",
                        "action_id": "approve_video"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": f"reject_{content_id}",
                        "action_id": "reject_video"
                    }
                ]
            }
        ]
        
        payload = {
            "channel": self.channel,
            "text": f"New video ready: {topic}",
            "blocks": blocks
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Approval request sent for content {content_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Slack webhook failed: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            raise SlackServiceError(f"Send failed: {str(e)}")
    
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
'''

# Store all generated files
all_files = {
    'app/services/llm_service.py': llm_service,
    'app/services/sheets_service.py': sheets_service,
    'app/services/slack_service.py': slack_service
}

print(f"✓ Generated {len(all_files)} additional service files")
print("\nServices completed:")
print("  - LLM Service (Gemini API)")
print("  - Google Sheets Service")
print("  - Slack Service")
print("\nContinuing with WordPress, Workflow, and API routes...")
