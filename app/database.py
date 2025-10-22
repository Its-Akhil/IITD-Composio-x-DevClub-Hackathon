"""
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
