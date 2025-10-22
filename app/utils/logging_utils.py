"""
Logging utilities for safe error message handling
"""
import re


def sanitize_for_logging(message: str, max_length: int = 500) -> str:
    """
    Sanitize error messages for safe logging on Windows
    
    Args:
        message: The message to sanitize
        max_length: Maximum length of the message
        
    Returns:
        Sanitized message safe for logging
    """
    if not isinstance(message, str):
        message = str(message)
    
    # Truncate long messages
    if len(message) > max_length:
        message = message[:max_length] + "... (truncated)"
    
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u2192': '->',  # Right arrow
        '\u2190': '<-',  # Left arrow
        '\u2194': '<->',  # Left-right arrow
        '\u2022': '*',   # Bullet point
        '\u2013': '-',   # En dash
        '\u2014': '--',  # Em dash
        '\u2018': "'",   # Left single quote
        '\u2019': "'",   # Right single quote
        '\u201c': '"',   # Left double quote
        '\u201d': '"',   # Right double quote
        '\u2026': '...',  # Ellipsis
    }
    
    for unicode_char, ascii_char in replacements.items():
        message = message.replace(unicode_char, ascii_char)
    
    # Remove any remaining non-ASCII characters
    # Use 'replace' error handling to substitute with '?'
    try:
        message = message.encode('ascii', errors='replace').decode('ascii')
    except Exception:
        # If encoding fails, strip all non-ASCII
        message = re.sub(r'[^\x00-\x7F]+', '?', message)
    
    return message


def truncate_html_error(html_content: str, max_length: int = 200) -> str:
    """
    Truncate HTML error messages to show just the relevant part
    
    Args:
        html_content: HTML content from error response
        max_length: Maximum length to keep
        
    Returns:
        Truncated and sanitized error message
    """
    if not html_content or not isinstance(html_content, str):
        return str(html_content)
    
    # If it's HTML, try to extract title or first meaningful text
    if html_content.strip().startswith('<!DOCTYPE') or html_content.strip().startswith('<html'):
        # Try to extract title
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            error_msg = f"HTML Error Page: {title_match.group(1).strip()}"
        else:
            error_msg = "HTML Error Page (details in logs)"
        
        return sanitize_for_logging(error_msg, max_length)
    
    # For non-HTML, just sanitize and truncate
    return sanitize_for_logging(html_content, max_length)
