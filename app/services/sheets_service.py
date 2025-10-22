"""
Google Sheets integration service
"""
import asyncio
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
            # Run blocking gspread call in thread pool to avoid blocking event loop
            records = await asyncio.to_thread(self.worksheet.get_all_records)
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
        caption: Optional[str] = None,
        script: Optional[str] = None,
        workflow_id: Optional[str] = None,
        post_id: Optional[str] = None,
        approved_by: Optional[str] = None
    ):
        """Update content item status and related data"""
        if not self.configured:
            raise SheetsServiceError("Google Sheets not configured")
        
        try:
            # Run all blocking gspread calls in thread pool to avoid blocking event loop
            # Update Status column (column D)
            await asyncio.to_thread(self.worksheet.update_cell, row_id, 4, status.value)
            
            # Update Video_URL if provided (column E)
            if video_url:
                await asyncio.to_thread(self.worksheet.update_cell, row_id, 5, video_url)
            
            # Update Caption if provided (column G)
            if caption:
                # Truncate caption if too long (Google Sheets cell limit is 50,000 chars)
                caption_truncated = caption[:5000] if len(caption) > 5000 else caption
                await asyncio.to_thread(self.worksheet.update_cell, row_id, 7, caption_truncated)
            
            # Update Script if provided (column H)
            if script:
                # Truncate script if too long
                script_truncated = script[:5000] if len(script) > 5000 else script
                await asyncio.to_thread(self.worksheet.update_cell, row_id, 8, script_truncated)
            
            # Update Workflow_ID if provided (column I)
            if workflow_id:
                await asyncio.to_thread(self.worksheet.update_cell, row_id, 9, workflow_id)
            
            # Update Post_ID if provided (column J)
            if post_id:
                await asyncio.to_thread(self.worksheet.update_cell, row_id, 10, post_id)
            
            # Update Approved_By if provided (column K)
            if approved_by:
                await asyncio.to_thread(self.worksheet.update_cell, row_id, 11, approved_by)
            
            # Update Timestamp (column L)
            await asyncio.to_thread(self.worksheet.update_cell, row_id, 12, datetime.now().isoformat())
            
            logger.info(f"Updated row {row_id} status to {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            raise SheetsServiceError(f"Update failed: {str(e)}")
    
    async def log_error(self, row_id: int, error_message: str):
        """Log error for a content item"""
        if not self.configured:
            return
        
        try:
            # Add error to Notes column (column M)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_log = f"[{timestamp}] {error_message}"
            await asyncio.to_thread(self.worksheet.update_cell, row_id, 13, error_log)
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
