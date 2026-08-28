from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ParticipantRole(str, Enum):
    HOST = "host"
    PARTICIPANT = "participant"

class Participant(BaseModel):
    id: str
    room_id: str
    name: str
    email: Optional[str] = None
    company: str
    position: str
    role: ParticipantRole
    joined_at: datetime
    left_at: Optional[datetime] = None
    is_muted: bool = False
    is_video_off: bool = True
    is_screen_sharing: bool = False
    is_hand_raised: bool = False

class Room(BaseModel):
    id: str
    name: str
    meeting_id: str
    host_id: str
    host_name: str
    created_at: datetime
    is_active: bool = False
    is_recording: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    participants: List[Participant] = []

class ChatMessage(BaseModel):
    id: str
    room_id: str
    participant_id: str
    participant_name: str
    message: str
    created_at: datetime
    is_private: bool = False
    recipient_id: Optional[str] = None
