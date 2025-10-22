"""
LinkedIn API integration service
"""
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from app.config import settings
from app.core.exceptions import LinkedInServiceError

logger = logging.getLogger(__name__)

class LinkedInService:
    """LinkedIn API service for posting content"""
    
    def __init__(self):
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.person_urn = settings.LINKEDIN_PERSON_URN
        self.organization_urn = settings.LINKEDIN_ORGANIZATION_URN
        self.configured = bool(self.access_token and self.person_urn)
        
        if self.configured:
            logger.info("LinkedIn service initialized")
        else:
            logger.warning("LinkedIn not configured - missing access token or person URN")
    
    async def _register_video_upload(self, author_urn: str) -> tuple[Optional[str], Optional[str]]:
        """Register video upload with LinkedIn and get upload URL"""
        try:
            url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            
            payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": author_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Video registration failed: {response.status} - {error_text}")
                        return None, None
                    
                    data = await response.json()
                    video_urn = data["value"]["asset"]
                    upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                    
                    logger.info(f"Video registered successfully. URN: {video_urn}")
                    return video_urn, upload_url
                    
        except Exception as e:
            logger.error(f"Failed to register video upload: {e}")
            return None, None
    
    async def _upload_video_binary(self, upload_url: str, video_data: bytes) -> bool:
        """Upload video binary data to LinkedIn"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/octet-stream"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    upload_url, 
                    data=video_data, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for video upload
                ) as response:
                    if response.status == 201:
                        logger.info("Video uploaded successfully to LinkedIn")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Video upload failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to upload video binary: {e}")
            return False
    
    async def _download_video(self, video_url: str) -> Optional[bytes]:
        """Download video from URL"""
        try:
            logger.info(f"Downloading video from: {video_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        video_data = await response.read()
                        logger.info(f"Video downloaded successfully. Size: {len(video_data)} bytes")
                        return video_data
                    else:
                        logger.error(f"Failed to download video: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return None

    async def create_post(
        self,
        text: str,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        use_organization: bool = False
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn post
        
        Args:
            text: Post content text
            image_url: Optional image URL
            video_url: Optional video URL (will be downloaded and uploaded to LinkedIn)
            use_organization: Post as organization instead of person
            
        Returns:
            Dict with post details including post_id and post_url
        """
        if not self.configured:
            raise LinkedInServiceError("LinkedIn not configured")
        
        try:
            # Determine author URN
            author_urn = self.organization_urn if use_organization and self.organization_urn else self.person_urn
            
            video_urn = None
            
            # Handle video upload if video_url provided
            if video_url:
                logger.info("Starting LinkedIn video upload process...")
                
                # Step 1: Register video upload
                video_urn, upload_url = await self._register_video_upload(author_urn)
                
                if video_urn and upload_url:
                    # Step 2: Download video from our server
                    video_data = await self._download_video(video_url)
                    
                    if video_data:
                        # Step 3: Upload video to LinkedIn
                        upload_success = await self._upload_video_binary(upload_url, video_data)
                        
                        if not upload_success:
                            logger.warning("Video upload failed, posting as text-only")
                            video_urn = None
                    else:
                        logger.warning("Video download failed, posting as text-only")
                        video_urn = None
                else:
                    logger.warning("Video registration failed, posting as text-only")
                    video_urn = None
            
            # Build the post payload
            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add media if provided
            if image_url:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "originalUrl": image_url
                    }
                ]
            elif video_urn:
                # Use uploaded video URN
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "VIDEO"
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "media": video_urn
                    }
                ]
                logger.info(f"Including video in post: {video_urn}")
            
            # Make API request using aiohttp (async)
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            logger.info(f"LinkedIn API Request - Author URN: {author_urn}")
            logger.info(f"LinkedIn API Request - Payload: {payload}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    # Log response details before raising for status
                    response_text = await response.text()
                    logger.info(f"LinkedIn API Response Status: {response.status}")
                    logger.info(f"LinkedIn API Response Body: {response_text}")
                    
                    if response.status != 201 and response.status != 200:
                        logger.error(f"LinkedIn API error response: {response_text}")
                        raise LinkedInServiceError(
                            f"LinkedIn API returned {response.status}: {response_text}"
                        )
                    
                    # Extract post ID from response
                    post_data = await response.json() if not response_text else eval(response_text)
                    post_id = post_data.get("id", "")
                    
                    # Construct post URL (approximate)
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}"
                    
                    logger.info(f"LinkedIn post created: {post_id}")
                    
                    return {
                        "post_id": post_id,
                        "post_url": post_url,
                        "platform": "linkedin",
                        "status": "published"
                    }
            
        except aiohttp.ClientError as e:
            logger.error(f"LinkedIn API error: {e}")
            raise LinkedInServiceError(f"Failed to create LinkedIn post: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating LinkedIn post: {e}")
            raise LinkedInServiceError(f"Unexpected error: {str(e)}")
    
    async def create_text_post(self, text: str) -> Dict[str, Any]:
        """Create a simple text-only LinkedIn post"""
        return await self.create_post(text=text)
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a LinkedIn post (placeholder)"""
        if not self.configured:
            raise LinkedInServiceError("LinkedIn not configured")
        
        # This would require additional LinkedIn API permissions
        logger.warning("LinkedIn analytics not yet implemented")
        return {
            "post_id": post_id,
            "impressions": 0,
            "clicks": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        }
