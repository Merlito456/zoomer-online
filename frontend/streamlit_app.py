import streamlit as st
import time
import json
import os
from utils import create_room, join_room, get_rooms, get_room, get_participants

# Page configuration
st.set_page_config(
    page_title="Zoom Clone Pro",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #0066FF, #0052CC);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .main-header h1 { font-size: 3rem; margin: 0; }
        .main-header p { font-size: 1.2rem; opacity: 0.9; margin: 0.5rem 0 0; }
        .room-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border-left: 4px solid #0066FF;
        }
        .room-card h3 { margin: 0 0 0.5rem 0; color: #1A1A2E; }
        .room-card .meeting-id {
            font-family: monospace;
            background: #f0f2f5;
            padding: 0.2rem 0.8rem;
            border-radius: 4px;
            display: inline-block;
            margin: 0.5rem 0;
        }
        .room-card .status {
            display: inline-block;
            padding: 0.2rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .room-card .status.active { background: #e8f5e9; color: #2e7d32; }
        .room-card .status.inactive { background: #f5f5f5; color: #757575; }
        .stButton > button { width: 100%; border-radius: 8px; font-weight: 500; }
        .participant-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .status-badge {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-badge.online { background: #4CAF50; }
        .status-badge.offline { background: #f44336; }
        .host-badge {
            background: #FFD700;
            color: #1A1A2E;
            padding: 0.2rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }
        .participant-badge {
            background: #E8ECF1;
            color: #1A1A2E;
            padding: 0.2rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }
        .video-container {
            background: #1A1A2E;
            border-radius: 12px;
            padding: 1rem;
            min-height: 300px;
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
            align-items: center;
        }
        .video-participant {
            background: #2A2A3A;
            border-radius: 8px;
            min-width: 200px;
            min-height: 150px;
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            position: relative;
        }
        .video-participant video {
            width: 100%;
            border-radius: 8px;
        }
        .video-participant .participant-name {
            position: absolute;
            bottom: 8px;
            left: 8px;
            background: rgba(0,0,0,0.7);
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        .video-participant .avatar {
            font-size: 3rem;
            font-weight: 600;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'participant_id' not in st.session_state:
    st.session_state.participant_id = None
if 'room_data' not in st.session_state:
    st.session_state.room_data = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'is_host' not in st.session_state:
    st.session_state.is_host = False
if 'livekit_connected' not in st.session_state:
    st.session_state.livekit_connected = False
if 'participants' not in st.session_state:
    st.session_state.participants = []

# Header
st.markdown("""
    <div class="main-header">
        <h1>🎥 Zoom Clone Pro</h1>
        <p>Professional Video Conferencing Platform</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Navigation")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()
    
    if st.button("➕ New Meeting", use_container_width=True):
        st.session_state.page = 'create'
        st.rerun()
    
    if st.button("🔗 Join Meeting", use_container_width=True):
        st.session_state.page = 'join'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
        **Zoom Clone Pro** is a self-hosted video conferencing platform.
        
        Features:
        - HD Video/Audio
        - Screen Sharing
        - Chat
        - Recording
        - Up to 100 participants
    """)
    
    st.markdown("---")
    st.markdown("### 🖥️ Status")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Server**")
        st.markdown('<span class="status-badge online"></span> Online', unsafe_allow_html=True)
    with col2:
        st.markdown("**LiveKit**")
        st.markdown('<span class="status-badge online"></span> Connected', unsafe_allow_html=True)

# Main content
if st.session_state.page == 'dashboard':
    st.markdown("## 📊 Your Meetings")
    
    try:
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"""
                            <div class="room-card">
                                <h3>📹 {room['name']}</h3>
                                <div class="meeting-id">ID: {room['meeting_id']}</div>
                                <div>
                                    <span class="status {'active' if room['is_active'] else 'inactive'}">
                                        {'🟢 Active' if room['is_active'] else '⚪ Inactive'}
                                    </span>
                                    <span style="margin-left: 1rem; color: #666; font-size: 0.9rem;">
                                        👤 Host: {room['host_name']}
                                    </span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        if st.button(f"Join {room['meeting_id'][:4]}", key=f"join_{room['id']}"):
                            st.session_state.room_data = room
                            st.session_state.is_host = False
                            st.session_state.page = 'join_room'
                            st.rerun()
        else:
            st.info("No meetings created yet. Create a new meeting to get started!")
    except Exception as e:
        st.error(f"Failed to load rooms: {str(e)}")

elif st.session_state.page == 'create':
    st.markdown("## ➕ Create New Meeting")
    
    with st.form("create_meeting_form"):
        col1, col2 = st.columns(2)
        with col1:
            meeting_name = st.text_input("Meeting Name", placeholder="e.g., Team Standup")
            host_name = st.text_input("Your Full Name", placeholder="e.g., John Doe")
        with col2:
            company = st.text_input("Company", placeholder="Your company name")
            position = st.text_input("Position", placeholder="Your position")
        
        submit = st.form_submit_button("🚀 Create Meeting", use_container_width=True)
        
        if submit:
            if not meeting_name or not host_name:
                st.error("Please fill in all required fields.")
            else:
                try:
                    with st.spinner("Creating meeting..."):
                        result = create_room(meeting_name, host_name, company, position)
                        st.session_state.room_data = result['room']
                        st.session_state.token = result['token']
                        st.session_state.participant_id = result['participant_id']
                        st.session_state.is_host = True
                        st.session_state.page = 'meeting'
                        st.success("Meeting created successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to create meeting: {str(e)}")

elif st.session_state.page == 'join':
    st.markdown("## 🔗 Join Meeting")
    meeting_id = st.text_input("Meeting ID", placeholder="e.g., A1B2C3D4", max_chars=8).upper()
    
    if st.button("Check Meeting", use_container_width=True):
        if meeting_id:
            try:
                room = get_room(meeting_id)
                if room:
                    st.session_state.room_data = room
                    st.session_state.is_host = False
                    st.session_state.page = 'join_room'
                    st.rerun()
                else:
                    st.error("Meeting not found.")
            except Exception as e:
                st.error(f"Failed to find meeting: {str(e)}")

elif st.session_state.page == 'join_room':
    room = st.session_state.room_data
    
    st.markdown(f"## 🔗 Join Meeting: {room['name']}")
    
    st.markdown(f"""
        <div class="room-card">
            <h3>📹 {room['name']}</h3>
            <div class="meeting-id">ID: {room['meeting_id']}</div>
            <div>
                <span class="status {'active' if room['is_active'] else 'inactive'}">
                    {'🟢 Active' if room['is_active'] else '⚪ Inactive'}
                </span>
                <span style="margin-left: 1rem; color: #666; font-size: 0.9rem;">
                    👤 Host: {room['host_name']}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not room['is_active']:
        st.warning("⏳ This meeting hasn't started yet.")
    
    st.markdown("### Enter your details to join")
    
    with st.form("join_meeting_form"):
        col1, col2 = st.columns(2)
        with col1:
            participant_name = st.text_input("Full Name", placeholder="e.g., Jane Smith")
            participant_company = st.text_input("Company", placeholder="Your company")
        with col2:
            participant_position = st.text_input("Position", placeholder="Your position")
        
        submit = st.form_submit_button("🎥 Join Meeting", use_container_width=True)
        
        if submit:
            if not participant_name:
                st.error("Please enter your name.")
            else:
                try:
                    with st.spinner("Joining meeting..."):
                        result = join_room(
                            room['meeting_id'],
                            participant_name,
                            participant_company,
                            participant_position
                        )
                        st.session_state.token = result['token']
                        st.session_state.participant_id = result['participant_id']
                        st.session_state.is_host = False
                        st.session_state.page = 'meeting'
                        st.success("Connected successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to join meeting: {str(e)}")

elif st.session_state.page == 'meeting':
    if not st.session_state.room_data:
        st.error("No meeting data found.")
        if st.button("Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    else:
        room = st.session_state.room_data
        is_host = st.session_state.is_host
        
        role_badge = '<span class="host-badge">👑 Host</span>' if is_host else '<span class="participant-badge">👤 Participant</span>'
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2>🎥 {room['name']} {role_badge}</h2>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span style="font-size: 0.9rem; color: #666;">ID: {room['meeting_id']}</span>
                    <span class="status active">🟢 Live</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Video container
        st.markdown("### 📹 Video Feed")
        st.markdown("""
            <div class="video-container" id="videoContainer">
                <div class="video-participant">
                    <div class="avatar">👤</div>
                    <div class="participant-name">You (Connecting...)</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # LiveKit connection status
        if st.session_state.token:
            st.success(f"🔐 Connected to media server (Token: {st.session_state.token[:20]}...)")
            
            # Show connection info
            with st.expander("🔍 Media Server Details"):
                st.code(f"""
Meeting ID: {room['meeting_id']}
Role: {'Host' if is_host else 'Participant'}
Participant ID: {st.session_state.participant_id}
LiveKit URL: {st.session_state.room_data.get('livekit_url', 'Not set')}
                """, language="text")
        
        # Meeting controls
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🎤 Mute", use_container_width=True):
                st.info("🔇 Mute/Unmute feature coming soon!")
        
        with col2:
            if st.button("📹 Video", use_container_width=True):
                st.info("📹 Video toggle feature coming soon!")
        
        with col3:
            if st.button("🖥️ Share", use_container_width=True):
                st.info("🖥️ Screen sharing feature coming soon!")
        
        with col4:
            if st.button("💬 Chat", use_container_width=True):
                st.info("💬 Chat feature coming soon!")
        
        with col5:
            if st.button("🚪 Leave", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.session_state.room_data = None
                st.session_state.token = None
                st.session_state.participant_id = None
                st.session_state.is_host = False
                st.rerun()
        
        # Meeting info
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Participants")
            try:
                participants = get_participants(room['meeting_id'])
                if participants:
                    for p in participants:
                        is_me = p['id'] == st.session_state.participant_id
                        st.markdown(f"""
                            <div class="participant-info">
                                <strong>{p['name']}{' (You)' if is_me else ''}</strong>
                                <span style="color: #666; font-size: 0.8rem; margin-left: 0.5rem;">
                                    {p['company']} • {p['position']}
                                </span>
                                <span style="float: right; font-size: 0.8rem;">
                                    {'👑' if p['role'] == 'host' else '👤'}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No participants yet.")
            except Exception as e:
                st.error(f"Failed to load participants: {str(e)}")
        
        with col2:
            st.markdown("### 📊 Meeting Info")
            st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                    <p><strong>Meeting ID:</strong> {room['meeting_id']}</p>
                    <p><strong>Host:</strong> {room['host_name']}</p>
                    <p><strong>Created:</strong> {room['created_at'][:10]}</p>
                    <p><strong>Your Role:</strong> {'👑 Host' if is_host else '👤 Participant'}</p>
                </div>
            """, unsafe_allow_html=True)

# Custom JavaScript to load LiveKit SDK
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/livekit-client@latest/dist/livekit-client.umd.min.js">
</script>
<script>
    console.log('LiveKit SDK loaded');
</script>
""", unsafe_allow_html=True)

# Auto-refresh participants every 5 seconds
if st.session_state.page == 'meeting' and st.session_state.room_data:
    time.sleep(5)
    st.rerun()
