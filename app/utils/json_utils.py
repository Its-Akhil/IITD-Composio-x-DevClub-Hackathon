"""
JSON utilities for handling LLM responses
"""
import json
import re
import logging

logger = logging.getLogger(__name__)


def clean_json_response(text: str) -> str:
    """
    Clean and fix common issues in JSON responses from LLMs
    
    Args:
        text: Raw text that should contain JSON
        
    Returns:
        Cleaned JSON string ready for parsing
    """
    if not text:
        return "{}"
    
    text = text.strip()
    
    # Remove markdown code blocks
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        text = text.strip()
    
    # Extract JSON object or array if surrounded by other text
    json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if json_match:
        text = json_match.group(1)
    
    return text


def parse_llm_json(text: str, max_retries: int = 3) -> dict:
    """
    Parse JSON from LLM response with multiple fallback strategies
    
    Args:
        text: Raw response text
        max_retries: Number of fix attempts
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        json.JSONDecodeError: If all parsing attempts fail
    """
    original_text = text
    text = clean_json_response(text)
    
    # Attempt 1: Direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parse failed: {e}")
    
    # Attempt 2: Fix unescaped newlines within strings
    try:
        # This is tricky - we need to escape newlines inside string values
        # but not structural newlines in the JSON
        fixed_text = fix_json_newlines(text)
        return json.loads(fixed_text)
    except json.JSONDecodeError as e:
        logger.debug(f"Newline fix parse failed: {e}")
    
    # Attempt 3: Fix unescaped quotes
    try:
        fixed_text = fix_json_quotes(text)
        return json.loads(fixed_text)
    except json.JSONDecodeError as e:
        logger.debug(f"Quote fix parse failed: {e}")
    
    # Attempt 4: Try to fix common formatting issues
    try:
        fixed_text = fix_common_json_issues(text)
        return json.loads(fixed_text)
    except json.JSONDecodeError as e:
        logger.error(f"All JSON parsing attempts failed. Original text: {original_text[:500]}")
        raise


def fix_json_newlines(text: str) -> str:
    """
    Fix unescaped newlines in JSON strings
    """
    # Replace unescaped newlines with escaped ones
    # This is a simple approach - more sophisticated parsing might be needed
    result = []
    in_string = False
    escape_next = False
    
    for i, char in enumerate(text):
        if escape_next:
            result.append(char)
            escape_next = False
            continue
            
        if char == '\\':
            result.append(char)
            escape_next = True
            continue
            
        if char == '"':
            in_string = not in_string
            result.append(char)
            continue
            
        if char == '\n' and in_string:
            result.append('\\n')
        elif char == '\r' and in_string:
            result.append('\\r')
        elif char == '\t' and in_string:
            result.append('\\t')
        else:
            result.append(char)
    
    return ''.join(result)


def fix_json_quotes(text: str) -> str:
    """
    Attempt to fix unescaped quotes in JSON strings
    """
    # This is a simplified approach
    # Replace smart quotes with regular quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text


def fix_common_json_issues(text: str) -> str:
    """
    Fix various common JSON formatting issues
    """
    # Remove trailing commas before closing brackets/braces
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    # Fix missing commas between array elements
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)
    
    # Fix missing commas between object properties
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)
    
    return text


def safe_json_parse(text: str, default: dict = None) -> dict:
    """
    Safely parse JSON with a default fallback
    
    Args:
        text: Text to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed dictionary or default
    """
    if default is None:
        default = {}
    
    try:
        return parse_llm_json(text)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse JSON, using default: {e}")
        return default
