import uvicorn
import logging
from huggingface_hub import HfFolder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_auth():
    token = HfFolder.get_token()
    if not token:
        logger.error("Not logged in to Hugging Face. Please run 'huggingface-cli login'")
        raise ValueError("Hugging Face authentication required")
    logger.info("Hugging Face authentication successful")

if __name__ == "__main__":
    check_auth()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)