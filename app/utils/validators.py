"""
Input validation utilities
"""
import re
from typing import Optional

def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+[A-Z]{2,6}\\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})'  # ...or ip
        r'(?::\\d+)?'  # optional port
        r'(?:/?|[/?]\\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    return len(api_key) >= 16 and api_key.isprintable()
