from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from diffusers import StableDiffusionPipeline
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
    height: int = 512
    width: int = 512
    guidance_scale: float = 7.5
    num_inference_steps: int = 50

# Load environment variables
load_dotenv()

# Initialize Stable Diffusion model
try:
    logger.info("Loading Stable Diffusion model...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe.enable_model_cpu_offload()
    logger.info("Stable Diffusion model loaded successfully")
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
        
        # Generate image with Stable Diffusion
        image = pipe(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            generator=torch.Generator().manual_seed(42)
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
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        history = await get_chat_history(db, skip, limit)
        return [
            {
                "id": record.id,
                "prompt": record.prompt,
                "created_at": record.created_at.isoformat(),
                "image_path": record.image_path
            }
            for record in history
        ]
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)