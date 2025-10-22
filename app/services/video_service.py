"""
Video generation service using ModelScope text-to-video model
"""
import torch
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import asyncio
from functools import lru_cache

from diffusers import DiffusionPipeline
from app.config import settings
from app.models import VideoRequest, VideoResponse
from app.core.exceptions import VideoGenerationError

logger = logging.getLogger(__name__)

class VideoService:
    """Video generation service"""
    
    def __init__(self):
        self.pipe = None
        self.model_loaded = False
        self.gpu_available = torch.cuda.is_available()
        self.device = "cuda" if self.gpu_available and settings.USE_GPU else "cpu"
        self.output_dir = Path(settings.VIDEO_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"VideoService initialized - Device: {self.device}")
    
    async def load_model(self):
        """Load ModelScope text-to-video model"""
        try:
            logger.info("Loading ModelScope text-to-video model...")
            
            model_path = Path(settings.VIDEO_MODEL_PATH)
            
            if model_path.exists():
                logger.info(f"Loading model from {model_path}")
                self.pipe = DiffusionPipeline.from_pretrained(
                    str(model_path),
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            else:
                logger.info("Downloading model from HuggingFace...")
                self.pipe = DiffusionPipeline.from_pretrained(
                    "damo-vilab/text-to-video-ms-1.7b",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    variant="fp16" if self.device == "cuda" else None
                )
                # Cache for future use
                logger.info(f"Saving model to {model_path}")
                model_path.mkdir(exist_ok=True, parents=True)
                self.pipe.save_pretrained(str(model_path))
            
            self.pipe.to(self.device)
            self.model_loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise VideoGenerationError(f"Model loading failed: {str(e)}")
    
    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """Generate video from text prompt"""
        if not self.model_loaded:
            logger.info("Model not loaded, loading now...")
            await self.load_model()
        
        start_time = datetime.now()
        video_id = str(uuid.uuid4())
        output_path = self.output_dir / f"{video_id}.mp4"
        
        try:
            logger.info(f"Generating video: {video_id}")
            logger.info(f"Prompt: {request.prompt}")
            
            # Run generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._generate_video_sync,
                request.prompt,
                request.num_frames,
                request.height,
                request.width,
                request.negative_prompt
            )
            
            # Save video - handle different output formats
            await self._save_video(result, output_path)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Video generated in {generation_time:.2f}s: {video_id}")
            
            return VideoResponse(
                video_id=video_id,
                video_url=f"/videos/{video_id}.mp4",
                status="success",
                prompt=request.prompt,
                num_frames=request.num_frames,
                resolution=f"{request.width}x{request.height}",
                generation_time=generation_time,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise VideoGenerationError(f"Generation failed: {str(e)}")
    
    async def _save_video(self, result, output_path: Path):
        """Save video frames to file"""
        import imageio
        import numpy as np
        
        # Extract frames from result
        if hasattr(result, 'frames'):
            frames = result.frames[0]  # Get first video from batch
        elif isinstance(result, dict) and 'frames' in result:
            frames = result['frames'][0]
        else:
            # Assume result is the frames tensor directly
            frames = result[0]
        
        # Convert tensor to numpy array if needed
        if hasattr(frames, 'cpu'):
            frames = frames.cpu().numpy()
        
        # Ensure correct shape and type
        if frames.dtype != np.uint8:
            frames = (frames * 255).astype(np.uint8)
        
        # Save as video using imageio
        imageio.mimsave(str(output_path), frames, fps=8)
        logger.info(f"Video saved to {output_path}")
    
    def _generate_video_sync(
        self,
        prompt: str,
        num_frames: int,
        height: int,
        width: int,
        negative_prompt: Optional[str] = None
    ):
        """Synchronous video generation (runs in thread pool)"""
        return self.pipe(
            prompt,
            num_frames=num_frames,
            height=height,
            width=width,
            negative_prompt=negative_prompt,
            num_inference_steps=25
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up VideoService...")
        if self.pipe:
            del self.pipe
            if self.device == "cuda":
                torch.cuda.empty_cache()
        self.model_loaded = False
