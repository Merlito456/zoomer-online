from fastapi import APIRouter, HTTPException, Request
from typing import List
import uuid
import os
from datetime import datetime
import traceback

from .database import db
from .models import ParticipantRole
from .livekit_service import LiveKitService

router = APIRouter()
livekit = LiveKitService()

@router.post("/api/rooms/create")
async def create_room(request: Request):
    try:
        data = await request.json()
        print(f"📥 Creating room with data: {data}")
        
        name = data.get("name", "Meeting")
        host_name = data.get("host_name", "Host")
        host_email = data.get("host_email")
        host_id = str(uuid.uuid4())
        
        room = db.create_room(name, host_id, host_name, host_email)
        
        if not room:
            print("❌ Room creation failed")
            raise HTTPException(status_code=500, detail="Failed to create room")
        
        print(f"✅ Room created: {room['meeting_id']}")
        
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
        print(f"❌ Error creating room: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/rooms/join/{meeting_id}")
async def join_room(request: Request, meeting_id: str):
    try:
        data = await request.json()
        
        room = db.get_room_by_meeting_id(meeting_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Check if room is active or start it
        if not room["is_active"]:
            db.update_room_status(room["id"], True)
        
        # Add participant
        participant = db.add_participant(
            room_id=room["id"],
            name=data["name"],
            company=data.get("company", ""),
            position=data.get("position", ""),
            role=ParticipantRole.PARTICIPANT,
            email=data.get("email")
        )
        
        # Generate token
        token = livekit.generate_token(
            room_name=meeting_id,
            identity=participant["id"],
            name=data["name"],
            metadata={
                "role": "participant",
                "company": data.get("company", ""),
                "position": data.get("position", "")
            }
        )
        
        return {
            "room": room,
            "token": token,
            "participant_id": participant["id"],
            "livekit_url": os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        }
        
    except Exception as e:
        print(f"❌ Error joining room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/rooms")
async def get_rooms():
    try:
        return db.get_all_rooms()
    except Exception as e:
        print(f"❌ Error getting rooms: {str(e)}")
        return []

@router.get("/api/rooms/{meeting_id}")
async def get_room(meeting_id: str):
    try:
        room = db.get_room_by_meeting_id(meeting_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        participants = db.get_participants(room["id"])
        room["participants"] = participants
        return room
    except Exception as e:
        print(f"❌ Error getting room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/rooms/{meeting_id}/participants")
async def get_participants(meeting_id: str):
    try:
        room = db.get_room_by_meeting_id(meeting_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return db.get_participants(room["id"])
    except Exception as e:
        print(f"❌ Error getting participants: {str(e)}")
        return []
