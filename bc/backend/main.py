from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
from typing import Optional

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
                return ImageResponse(status="success", image=image_base64)
            else:
                raise HTTPException(status_code=500, detail="No image generated")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)