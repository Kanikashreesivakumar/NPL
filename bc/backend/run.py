import uvicorn
import logging
from huggingface_hub import HfFolder, login
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_backend():
    # Load environment variables
    load_dotenv()
    
    # Check authentication
    token = HfFolder.get_token()
    if not token and os.getenv("HUGGINGFACE_TOKEN"):
        # Try to login with token from .env file
        login(os.getenv("HUGGINGFACE_TOKEN"))
        token = HfFolder.get_token()
    
    if not token:
        logger.error("Not logged in to Hugging Face. Please run 'huggingface-cli login' or set HUGGINGFACE_TOKEN in .env")
        raise ValueError("Hugging Face authentication required")
    
    logger.info("Hugging Face authentication successful")

if __name__ == "__main__":
    try:
        setup_backend()
        logger.info("Starting FastAPI server...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise