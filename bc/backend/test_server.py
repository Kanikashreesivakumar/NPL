from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from diffusers import StableDiffusionPipeline  # Changed from FluxPipeline
from io import BytesIO
import base64
from PIL import Image


class ImageRequest(BaseModel):
    prompt: str
    height: int = 512  # Changed to 512 for Stable Diffusion
    width: int = 512
    guidance_scale: float = 7.5  # Changed guidance scale
    num_inference_steps: int = 50

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model with Stable Diffusion
try:
    print("Loading Stable Diffusion model...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe.enable_model_cpu_offload()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

@app.get("/test")
async def test_endpoint():
    return {
        "status": "Backend is running!",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available()
    }

@app.post("/api/generate")
async def generate_image(request: ImageRequest):
    try:
        print(f"Generating image for prompt: {request.prompt}")
        
        # Generate image with Stable Diffusion
        image = pipe(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            generator=torch.Generator().manual_seed(42)
        ).images[0]
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
    except Exception as e:
        print(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)