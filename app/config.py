"""
Configuration management using Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Social Factory"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    API_KEY: str = "change-this-in-production"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5678"]
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_MAX_TOKENS: int = 2048
    GEMINI_TEMPERATURE: float = 0.9
    
    # Video Generation
    VIDEO_MODEL_PATH: str = "./local_t2v_model"
    VIDEO_OUTPUT_DIR: str = "./generated_videos"
    VIDEO_NUM_FRAMES: int = 16
    VIDEO_HEIGHT: int = 256
    VIDEO_WIDTH: int = 256
    USE_GPU: bool = True
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = "./credentials.json"
    GOOGLE_SHEETS_SPREADSHEET_ID: str = ""
    GOOGLE_SHEETS_SHEET_NAME: str = "Content_Calendar"
    
    # Slack
    SLACK_WEBHOOK_URL: str = ""
    SLACK_BOT_TOKEN: str = ""
    SLACK_APP_TOKEN: str = ""
    SLACK_CHANNEL: str = "#content-review"
    
    # WordPress
    WORDPRESS_SITE_URL: str = ""
    WORDPRESS_USERNAME: str = ""
    WORDPRESS_APP_PASSWORD: str = ""
    
    # LinkedIn
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_PERSON_URN: str = ""  # Your LinkedIn user ID
    LINKEDIN_ORGANIZATION_URN: str = ""  # Optional: for company pages
    
    # Auto-processing
    SHEETS_POLLING_INTERVAL: int = 60  # Check Google Sheets every 60 seconds
    AUTO_PROCESS_ENABLED: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./ai_social_factory.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Workflow
    MAX_CONCURRENT_VIDEOS: int = 3
    VIDEO_GENERATION_TIMEOUT: int = 180  # seconds
    APPROVAL_TIMEOUT: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
