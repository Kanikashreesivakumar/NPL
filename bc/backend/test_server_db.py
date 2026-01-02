from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import base64
import io
import os
import sqlite3
from datetime import datetime, timedelta
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
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
CLEANUP_DAYS = int(os.getenv('CLEANUP_DAYS', 30))

print(f"🔧 Configuration:")
print(f"   Database: {DATABASE_URL}")
print(f"   Port: {PORT}")
print(f"   Auto-cleanup after: {CLEANUP_DAYS} days")
if STABILITY_API_KEY:
    print(f"   Stability AI: {STABILITY_API_KEY[:10]}...")
else:
    print("   Using Pollinations API (fallback)")

# Extract database path from URL
DATABASE_PATH = DATABASE_URL.replace('sqlite:///', '').replace('sqlite:', '')
IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

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

def cleanup_old_images():
    """Remove images older than CLEANUP_DAYS"""
    try:
        cutoff_date = datetime.now() - timedelta(days=CLEANUP_DAYS)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get old images
        cursor.execute('''
            SELECT id, filename FROM images 
            WHERE created_at < ?
        ''', (cutoff_date.isoformat(),))
        
        old_images = cursor.fetchall()
        
        if old_images:
            print(f"🧹 Cleaning up {len(old_images)} images older than {CLEANUP_DAYS} days...")
            
            for image_id, filename in old_images:
                # Delete physical file
                filepath = os.path.join(IMAGES_DIR, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"🗑️ Deleted file: {filename}")
                
                # Delete from database
                cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
            
            conn.commit()
            print(f"✅ Cleanup completed! Removed {len(old_images)} old images.")
        else:
            print(f"✅ No images older than {CLEANUP_DAYS} days found.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

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
    print(f"💾 Image saved to gallery with ID: {image_id}")
    return image_id

def get_images_from_db():
    """Get all images from database with expiration info"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, filename, prompt, created_at, file_size, width, height
        FROM images
        ORDER BY created_at DESC
    ''')
    
    images = []
    for row in cursor.fetchall():
        # Calculate days ago and expiration
        created_date = datetime.fromisoformat(row[3])
        days_ago = (datetime.now() - created_date).days
        expires_in = CLEANUP_DAYS - days_ago
        
        images.append({
            "id": str(row[0]),
            "filename": row[1],
            "prompt": row[2],
            "created_at": row[3],
            "file_size": row[4],
            "width": row[5],
            "height": row[6],
            "url": f"/api/images/{row[1]}",
            "days_ago": days_ago,
            "expires_in_days": expires_in
        })
    
    conn.close()
    print(f"📸 Gallery loaded: {len(images)} images")
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
    
    c
def generate_with_stability_ai(prompt: str, width: int, height: int):
    """Generate image using Stability AI API"""
    if not STABILITY_API_KEY:
        raise Exception("Stability AI API key not configured")
    
    url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }
    
    payload = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            }
        ],
        "cfg_scale": 7,
        "height": height,
        "width": width,
        "samples": 1,
        "steps": 30
    }
    
    print(f"🎨 Generating with Stability AI...")
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        error_msg = f"Stability AI API error: {response.status_code} - {response.text}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    data = response.json()
    
    if not data.get("artifacts") or len(data["artifacts"]) == 0:
        raise Exception("No image generated by Stability AI")
    
    image_base64 = data["artifacts"][0]["base64"]
    return base64.b64decode(image_base64)

@app.on_event("startup")
async def startup_event():
    init_database()
    # Auto cleanup on startup
    cleanup_old_images()
    
    # Test database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        count = cursor.fetchone()[0]
        conn.close()
        print(f"📊 Gallery ready! {count} images in database")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

@app.get("/")
def read_root():
    return {
        "message": "AI Image Gallery with Auto-Cleanup",
        "cleanup_days": CLEANUP_DAYS,
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
            "total_images": count,
            "cleanup_days": CLEANUP_DAYS,
            "stability_ai": "configured" if STABILITY_API_KEY else "using_fallback"
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
        
        # Try Stability AI first, fallback to Pollinations
        if STABILITY_API_KEY:
            try:
                image_data = generate_with_stability_ai(request.prompt, request.width, request.height)
                print("✅ Generated with Stability AI")
            except Exception as stability_error:
                print(f"⚠️ Stability AI failed: {stability_error}")
                print("🔄 Falling back to Pollinations API...")
                # Fallback to Pollinations
                api_url = f"https://image.pollinations.ai/prompt/{request.prompt}?width={request.width}&height={request.height}"
                response = requests.get(api_url, timeout=30)
                if response.status_code == 200:
                    image_data = response.content
                    print("✅ Generated with Pollinations (fallback)")
                else:
                    raise Exception("Both Stability AI and Pollinations failed")
        else:
            # Use Pollinations API as primary
            api_url = f"https://image.pollinations.ai/prompt/{request.prompt}?width={request.width}&height={request.height}"
            response = requests.get(api_url, timeout=30)
            
            if response.status_code == 200:
                image_data = response.content
                print("✅ Generated with Pollinations API")
            else:
                raise Exception("Pollinations API failed")
        
        # Save image to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"gallery_{timestamp}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Write image file
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Get file size
        file_size = len(image_data)
        
        # Save to gallery database
        image_id = save_image_to_db(
            filename=filename,
            prompt=request.prompt,
            file_size=file_size,
            width=request.width,
            height=request.height
        )
        
        generation_time = time.time() - start_time
        print(f"⚡ Generated and added to gallery in {generation_time:.2f} seconds!")
        print(f"📁 Will auto-delete after {CLEANUP_DAYS} days")
        
        # Convert to base64 for immediate display
        img_base64 = base64.b64encode(image_data).decode()
        
        return {
            "status": "success",
            "image": img_base64,
            "prompt": request.prompt,
            "image_id": str(image_id),
            "filename": filename,
            "expires_in_days": CLEANUP_DAYS
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gallery")
async def get_gallery():
    """Get all images in gallery with expiration info"""
    try:
        images = get_images_from_db()
        return {
            "images": images,
            "total_count": len(images),
            "cleanup_days": CLEANUP_DAYS
        }
    except Exception as e:
        print(f"Error fetching gallery: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch gallery")

@app.get("/api/history")
async def get_image_history():
    """Get all images from database (alias for gallery)"""
    return await get_gallery()

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    """Serve image files"""
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Image not found")

@app.delete("/api/gallery/{image_id}")
async def delete_from_gallery(image_id: str):
    """Manually delete image from gallery"""
    try:
        success = delete_image_from_db(int(image_id))
        if success:
            return {"status": "success", "message": "Image removed from gallery"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image ID")
    except Exception as e:
        print(f"Error deleting from gallery: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete from gallery")

@app.delete("/api/history/{image_id}")
async def delete_image(image_id: str):
    """Delete image from database and filesystem (alias for gallery delete)"""
    return await delete_from_gallery(image_id)

@app.post("/api/cleanup")
async def manual_cleanup():
    """Manually trigger cleanup of old images"""
    try:
        cleanup_old_images()
        
        # Get updated count
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        remaining_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "success",
            "message": f"Cleanup completed. {remaining_count} images remaining in gallery.",
            "cleanup_days": CLEANUP_DAYS
        }
    except Exception as e:
        print(f"Manual cleanup error: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

@app.get("/api/stats")
async def get_stats():
    """Get gallery statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM images')
    total_images = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(file_size) FROM images')
    total_size = cursor.fetchone()[0] or 0
    
    # Count recent images (last 7 days)
    recent_cutoff = datetime.now() - timedelta(days=7)
    cursor.execute('SELECT COUNT(*) FROM images WHERE created_at > ?', (recent_cutoff.isoformat(),))
    recent_images = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_images": total_images,
        "recent_images_7_days": recent_images,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "cleanup_days": CLEANUP_DAYS,
        "database_path": DATABASE_PATH
    }

if __name__ == "__main__":
    print(f"🚀 Starting AI Image Gallery Server")
    print(f"📁 Images auto-delete after {CLEANUP_DAYS} days")
    print(f"🌐 Server: {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, reload=False)