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

from database import SessionLocal, init_db, ChatHistory

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

# Initialize database
init_db()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize model
try:
    logger.info("Loading FLUX model...")
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.float32
    )
    pipe.enable_model_cpu_offload()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error initializing model: {e}")
    raise

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": pipe is not None}

@app.post("/api/generate")
async def generate_image(request: ImageRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Generating image for prompt: {request.prompt}")
        image = pipe(
            request.prompt,
            height=request.height,
            width=request.width,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            max_sequence_length=512,
            generator=torch.Generator("cpu").manual_seed(0)
        ).images[0]
        
        # Save image to disk
        os.makedirs("generated_images", exist_ok=True)
        image_filename = f"generated_images/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(image_filename)
        
        # Store in database
        db_record = ChatHistory(
            prompt=request.prompt,
            image_path=image_filename
        )
        db.add(db_record)
        db.commit()
        
        # Convert to base64 for response
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Cleanup old records
        await ChatHistory.cleanup_old_records(db)
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(db: Session = Depends(get_db)):
    history = db.query(ChatHistory).order_by(ChatHistory.created_at.desc()).all()
    return [{
        "id": record.id,
        "prompt": record.prompt,
        "created_at": record.created_at,
        "image_path": record.image_path
    } for record in history]