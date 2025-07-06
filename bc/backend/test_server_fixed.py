from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import base64
import io
from PIL import Image
import torch

# Check if CUDA is available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

app = FastAPI()

class GenerateImageRequest(BaseModel):
    prompt: str
    width: int = 512
    height: int = 512
    guidance_scale: float = 7.5
    num_inference_steps: int = 50

# Global variable to store the pipeline
pipe = None

def load_model():
    global pipe
    try:
        print("Loading Stable Diffusion model...")
        from diffusers import StableDiffusionPipeline
        
        # Load the pipeline
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        pipe = pipe.to(device)
        
        # Enable memory efficient attention if using CUDA
        if device == "cuda":
            pipe.enable_attention_slicing()
            pipe.enable_xformers_memory_efficient_attention()
        
        print("Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    success = load_model()
    if not success:
        print("Failed to load model on startup")

@app.get("/")
def read_root():
    return {"message": "Stable Diffusion API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": pipe is not None}

@app.post("/api/generate")
async def generate_image(request: GenerateImageRequest):
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        print(f"Generating image for prompt: {request.prompt}")
        
        # Generate image
        with torch.autocast(device):
            image = pipe(
                request.prompt,
                width=request.width,
                height=request.height,
                guidance_scale=request.guidance_scale,
                num_inference_steps=request.num_inference_steps
            ).images[0]
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
        
    except Exception as e:
        print(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("test_server_fixed:app", host="0.0.0.0", port=8000, reload=False)