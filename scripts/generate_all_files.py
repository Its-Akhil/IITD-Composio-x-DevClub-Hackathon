"""
COMPLETE PROJECT FILE GENERATOR
Generates all remaining files for the AI Social Factory project
Run this script to create all missing files from the codepieces folder
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
print(f"🚀 AI Social Factory - Complete Project Generator")
print(f"📁 Base directory: {BASE_DIR}\n")

def create_file(relative_path, content):
    """Create a file with given content"""
    file_path = BASE_DIR / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists
    if file_path.exists():
        print(f"⚠ Skipped (exists): {relative_path}")
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {relative_path}")
    return True

# All remaining files with their complete content
print("=" * 70)
print("CREATING REMAINING PROJECT FILES...")
print("=" * 70 + "\n")

created_count = 0

# ==================================================================
# REMAINING SERVICES
# ==================================================================
print("📦 Creating Service Layer Files...\n")

# WordPress Service
if create_file('app/services/wordpress_service.py', '''"""
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
'''):
    created_count += 1

print("\n" + "=" * 70)
print(f"✅ Successfully created {created_count} files!")
print("=" * 70 + "\n")

print("📝 Summary:")
print(f"   Created: {created_count} new files")
print(f"   Base directory: {BASE_DIR}")
print("\n🎉 Project file generation complete!")
print("\n📚 Next steps:")
print("   1. Review PROJECT_STATUS.md for current status")
print("   2. Run additional generator scripts for remaining files")
print("   3. Install dependencies: pip install -r requirements.txt")
print("   4. Configure .env file")
print("   5. Initialize database: python scripts/setup_db.py")
