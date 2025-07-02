from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from diffusers import FluxPipeline
from io import BytesIO
import base64
from PIL import Image
import logging
from sqlalchemy.orm import Session
from datetime import datetime
import os
from dotenv import load_dotenv

from database_setup import get_db, init_db
from database_operations import create_chat_record, get_chat_history, cleanup_old_records

logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    guidance_scale: float = 3.5
    num_inference_steps: int = 50

# Load environment variables
load_dotenv()
token = os.getenv("HUGGINGFACE_TOKEN")

# Initialize model
try:
    logger.info("Loading FLUX model...")
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.float32,
        use_auth_token=token  # Add authentication token
    )
    pipe.enable_model_cpu_offload()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error initializing model: {e}")
    raise

# Initialize database
init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": pipe is not None}

@app.post("/api/generate")
async def generate_image(request: ImageRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Generating image for prompt: {request.prompt}")
        # Generate image
        image = pipe(
            request.prompt,
            height=request.height,
            width=request.width,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps
        ).images[0]
        
        # Save image to disk
        os.makedirs("generated_images", exist_ok=True)
        image_filename = f"generated_images/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(image_filename)
        
        # Save to database
        await create_chat_record(db, request.prompt, image_filename)
        
        # Convert to base64 for response
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    try:
        history = await get_chat_history(db, skip, limit)
        return history
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))