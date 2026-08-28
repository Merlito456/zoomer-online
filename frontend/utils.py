import streamlit as st
import requests
from typing import Dict, Any, List, Optional

# Get API base from secrets or use default
try:
    API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
except:
    API_BASE = "http://localhost:8000"

def create_room(name: str, host_name: str, company: str, position: str) -> Dict[str, Any]:
    """Create a new meeting room"""
    try:
        response = requests.post(
            f"{API_BASE}/api/rooms/create",
            json={
                "name": name,
                "host_name": host_name,
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
