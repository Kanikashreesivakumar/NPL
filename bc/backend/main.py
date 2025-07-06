from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import base64
import os
from dotenv import load_dotenv
from typing import Optional
from fastapi.responses import FileResponse
from datetime import datetime
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Stability AI Image Generator")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGES_DIR = "generated_images"
HISTORY_FILE = "image_history.json"

# Create directories if they don't exist
os.makedirs(IMAGES_DIR, exist_ok=True)

def load_image_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_image_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)

class ImageRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    cfg_scale: float = 7.0
    steps: int = 30
    samples: int = 1

class ImageResponse(BaseModel):
    status: str
    image: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Stability AI Image Generator API", "status": "running"}

@app.get("/health")
async def health_check():
    api_key = os.getenv("STABILITY_API_KEY")
    return {
        "status": "healthy", 
        "service": "Stability AI Backend",
        "api_key_configured": bool(api_key and api_key.startswith("sk-"))
    }

@app.post("/api/generate", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    try:
        # Get API key from environment
        api_key = os.getenv("STABILITY_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Stability AI API key not configured")
        
        # Stability AI API endpoint
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        data = {
            "text_prompts": [{"text": request.prompt}],
            "cfg_scale": request.cfg_scale,
            "height": request.height,
            "width": request.width,
            "steps": request.steps,
            "samples": request.samples,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_detail = f"Stability AI API error: {response.status_code} - {response.text}"
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            response_data = response.json()
            
            # Extract the base64 image
            if "artifacts" in response_data and len(response_data["artifacts"]) > 0:
                image_base64 = response_data["artifacts"][0]["base64"]
                
                # Save image to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}.png"
                filepath = os.path.join(IMAGES_DIR, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
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
                
                # Return base64 for immediate display
                encoded_image = base64.b64encode(response.content).decode('utf-8')
                return {"status": "success", "image": encoded_image}
            else:
                raise HTTPException(status_code=500, detail="No image generated")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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