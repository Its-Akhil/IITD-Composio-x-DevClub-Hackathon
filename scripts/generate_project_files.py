"""
Script to generate all project files from code pieces
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(r"c:\Users\Nikhil Gupta\Desktop\Learn + Practice\ai-social-factory")

def create_file(relative_path, content):
    """Create a file with given content"""
    file_path = BASE_DIR / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {relative_path}")

# Core utilities - must be created first
create_file('app/core/__init__.py', '"""Core utilities"""\n')

create_file('app/core/exceptions.py', '''"""
Custom exception classes
"""

class AIFactoryException(Exception):
    """Base exception for AI Social Factory"""
    pass

class VideoGenerationError(AIFactoryException):
    """Video generation failed"""
    pass

class LLMServiceError(AIFactoryException):
    """LLM service error"""
    pass

class SheetsServiceError(AIFactoryException):
    """Google Sheets service error"""
    pass

class SlackServiceError(AIFactoryException):
    """Slack service error"""
    pass

class WordPressServiceError(AIFactoryException):
    """WordPress service error"""
    pass

class WorkflowError(AIFactoryException):
    """Workflow execution error"""
    pass
''')

create_file('app/core/logging.py', '''"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    logger.info("Logging configured")
''')

create_file('app/core/security.py', '''"""
Security utilities for API authentication
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )
''')

print("✅ Core utilities created successfully!")
print("Run this script to generate remaining files")
