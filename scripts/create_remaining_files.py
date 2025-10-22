"""
Complete project file generator - Reads from code pieces and creates all files
Run this script to generate all remaining project files
"""

import os
import sys
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
print(f"Base directory: {BASE_DIR}")

# File contents extracted from code pieces
FILES_TO_CREATE = {
    # Google Sheets Service
    'app/services/sheets_service.py': '''"""
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
''',

    # Slack Service
    'app/services/slack_service.py': '''"""
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
''',
}

def create_file(relative_path, content):
    """Create a file with given content"""
    file_path = BASE_DIR / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {relative_path}")

# Create all files
for file_path, content in FILES_TO_CREATE.items():
    create_file(file_path, content)

print(f"\n✅ Successfully created {len(FILES_TO_CREATE)} files!")
print("Project structure is being built...")
