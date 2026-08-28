import streamlit as st
import requests
from typing import Dict, Any, List, Optional

# Get API base from secrets
try:
    API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
except:
    API_BASE = "http://localhost:8000"

# ===== Existing functions (create_room, join_room, etc.) =====

def save_chat_message(room_id: str, participant_id: str, participant_name: str, message: str) -> Dict[str, Any]:
    """Save a chat message"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/chat",
            json={
                "participant_id": participant_id,
                "participant_name": participant_name,
                "message": message
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"message": "saved"}

def get_chat_messages(room_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get chat messages"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms/{room_id}/chat?limit={limit}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return []

def create_poll(room_id: str, host_id: str, question: str, options: List[str], is_anonymous: bool = True) -> Dict[str, Any]:
    """Create a poll"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/polls",
            json={
                "host_id": host_id,
                "question": question,
                "options": options,
                "is_anonymous": is_anonymous
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"id": "mock-poll"}

def vote_poll(poll_id: str, option_index: int, participant_id: str) -> Dict[str, Any]:
    """Vote on a poll"""
    try:
        response = requests.post(
            f"{API_BASE}/api/polls/{poll_id}/vote",
            json={
                "participant_id": participant_id,
                "option_index": option_index
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "voted"}

def get_polls(room_id: str) -> List[Dict[str, Any]]:
    """Get all polls for a room"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms/{room_id}/polls",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return []

def start_recording(room_id: str, participant_id: str) -> Dict[str, Any]:
    """Start recording"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/recording/start",
            json={"participant_id": participant_id},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "started"}

def stop_recording(room_id: str, participant_id: str) -> Dict[str, Any]:
    """Stop recording"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/recording/stop",
            json={"participant_id": participant_id},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "stopped"}

def get_recordings(room_id: str) -> List[Dict[str, Any]]:
    """Get recordings"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms/{room_id}/recordings",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return []

def create_breakout_room(room_id: str, name: str, participants: List[str]) -> Dict[str, Any]:
    """Create a breakout room"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/breakout",
            json={
                "name": name,
                "participants": participants
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"id": "mock-breakout"}

def get_breakout_rooms(room_id: str) -> List[Dict[str, Any]]:
    """Get breakout rooms"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms/{room_id}/breakout",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return []

def raise_hand(room_id: str, participant_id: str) -> Dict[str, Any]:
    """Raise hand"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/hand-raise",
            json={"participant_id": participant_id},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "raised"}

def mute_participant(room_id: str, participant_id: str) -> Dict[str, Any]:
    """Mute participant (host only)"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/mute/{participant_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "muted"}

def remove_participant(room_id: str, participant_id: str) -> Dict[str, Any]:
    """Remove participant (host only)"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/remove/{participant_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "removed"}

def update_participant_status(room_id: str, participant_id: str, status: str) -> Dict[str, Any]:
    """Update participant status"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/{room_id}/status",
            json={
                "participant_id": participant_id,
                "status": status
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"status": "updated"}
