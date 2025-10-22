"""
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
