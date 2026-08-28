from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Import the router from rooms.py
from .rooms import router as rooms_router
from .database import db

# Load environment variables
load_dotenv()

# Create the FastAPI app - this MUST be named "app"
app = FastAPI(
    title="Zoom Clone API",
    description="Backend API for Zoom Clone",
    version="1.0.0"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,https://your-streamlit-app.streamlit.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router - this registers all /api/rooms routes
app.include_router(rooms_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Zoom Clone API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    try:
        rooms = db.get_all_rooms()
        return {
            "status": "healthy",
            "rooms_count": len(rooms),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Stats endpoint
@app.get("/api/stats")
async def get_stats():
    rooms = db.get_all_rooms()
    active_rooms = [r for r in rooms if r.get("is_active")]
    
    return {
        "total_rooms": len(rooms),
        "active_rooms": len(active_rooms),
        "total_participants": sum(len(db.get_participants(r["id"])) for r in active_rooms)
    }

# Test endpoint
@app.get("/api/test")
async def test():
    """Test endpoint to verify everything is working"""
    return {
        "status": "success",
        "message": "API is working!",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "livekit_url": os.getenv("LIVEKIT_URL", "not set")
    }

# For running locally
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
