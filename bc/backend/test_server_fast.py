from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import base64
import io
import os
import json
from datetime import datetime
from PIL import Image
import torch
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGES_DIR = "generated_images"
HISTORY_FILE = "image_history.json"
os.makedirs(IMAGES_DIR, exist_ok=True)

class GenerateImageRequest(BaseModel):
    prompt: str
    width: int = 256  # Much smaller for speed
    height: int = 256
    guidance_scale: float = 5.0  # Lower for speed
    num_inference_steps: int = 4  # Very low for speed

pipe = None

def load_image_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_image_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)

def load_model():
    global pipe
    try:
        print("Loading FAST Stable Diffusion model...")
        from diffusers import StableDiffusionPipeline, LCMScheduler
        
        # Use a much smaller/faster model
        pipe = StableDiffusionPipeline.from_pretrained(
            "SimianLuo/LCM_Dreamshaper_v7",  # Much faster model
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        # Use LCM scheduler for ultra-fast generation
        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
        pipe = pipe.to("cpu")
        
        print("Fast model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading fast model: {e}")
        # Fallback to original model with ultra-fast settings
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            pipe = pipe.to("cpu")
            print("Fallback model loaded!")
            return True
        except Exception as e2:
            print(f"Error loading fallback model: {e2}")
            return False

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/")
def read_root():
    return {"message": "FAST Stable Diffusion API"}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": pipe is not None}

@app.post("/api/generate")
async def generate_image(request: GenerateImageRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        print(f"🚀 FAST generating: '{request.prompt}'")
        start_time = time.time()
        
        # Ultra-fast generation with minimal steps
        image = pipe(
            request.prompt,
            width=request.width,
            height=request.height,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,  # Very few steps
            generator=torch.manual_seed(42)
        ).images[0]
        
        generation_time = time.time() - start_time
        print(f"⚡ Generated in {generation_time:.2f} seconds!")
        
        # Save logic (same as before)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"image_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        image.save(filepath)
        
        history = load_image_history()
        image_record = {
            "id": timestamp,
            "filename": filename,
            "prompt": request.prompt,
            "created_at": datetime.now().isoformat(),
            "url": f"/api/images/{filename}"
        }
        history.append(image_record)
        save_image_history(history)
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_image_history():
    history = load_image_history()
    return {"images": history}

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Image not found")

@app.delete("/api/history/{image_id}")
async def delete_image(image_id: str):
    history = load_image_history()
    image_to_delete = None
    
    for i, img in enumerate(history):
        if img["id"] == image_id:
            image_to_delete = history.pop(i)
            break
    
    if image_to_delete:
        filepath = os.path.join(IMAGES_DIR, image_to_delete["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
        save_image_history(history)
        return {"status": "success", "message": "Image deleted"}
    
    raise HTTPException(status_code=404, detail="Image not found")

if __name__ == "__main__":
    uvicorn.run("test_server_fast:app", host="0.0.0.0", port=8001, reload=False)