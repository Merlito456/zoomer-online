import requests
import streamlit as st
from typing import Dict, Any

API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

def create_room(name: str, host_name: str, company: str, position: str) -> Dict[str, Any]:
    """Create a new meeting room"""
    response = requests.post(
        f"{API_BASE}/api/rooms/create",
        json={
            "name": name,
            "host_name": host_name,
            "company": company,
            "position": position
        }
    )
    response.raise_for_status()
    return response.json()

def join_room(meeting_id: str, name: str, company: str, position: str) -> Dict[str, Any]:
    """Join an existing meeting room"""
    response = requests.post(
        f"{API_BASE}/api/rooms/join/{meeting_id}",
        json={
            "name": name,
            "company": company,
            "position": position
        }
    )
    response.raise_for_status()
    return response.json()

def get_rooms() -> Dict[str, Any]:
    """Get all rooms"""
    response = requests.get(f"{API_BASE}/api/rooms")
    response.raise_for_status()
    return response.json()

def get_room(meeting_id: str) -> Dict[str, Any]:
    """Get room details"""
    response = requests.get(f"{API_BASE}/api/rooms/{meeting_id}")
    response.raise_for_status()
    return response.json()

def get_participants(meeting_id: str) -> Dict[str, Any]:
    """Get participants in a room"""
    response = requests.get(f"{API_BASE}/api/rooms/{meeting_id}/participants")
    response.raise_for_status()
    return response.json()
