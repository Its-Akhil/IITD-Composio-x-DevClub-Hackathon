#!/usr/bin/env python3
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
