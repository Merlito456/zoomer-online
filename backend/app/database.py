import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from .supabase_client import supabase

class Database:
    def __init__(self):
        pass
    
    def create_room(self, name: str, host_id: str, host_name: str, host_email: str = None) -> dict:
        room_id = str(uuid.uuid4())
        meeting_id = f"{uuid.uuid4().hex[:8].upper()}"
        
        data = {
            "id": room_id,
            "name": name,
            "meeting_id": meeting_id,
            "host_id": host_id,
            "host_name": host_name,
            "host_email": host_email,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": False,
            "is_recording": False
        }
        
        result = supabase.table("rooms").insert(data).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_room_by_meeting_id(self, meeting_id: str) -> Optional[dict]:
        result = supabase.table("rooms").select("*").eq("meeting_id", meeting_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_room_by_id(self, room_id: str) -> Optional[dict]:
        result = supabase.table("rooms").select("*").eq("id", room_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_all_rooms(self) -> List[dict]:
        result = supabase.table("rooms").select("*").order("created_at", desc=True).execute()
        return result.data if result.data else []
    
    def add_participant(self, room_id: str, name: str, company: str, position: str, role: str, email: str = None) -> dict:
        participant_id = str(uuid.uuid4())
        
        data = {
            "id": participant_id,
            "room_id": room_id,
            "name": name,
            "email": email,
            "company": company,
            "position": position,
            "role": role,
            "joined_at": datetime.utcnow().isoformat(),
            "is_muted": False,
            "is_video_off": True,
            "is_screen_sharing": False,
            "is_hand_raised": False
        }
        
        result = supabase.table("participants").insert(data).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_participant(self, participant_id: str) -> Optional[dict]:
        result = supabase.table("participants").select("*").eq("id", participant_id).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_participants(self, room_id: str) -> List[dict]:
        result = supabase.table("participants").select("*").eq("room_id", room_id).is_("left_at", "null").execute()
        return result.data if result.data else []
    
    def remove_participant(self, participant_id: str):
        supabase.table("participants").update({"left_at": datetime.utcnow().isoformat()}).eq("id", participant_id).execute()
    
    def save_chat_message(self, room_id: str, participant_id: str, participant_name: str, message: str) -> dict:
        msg_id = str(uuid.uuid4())
        
        data = {
            "id": msg_id,
            "room_id": room_id,
            "participant_id": participant_id,
            "participant_name": participant_name,
            "message": message,
            "created_at": datetime.utcnow().isoformat(),
            "is_private": False
        }
        
        result = supabase.table("chat_messages").insert(data).execute()
        if result.data:
            return result.data[0]
        return None
    
    def get_chat_messages(self, room_id: str, limit: int = 50) -> List[dict]:
        result = supabase.table("chat_messages").select("*").eq("room_id", room_id).order("created_at", desc=False).limit(limit).execute()
        return result.data if result.data else []
    
    def update_room_status(self, room_id: str, is_active: bool, is_recording: bool = None):
        updates = {"is_active": is_active}
        if is_active:
            updates["start_time"] = datetime.utcnow().isoformat()
        else:
            updates["end_time"] = datetime.utcnow().isoformat()
        
        if is_recording is not None:
            updates["is_recording"] = is_recording
        
        supabase.table("rooms").update(updates).eq("id", room_id).execute()
    
    def update_participant(self, participant_id: str, **kwargs):
        supabase.table("participants").update(kwargs).eq("id", participant_id).execute()

db = Database()
