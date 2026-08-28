import streamlit as st
import requests
from typing import Dict, Any, List, Optional

# Get API base from secrets
try:
    API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
except:
    API_BASE = "http://localhost:8000"

# ===== Room Functions =====

def create_room(name: str, host_name: str, company: str, position: str, settings: dict = None) -> Dict[str, Any]:
    """Create a new meeting room"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/create",
            json={
                "name": name,
                "host_name": host_name,
                "company": company or "Unknown",
                "position": position or "Guest",
                "settings": settings or {}
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_BASE}")
        raise
    except Exception as e:
        st.error(f"❌ Error creating room: {str(e)}")
        raise

def join_room(meeting_id: str, name: str, company: str, position: str) -> Dict[str, Any]:
    """Join an existing meeting room"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/join/{meeting_id}",
            json={
                "name": name,
                "company": company or "Unknown",
                "position": position or "Guest"
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_BASE}")
        raise
    except Exception as e:
        st.error(f"❌ Error joining room: {str(e)}")
        raise

def get_rooms() -> List[Dict[str, Any]]:
    """Get all rooms"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.warning(f"⚠️ Cannot connect to backend at {API_BASE}")
        return []
    except Exception as e:
        st.warning(f"⚠️ Error fetching rooms: {str(e)}")
        return []

def get_room(meeting_id: str) -> Optional[Dict[str, Any]]:
    """Get room details"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms/{meeting_id}",
            timeout=10
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_BASE}")
        return None
    except Exception as e:
        st.error(f"❌ Error fetching room: {str(e)}")
        return None

def get_participants(meeting_id: str) -> List[Dict[str, Any]]:
    """Get participants in a room"""
    try:
        response = requests.get(
            f"{API_BASE}/api/rooms/{meeting_id}/participants",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.warning(f"⚠️ Cannot connect to backend at {API_BASE}")
        return []
    except Exception as e:
        st.warning(f"⚠️ Error fetching participants: {str(e)}")
        return []

def get_stats() -> Dict[str, Any]:
    """Get server statistics"""
    try:
        response = requests.get(
            f"{API_BASE}/api/stats",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {"total_rooms": 0, "active_rooms": 0, "total_participants": 0}

# ===== Chat Functions =====

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
        return {"id": "mock", "message": message}

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

# ===== Poll Functions =====

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
        return {"id": "mock-poll", "question": question, "options": options}

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

# ===== Recording Functions =====

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

# ===== Breakout Room Functions =====

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
        return {"id": "mock-breakout", "name": name}

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

# ===== Participant Management Functions =====

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
