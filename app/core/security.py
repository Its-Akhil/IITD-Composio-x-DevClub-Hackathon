"""
Security utilities for API authentication
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings
import logging

logger = logging.getLogger(__name__)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    logger.info(f"Received API key: '{api_key}'")
    logger.info(f"Expected API key: '{settings.API_KEY}'")
    logger.info(f"Keys match: {api_key == settings.API_KEY}")
    logger.info(f"Received type: {type(api_key)}, Expected type: {type(settings.API_KEY)}")
    
    if api_key and api_key == settings.API_KEY:
        return api_key
    
    logger.warning(f"Invalid API key attempt. Received: '{api_key}', Expected: '{settings.API_KEY}'")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )
