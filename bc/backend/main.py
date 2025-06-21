from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from diffusers import FluxPipeline
from io import BytesIO
import base64
from PIL import Image

app = FastAPI()

cd # Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test_endpoint():
    return {
        "status": "Backend is running!",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available()
    }

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev", 
    torch_dtype=torch.bfloat16
)
pipe.enable_model_cpu_offload()

class ImageRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    guidance_scale: float = 3.5
    num_inference_steps: int = 50

@app.post("/api/generate")
async def generate_image(request: ImageRequest):
    try:
        
        image = pipe(
            request.prompt,
            height=request.height,
            width=request.width,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            max_sequence_length=512,
            generator=torch.Generator("cpu").manual_seed(0)
        ).images[0]
    
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "status": "success",
            "image": img_str,
            "prompt": request.prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)