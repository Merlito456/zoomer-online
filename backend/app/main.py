from fastapi import APIRouter, HTTPException, Request
from typing import List
import uuid
import os
from datetime import datetime

from .database import db
from .models import ParticipantRole
from .livekit_service import LiveKitService

router = APIRouter()
livekit = LiveKitService()

@router.post("/api/rooms/create")
async def create_room(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "Meeting")
        host_name = data.get("host_name", "Host")
        host_email = data.get("host_email")
        host_id = str(uuid.uuid4())
        
        room = db.create_room(name, host_id, host_name, host_email)
        
        if not room:
            raise HTTPException(status_code=500, detail="Failed to create room")
        
        # Add host as participant
        db.add_participant(
            room_id=room["id"],
            name=host_name,
            company=data.get("company", ""),
            position=data.get("position", ""),
            role=ParticipantRole.HOST,
            email=host_email
        )
        
        # Generate token for host
        token = livekit.generate_token(
            room_name=room["meeting_id"],
            identity=host_id,
            name=host_name,
            metadata={"role": "host", "email": host_email or ""}
        )
        
        return {
            "room": room,
            "token": token,
            "participant_id": host_id,
            "livekit_url": os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        }
    except Exception as e:
        print(f"Error creating room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ... rest of your routes
