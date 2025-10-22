"""
WordPress REST API integration service
"""
import logging
import base64
import aiohttp
from typing import Optional, Dict, Any
from app.config import settings
from app.core.exceptions import WordPressServiceError
from app.utils.logging_utils import sanitize_for_logging, truncate_html_error

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
        video_url: str = None,
        caption: str = None,
        categories: Optional[list] = None,
        tags: Optional[list] = None,
        status: str = "publish"
    ) -> Dict[str, Any]:
        """Create a new WordPress post"""
        if not self.configured:
            logger.warning("WordPress not configured, skipping post creation")
            raise WordPressServiceError("WordPress not configured")
        
        # Embed video in content if provided
        if video_url:
            video_embed = f"""
            <video controls width="100%">
                <source src="{video_url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            """
            full_content = video_embed + "\n" + content
        else:
            full_content = content
        
        if caption:
            full_content = f"<p>{caption}</p>\n" + full_content
        
        endpoint = f"{self.site_url}/wp-json/wp/v2/posts"
        
        payload = {
            "title": title,
            "content": full_content,
            "status": status,
            "categories": categories or [1],
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
                        # Sanitize error for logging
                        safe_error = truncate_html_error(error_text, max_length=300)
                        logger.error(f"WordPress API error: {safe_error}")
                        raise WordPressServiceError(f"Post creation failed: {safe_error}")
        except Exception as e:
            # Sanitize exception message
            safe_msg = truncate_html_error(str(e), max_length=300)
            logger.error(f"Failed to create WordPress post: {safe_msg}")
            raise WordPressServiceError(f"Post creation failed: {safe_msg}")
    
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
    
    async def update_post_status(self, post_id: str, status: str) -> Dict[str, Any]:
        """Update WordPress post status (draft → publish or vice versa)"""
        if not self.configured:
            logger.warning("WordPress not configured, skipping status update")
            raise WordPressServiceError("WordPress not configured")
        
        endpoint = f"{self.site_url}/wp-json/wp/v2/posts/{post_id}"
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        
        payload = {"status": status}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Post {post_id} status updated to: {status}")
                        return {
                            "post_id": post_id,
                            "status": status,
                            "post_url": data.get('link')
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"WordPress status update error: {error_text}")
                        raise WordPressServiceError(f"Status update failed: {error_text}")
        except Exception as e:
            logger.error(f"Failed to update post status: {e}")
            raise WordPressServiceError(f"Status update failed: {str(e)}")
