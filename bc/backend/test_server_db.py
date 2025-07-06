from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import base64
import io
import os
import sqlite3
from datetime import datetime
from PIL import Image
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration from environment variables
PORT = int(os.getenv('PORT', 8001))
HOST = os.getenv('HOST', '0.0.0.0')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./image_gallery.db')
CLEANUP_DAYS = int(os.getenv('CLEANUP_DAYS', 30))

# Extract database path from URL
DATABASE_PATH = DATABASE_URL.replace('sqlite:///', '').replace('sqlite:', '')
IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

print(f"🔧 Configuration:")
print(f"   Database: {DATABASE_PATH}")
print(f"   Port: {PORT}")
print(f"   Images Directory: {IMAGES_DIR}")

class GenerateImageRequest(BaseModel):
    prompt: str
    width: int = 512
    height: int = 512

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def init_database():
    """Initialize SQLite database for storing image metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            prompt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            width INTEGER,
            height INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DATABASE_PATH}")

def save_image_to_db(filename, prompt, file_size, width, height):
    """Save image metadata to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO images (filename, prompt, file_size, width, height)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, prompt, file_size, width, height))
    
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    print(f"💾 Image saved to database with ID: {image_id}")
    return image_id

def get_images_from_db():
    """Get all images from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, prompt, created_at, file_size, width, height
        FROM images
        ORDER BY created_at DESC
    ''')
    
    images = []
    for row in cursor.fetchall():
        images.append({
            "id": str(row[0]),
            "filename": row[1],
            "prompt": row[2],
            "created_at": row[3],
            "file_size": row[4],
            "width": row[5],
            "height": row[6],
            "url": f"/api/images/{row[1]}"
        })
    
    conn.close()
    print(f"📸 Retrieved {len(images)} images from database")
    return images

def delete_image_from_db(image_id):
    """Delete image from database and file system"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get filename before deleting
    cursor.execute('SELECT filename FROM images WHERE id = ?', (image_id,))
    result = cursor.fetchone()
    
    if result:
        filename = result[0]
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Delete from database
        cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
        conn.commit()
        
        # Delete physical file
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Deleted file: {filepath}")
        
        conn.close()
        print(f"🗑️ Deleted image with ID: {image_id}")
        return True
    
    conn.close()
    return False

@app.on_event("startup")
async def startup_event():
    init_database()
    # Test database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        count = cursor.fetchone()[0]
        conn.close()
        print(f"📊 Database connected successfully! Found {count} existing images.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

@app.get("/")
def read_root():
    return {
        "message": "Image Generator API with SQLite Database",
        "database": DATABASE_PATH,
        "port": PORT
    }

@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        count = cursor.fetchone()[0]
        conn.close()
        return {
            "status": "ok", 
            "database": "connected",
            "database_path": DATABASE_PATH,
            "total_images": count
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/generate")
async def generate_image(request: GenerateImageRequest):
    try:
        print(f"🚀 Generating image: '{request.prompt}'")
        start_time = time.time()
        
        # Using Pollinations API for fast generation
        api_url = f"https://image.pollinations.ai/prompt/{request.prompt}?width={request.width}&height={request.height}"
        
        response = requests.get(api_url, timeout=30)
        
        if response.status_code == 200:
            # Save image to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"image_{timestamp}.png"
            filepath = os.path.join(IMAGES_DIR, filename)
            
            # Write image file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Get file size
            file_size = len(response.content)
            
            # Save to database
            image_id = save_image_to_db(
                filename=filename,
                prompt=request.prompt,
                file_size=file_size,
                width=request.width,
                height=request.height
            )
            
            generation_time = time.time() - start_time
            print(f"⚡ Generated and saved in {generation_time:.2f} seconds!")
            
            # Convert to base64 for immediate display
            img_base64 = base64.b64encode(response.content).decode()
            
            return {
                "status": "success",
                "image": img_base64,
                "prompt": request.prompt,
                "image_id": str(image_id),
                "filename": filename
            }
        else:
            raise HTTPException(status_code=500, detail="Image generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_image_history():
    """Get all images from database"""
    try:
        images = get_images_from_db()
        return {"images": images}
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch image history")

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    """Serve image files"""
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Image not found")

@app.delete("/api/history/{image_id}")
async def delete_image(image_id: str):
    """Delete image from database and filesystem"""
    try:
        success = delete_image_from_db(int(image_id))
        if success:
            return {"status": "success", "message": "Image deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image ID")
    except Exception as e:
        print(f"Error deleting image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")

@app.get("/api/stats")
async def get_stats():
    """Get gallery statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM images')
    total_images = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(file_size) FROM images')
    total_size = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_images": total_images,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "database_path": DATABASE_PATH
    }

if __name__ == "__main__":
    print(f"🚀 Starting server on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, reload=False)