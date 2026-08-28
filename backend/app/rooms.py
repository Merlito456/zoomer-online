from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .rooms import router as rooms_router
from .database import db

load_dotenv()

# This MUST be named "app"
app = FastAPI(
    title="Zoom Clone API",
    description="Backend API for Zoom Clone",
    version="1.0.0"
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,https://your-streamlit-app.streamlit.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - THIS IS CRITICAL
app.include_router(rooms_router)

@app.get("/")
async def root():
    return {
        "message": "Zoom Clone API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/stats")
async def get_stats():
    rooms = db.get_all_rooms()
    active_rooms = [r for r in rooms if r.get("is_active")]
    
    return {
        "total_rooms": len(rooms),
        "active_rooms": len(active_rooms),
        "total_participants": sum(len(db.get_participants(r["id"])) for r in active_rooms)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
