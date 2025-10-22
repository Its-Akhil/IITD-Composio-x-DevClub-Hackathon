#Generate remaining files: database, utilities, scripts, config files

# 17. Database module
database_code = '''"""
Database connection and models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VideoGeneration(Base):
    """Video generation history"""
    __tablename__ = "video_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    prompt = Column(Text)
    video_url = Column(String)
    status = Column(String)
    generation_time = Column(Float)
    num_frames = Column(Integer)
    resolution = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class WorkflowExecution(Base):
    """Workflow execution history"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True)
    content_id = Column(Integer)
    status = Column(String)
    steps_completed = Column(Text)  # JSON string
    errors = Column(Text)  # JSON string
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

# 18. File utilities
file_utils_code = '''"""
File operation utilities
"""
import os
import shutil
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

def ensure_directory(path: str) -> Path:
    """Ensure directory exists"""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def cleanup_old_files(directory: str, max_age_days: int = 7) -> int:
    """Clean up files older than specified days"""
    import time
    
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0
    
    now = time.time()
    cutoff = now - (max_age_days * 86400)
    removed_count = 0
    
    for file_path in dir_path.glob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff:
            try:
                file_path.unlink()
                removed_count += 1
                logger.info(f"Removed old file: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {e}")
    
    return removed_count

def get_file_size(path: str) -> int:
    """Get file size in bytes"""
    return Path(path).stat().st_size

def list_videos(directory: str) -> List[dict]:
    """List all video files in directory"""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    videos = []
    for file_path in dir_path.glob("*.mp4"):
        videos.append({
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "created": file_path.stat().st_ctime
        })
    
    return sorted(videos, key=lambda x: x['created'], reverse=True)
'''

# 19. Validators utility
validators_code = '''"""
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
'''

# 20. Script: Download model
download_script = '''#!/usr/bin/env python3
"""
Download ModelScope text-to-video model
Run this script once before starting the application
"""
import sys
import torch
from pathlib import Path
from diffusers import DiffusionPipeline

def download_model():
    """Download and cache ModelScope model"""
    model_path = Path("./local_t2v_model")
    
    if model_path.exists():
        print(f"✓ Model already exists at {model_path}")
        response = input("Download again? (y/N): ")
        if response.lower() != 'y':
            return
    
    print("Downloading ModelScope text-to-video-ms-1.7b...")
    print("This will take 10-15 minutes and requires ~6GB disk space")
    
    try:
        # Check GPU availability
        if torch.cuda.is_available():
            print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
            dtype = torch.float16
            variant = "fp16"
        else:
            print("⚠ No GPU detected, using CPU (will be slow)")
            dtype = torch.float32
            variant = None
        
        # Download model
        print("\\nDownloading from HuggingFace...")
        pipe = DiffusionPipeline.from_pretrained(
            "damo-vilab/text-to-video-ms-1.7b",
            torch_dtype=dtype,
            variant=variant
        )
        
        # Save locally
        print(f"\\nSaving model to {model_path}...")
        model_path.mkdir(exist_ok=True, parents=True)
        pipe.save_pretrained(str(model_path))
        
        print("\\n✅ Model downloaded and cached successfully!")
        print("\\nYou can now run: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"\\n❌ Error downloading model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()
'''

# 21. Script: Setup database
setup_db_script = '''#!/usr/bin/env python3
"""
Initialize database schema
"""
from app.database import init_db, engine
from sqlalchemy import inspect

def setup_database():
    """Setup database tables"""
    print("Initializing database...")
    
    try:
        init_db()
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\\n✓ Database initialized with {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        print("\\n✅ Database setup complete!")
        
    except Exception as e:
        print(f"\\n❌ Database setup failed: {e}")

if __name__ == "__main__":
    setup_database()
'''

# 22. Script: Test APIs
test_apis_script = '''#!/usr/bin/env python3
"""
Test external API connections
"""
import asyncio
import sys
from app.config import settings
from app.services.llm_service import LLMService
from app.services.sheets_service import SheetsService
from app.services.slack_service import SlackService
from app.services.wordpress_service import WordPressService

async def test_gemini():
    """Test Gemini API"""
    print("\\n🔍 Testing Gemini API...")
    try:
        llm = LLMService()
        if not llm.configured:
            print("  ⚠ Gemini API not configured")
            return False
        
        result = await llm._generate_content("Say 'API working!' in one word")
        print(f"  ✅ Gemini API: {result[:50]}")
        return True
    except Exception as e:
        print(f"  ❌ Gemini API failed: {e}")
        return False

async def test_sheets():
    """Test Google Sheets"""
    print("\\n🔍 Testing Google Sheets API...")
    try:
        sheets = SheetsService()
        if not sheets.configured:
            print("  ⚠ Google Sheets not configured")
            return False
        
        items = await sheets.get_pending_content()
        print(f"  ✅ Google Sheets: Found {len(items)} pending items")
        return True
    except Exception as e:
        print(f"  ❌ Google Sheets failed: {e}")
        return False

async def test_slack():
    """Test Slack webhook"""
    print("\\n🔍 Testing Slack webhook...")
    try:
        slack = SlackService()
        if not slack.configured:
            print("  ⚠ Slack not configured")
            return False
        
        await slack.send_notification("API test message", "info")
        print("  ✅ Slack webhook working")
        return True
    except Exception as e:
        print(f"  ❌ Slack failed: {e}")
        return False

async def test_wordpress():
    """Test WordPress API"""
    print("\\n🔍 Testing WordPress API...")
    try:
        wp = WordPressService()
        if not wp.configured:
            print("  ⚠ WordPress not configured")
            return False
        
        print("  ✅ WordPress API configured")
        return True
    except Exception as e:
        print(f"  ❌ WordPress failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("AI SOCIAL FACTORY - API TEST SUITE")
    print("=" * 60)
    
    results = {
        "Gemini": await test_gemini(),
        "Google Sheets": await test_sheets(),
        "Slack": await test_slack(),
        "WordPress": await test_wordpress()
    }
    
    print("\\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service}")
    
    success_count = sum(results.values())
    total = len(results)
    print(f"\\nPassed: {success_count}/{total}")
    
    if success_count == total:
        print("\\n🎉 All tests passed!")
        return 0
    else:
        print("\\n⚠ Some tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
'''

# Store all remaining files
remaining_files = {
    'app/database.py': database_code,
    'app/utils/file_utils.py': file_utils_code,
    'app/utils/validators.py': validators_code,
    'scripts/download_model.py': download_script,
    'scripts/setup_db.py': setup_db_script,
    'scripts/test_apis.py': test_apis_script
}

print("✓ Database module")
print("✓ File utilities")
print("✓ Validators")
print("✓ Download model script")
print("✓ Setup database script")
print("✓ Test APIs script")
print(f"\nTotal utility files: {len(remaining_files)}")
print("\nGenerating configuration and deployment files...")
