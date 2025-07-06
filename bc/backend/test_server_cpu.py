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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing images and history
IMAGES_DIR = "generated_images"
HISTORY_FILE = "image_history.json"
os.makedirs(IMAGES_DIR, exist_ok=True)

class GenerateImageRequest(BaseModel):
    prompt: str
    width: int = 512
    height: int = 512
    guidance_scale: float = 7.5
    num_inference_steps: int = 10  # Reduced for faster generation

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
        print("Loading Stable Diffusion model for CPU...")
        from diffusers import StableDiffusionPipeline
        
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        pipe = pipe.to("cpu")
        print("Model loaded successfully on CPU!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/")
def read_root():
    return {"message": "Stable Diffusion API is running on CPU"}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": pipe is not None}

@app.post("/api/generate")
async def generate_image(request: GenerateImageRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        print(f"Generating image for prompt: '{request.prompt}'")
        print(f"Parameters: {request.width}x{request.height}, steps: {request.num_inference_steps}")
        print("⏳ This will take 1-3 minutes on CPU, please wait...")
        
        start_time = time.time()
        
        # Generate image
        image = pipe(
            request.prompt,
            width=request.width,
            height=request.height,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            generator=torch.manual_seed(42)
        ).images[0]
        
        generation_time = time.time() - start_time
        print(f"✅ Image generated in {generation_time:.2f} seconds")
        
        # Save image to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        filename = f"image_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        image.save(filepath)
        print(f"💾 Image saved to {filepath}")
        
        # Save to history
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
        print(f"📝 Added to history: {len(history)} total images")
        
        # Convert to base64 for immediate display
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")

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
        # Delete physical file
        filepath = os.path.join(IMAGES_DIR, image_to_delete["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        save_image_history(history)
        return {"status": "success", "message": "Image deleted"}
    
    raise HTTPException(status_code=404, detail="Image not found")

if __name__ == "__main__":
    uvicorn.run("test_server_cpu:app", host="0.0.0.0", port=8001, reload=False)