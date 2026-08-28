import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from .supabase_client import supabase

class Database:
    def __init__(self):
        self.supabase = supabase
        self.use_mock = supabase is None
        
        if self.use_mock:
            print("⚠️ Using mock database (no Supabase connection)")
            self._mock_rooms = []
            self._mock_participants = []
            self._mock_messages = []
    
    def create_room(self, name: str, host_id: str, host_name: str, host_email: str = None) -> dict:
        room_id = str(uuid.uuid4())
        meeting_id = f"{uuid.uuid4().hex[:8].upper()}"
        
        room_data = {
            "id": room_id,
            "name": name,
            "meeting_id": meeting_id,
            "host_id": host_id,
            "host_name": host_name,
            "host_email": host_email,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": False,
            "is_recording": False,
            "start_time": None,
            "end_time": None
        }
        
        if self.use_mock:
            self._mock_rooms.append(room_data)
            return room_data
        
        try:
            result = self.supabase.table("rooms").insert(room_data).execute()
            if result.data:
                return result.data[0]
            return room_data
        except Exception as e:
            print(f"❌ Supabase error (create_room): {e}")
            return room_data
    
    def get_room_by_meeting_id(self, meeting_id: str) -> Optional[dict]:
        if self.use_mock:
            for room in self._mock_rooms:
                if room["meeting_id"] == meeting_id:
                    return room
            return None
        
        try:
            result = self.supabase.table("rooms").select("*").eq("meeting_id", meeting_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Supabase error (get_room_by_meeting_id): {e}")
            return None
    
    def get_room_by_id(self, room_id: str) -> Optional[dict]:
        if self.use_mock:
            for room in self._mock_rooms:
                if room["id"] == room_id:
                    return room
            return None
        
        try:
            result = self.supabase.table("rooms").select("*").eq("id", room_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Supabase error (get_room_by_id): {e}")
            return None
    
    def get_all_rooms(self) -> List[dict]:
        if self.use_mock:
            return self._mock_rooms.copy()
        
        try:
            result = self.supabase.table("rooms").select("*").order("created_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Supabase error (get_all_rooms): {e}")
            return self._mock_rooms
    
    def add_participant(self, room_id: str, name: str, company: str, position: str, role: str, email: str = None) -> dict:
        participant_id = str(uuid.uuid4())
        
        participant_data = {
            "id": participant_id,
            "room_id": room_id,
            "name": name,
            "email": email,
            "company": company,
            "position": position,
            "role": role,
            "joined_at": datetime.utcnow().isoformat(),
            "left_at": None,
            "is_muted": False,
            "is_video_off": True,
            "is_screen_sharing": False,
            "is_hand_raised": False
        }
        
        if self.use_mock:
            self._mock_participants.append(participant_data)
            return participant_data
        
        try:
            result = self.supabase.table("participants").insert(participant_data).execute()
            if result.data:
                return result.data[0]
            return participant_data
        except Exception as e:
            print(f"❌ Supabase error (add_participant): {e}")
            return participant_data
    
    def get_participant(self, participant_id: str) -> Optional[dict]:
        if self.use_mock:
            for p in self._mock_participants:
                if p["id"] == participant_id:
                    return p
            return None
        
        try:
            result = self.supabase.table("participants").select("*").eq("id", participant_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Supabase error (get_participant): {e}")
            return None
    
    def get_participants(self, room_id: str) -> List[dict]:
        if self.use_mock:
            return [p for p in self._mock_participants if p["room_id"] == room_id and p["left_at"] is None]
        
        try:
            result = self.supabase.table("participants").select("*").eq("room_id", room_id).is_("left_at", "null").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Supabase error (get_participants): {e}")
            return []
    
    def remove_participant(self, participant_id: str):
        if self.use_mock:
            for p in self._mock_participants:
                if p["id"] == participant_id:
                    p["left_at"] = datetime.utcnow().isoformat()
            return
        
        try:
            self.supabase.table("participants").update({"left_at": datetime.utcnow().isoformat()}).eq("id", participant_id).execute()
        except Exception as e:
            print(f"❌ Supabase error (remove_participant): {e}")
    
    def save_chat_message(self, room_id: str, participant_id: str, participant_name: str, message: str) -> dict:
        msg_id = str(uuid.uuid4())
        
        msg_data = {
            "id": msg_id,
            "room_id": room_id,
            "participant_id": participant_id,
            "participant_name": participant_name,
            "message": message,
            "created_at": datetime.utcnow().isoformat(),
            "is_private": False,
            "recipient_id": None
        }
        
        if self.use_mock:
            self._mock_messages.append(msg_data)
            return msg_data
        
        try:
            result = self.supabase.table("chat_messages").insert(msg_data).execute()
            if result.data:
                return result.data[0]
            return msg_data
        except Exception as e:
            print(f"❌ Supabase error (save_chat_message): {e}")
            return msg_data
    
    def get_chat_messages(self, room_id: str, limit: int = 50) -> List[dict]:
        if self.use_mock:
            return [m for m in self._mock_messages if m["room_id"] == room_id][-limit:]
        
        try:
            result = self.supabase.table("chat_messages").select("*").eq("room_id", room_id).order("created_at", desc=False).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Supabase error (get_chat_messages): {e}")
            return []
    
    def update_room_status(self, room_id: str, is_active: bool, is_recording: bool = None):
        updates = {"is_active": is_active}
        if is_active:
            updates["start_time"] = datetime.utcnow().isoformat()
        else:
            updates["end_time"] = datetime.utcnow().isoformat()
        
        if is_recording is not None:
            updates["is_recording"] = is_recording
        
        if self.use_mock:
            for room in self._mock_rooms:
                if room["id"] == room_id:
                    room.update(updates)
            return
        
        try:
            self.supabase.table("rooms").update(updates).eq("id", room_id).execute()
        except Exception as e:
            print(f"❌ Supabase error (update_room_status): {e}")
    
    def update_participant(self, participant_id: str, **kwargs):
        if self.use_mock:
            for p in self._mock_participants:
                if p["id"] == participant_id:
                    p.update(kwargs)
            return
        
        try:
            self.supabase.table("participants").update(kwargs).eq("id", participant_id).execute()
        except Exception as e:
            print(f"❌ Supabase error (update_participant): {e}")

db = Database()
