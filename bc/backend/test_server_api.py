from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import base64
import time
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use a free API service for ultra-fast generation
@app.post("/api/generate")
async def generate_image(request: dict):
    try:
        print(f"🚀 Ultra-fast API generation: '{request['prompt']}'")
        start_time = time.time()
        
        # Using Pollinations API (free and fast)
        api_url = f"https://image.pollinations.ai/prompt/{request['prompt']}"
        
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            # Convert to base64
            img_base64 = base64.b64encode(response.content).decode()
            
            generation_time = time.time() - start_time
            print(f"⚡ Generated in {generation_time:.2f} seconds!")
            
            return {
                "status": "success",
                "image": img_base64,
                "prompt": request['prompt']
            }
        else:
            raise HTTPException(status_code=500, detail="API generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": True}

if __name__ == "__main__":
    uvicorn.run("test_server_api:app", host="0.0.0.0", port=8001, reload=False)