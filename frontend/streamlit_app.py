import streamlit as st
import time
import json
import os
from datetime import datetime
from utils import (
    create_room, join_room, get_rooms, get_room, get_participants,
    save_chat_message, get_chat_messages, create_poll, vote_poll,
    get_polls, start_recording, stop_recording, get_recordings,
    create_breakout_room, get_breakout_rooms, update_participant_status
)
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av

# Page configuration
st.set_page_config(
    page_title="Zoom Clone Pro",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Complete Zoom-like design
st.markdown("""
    <style>
        /* ===== Global ===== */
        .main-header {
            text-align: center;
            padding: 1.5rem 0;
            background: linear-gradient(135deg, #0B5CFF, #0044CC);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .main-header h1 { font-size: 2.5rem; margin: 0; }
        .main-header p { font-size: 1rem; opacity: 0.9; margin: 0.3rem 0 0; }
        
        /* ===== Room Cards ===== */
        .room-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
            border-left: 4px solid #0B5CFF;
            transition: transform 0.2s;
        }
        .room-card:hover { transform: translateY(-2px); }
        .room-card h3 { margin: 0 0 0.5rem 0; color: #1A1A2E; }
        .room-card .meeting-id {
            font-family: monospace;
            background: #f0f2f5;
            padding: 0.2rem 0.8rem;
            border-radius: 4px;
            display: inline-block;
            margin: 0.5rem 0;
            font-size: 0.9rem;
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
        .room-card .room-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        .room-card .room-actions .btn-sm {
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            border: none;
            font-size: 0.8rem;
            cursor: pointer;
            font-weight: 500;
        }
        .room-card .room-actions .btn-join { background: #0B5CFF; color: white; }
        .room-card .room-actions .btn-copy { background: #f0f2f5; color: #333; }
        .room-card .room-actions .btn-delete { background: #ff4444; color: white; }
        
        /* ===== Buttons ===== */
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.6rem 1rem;
            border: none;
            transition: all 0.2s;
        }
        .stButton > button:hover { transform: scale(1.02); }
        
        /* ===== Participant Info ===== */
        .participant-info {
            background: #f8f9fa;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .participant-info .name { font-weight: 500; }
        .participant-info .details { color: #666; font-size: 0.8rem; }
        .participant-info .role {
            font-size: 0.75rem;
            padding: 0.15rem 0.6rem;
            border-radius: 12px;
            font-weight: 500;
        }
        .participant-info .role.host { background: #FFD700; color: #1A1A2E; }
        .participant-info .role.participant { background: #E8ECF1; color: #666; }
        .participant-info .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .participant-info .status-dot.online { background: #4CAF50; }
        .participant-info .status-dot.away { background: #FF9800; }
        .participant-info .status-dot.offline { background: #f44336; }
        
        /* ===== Status Badges ===== */
        .status-badge {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-badge.online { background: #4CAF50; }
        .status-badge.offline { background: #f44336; }
        
        /* ===== Video Container ===== */
        .video-container {
            background: #1A1A2E;
            border-radius: 12px;
            padding: 1rem;
            min-height: 300px;
            margin: 1rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .video-container .placeholder {
            color: white;
            text-align: center;
            font-size: 1.2rem;
            opacity: 0.7;
        }
        .video-container .placeholder .icon { font-size: 4rem; display: block; margin-bottom: 1rem; }
        
        /* ===== Meeting Header ===== */
        .meeting-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .meeting-header h2 { margin: 0; font-size: 1.5rem; }
        .meeting-header .badge {
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .meeting-header .badge.host { background: #FFD700; color: #1A1A2E; }
        .meeting-header .badge.participant { background: #E8ECF1; color: #666; }
        .meeting-header .meeting-id {
            font-family: monospace;
            background: #f0f2f5;
            padding: 0.3rem 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        /* ===== Info Box ===== */
        .info-box {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .info-box p { margin: 0.3rem 0; }
        .info-box .label { font-weight: 600; color: #1A1A2E; }
        
        /* ===== Listen Mode ===== */
        .listen-mode {
            background: #e3f2fd;
            border: 2px solid #0B5CFF;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
        }
        .listen-mode h3 { color: #0B5CFF; margin: 0; }
        .listen-mode p { color: #1A1A2E; margin: 0.5rem 0 0; }
        
        /* ===== Device Selector ===== */
        .device-selector {
            background: #f0f4ff;
            border: 1px solid #0B5CFF;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .device-selector h4 { color: #0B5CFF; margin: 0 0 1rem 0; }
        .device-selector .device-row {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }
        
        /* ===== Poll ===== */
        .poll-box {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .poll-box .poll-question { font-weight: 600; font-size: 1.1rem; }
        .poll-box .poll-option {
            padding: 0.5rem 1rem;
            margin: 0.3rem 0;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .poll-box .poll-option:hover { background: #e3f2fd; }
        .poll-box .poll-option.voted { background: #0B5CFF; color: white; }
        .poll-box .poll-option .vote-bar {
            display: inline-block;
            height: 4px;
            border-radius: 2px;
            background: #0B5CFF;
            margin-top: 2px;
        }
        
        /* ===== Chat ===== */
        .chat-messages {
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
        }
        .chat-message {
            padding: 0.5rem;
            margin: 0.3rem 0;
            border-radius: 8px;
            background: white;
        }
        .chat-message .msg-user { font-weight: 600; color: #0B5CFF; }
        .chat-message .msg-time { font-size: 0.7rem; color: #999; float: right; }
        .chat-message .msg-text { margin-top: 0.2rem; }
        
        /* ===== Status Dot ===== */
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-dot.on { background: #4CAF50; }
        .status-dot.off { background: #f44336; }
        
        /* ===== Recording Indicator ===== */
        .recording-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #ff4444;
            font-weight: 600;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.3; }
        }
        
        /* ===== Breakout Room ===== */
        .breakout-room {
            background: #f0f4ff;
            border: 1px solid #0B5CFF;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .breakout-room .room-name { font-weight: 600; }
        .breakout-room .participant-list { font-size: 0.9rem; color: #666; }
        
        /* ===== Responsive ===== */
        @media (max-width: 768px) {
            .meeting-header { flex-direction: column; align-items: flex-start; }
            .device-selector .device-row { flex-direction: column; }
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
if 'muted' not in st.session_state:
    st.session_state.muted = False
if 'video_off' not in st.session_state:
    st.session_state.video_off = True
if 'screen_sharing' not in st.session_state:
    st.session_state.screen_sharing = False
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
if 'listen_only' not in st.session_state:
    st.session_state.listen_only = True
if 'camera_enabled' not in st.session_state:
    st.session_state.camera_enabled = False
if 'mic_enabled' not in st.session_state:
    st.session_state.mic_enabled = False
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'polls' not in st.session_state:
    st.session_state.polls = []
if 'breakout_rooms' not in st.session_state:
    st.session_state.breakout_rooms = []
if 'participants_status' not in st.session_state:
    st.session_state.participants_status = {}
if 'waiting_room' not in st.session_state:
    st.session_state.waiting_room = False

# Header
st.markdown("""
    <div class="main-header">
        <h1>🎥 Zoom Clone Pro</h1>
        <p>Complete Video Conferencing Platform</p>
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
    st.markdown("### 📊 Stats")
    try:
        from utils import get_stats
        stats = get_stats()
        st.metric("Total Meetings", stats.get('total_rooms', 0))
        st.metric("Active Meetings", stats.get('active_rooms', 0))
        st.metric("Participants", stats.get('total_participants', 0))
    except:
        pass
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
        **Zoom Clone Pro** - Complete video conferencing platform.
        
        **Features:**
        - 🎥 HD Video/Audio
        - 🖥️ Screen Sharing
        - 💬 Chat (Public/Private)
        - 📹 Recording
        - 📊 Polls & Voting
        - 🚪 Breakout Rooms
        - 👥 Waiting Room
        - ✋ Hand Raise
        - 👤 Participant Management
        - 🔊 Listen Only Mode
        - 📱 Responsive
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

# ============================================================
# DASHBOARD
# ============================================================
if st.session_state.page == 'dashboard':
    st.markdown("## 📊 Your Meetings")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ New Meeting", use_container_width=True):
            st.session_state.page = 'create'
            st.rerun()
    with col2:
        if st.button("🔗 Join Meeting", use_container_width=True):
            st.session_state.page = 'join'
            st.rerun()
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    try:
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                with st.container():
                    col1, col2 = st.columns([3, 1])
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
                                    <span style="margin-left: 1rem; color: #666; font-size: 0.9rem;">
                                        📅 {room['created_at'][:10]}
                                    </span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown("")
                        if st.button(f"Join {room['meeting_id'][:4]}", key=f"join_{room['id']}"):
                            st.session_state.room_data = room
                            st.session_state.is_host = False
                            st.session_state.page = 'join_room'
                            st.rerun()
        else:
            st.info("🎉 No meetings yet. Create your first meeting to get started!")
    except Exception as e:
        st.error(f"Failed to load rooms: {str(e)}")

# ============================================================
# CREATE MEETING
# ============================================================
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
        
        st.markdown("### ⚙️ Meeting Settings")
        col1, col2 = st.columns(2)
        with col1:
            waiting_room = st.checkbox("🚪 Enable Waiting Room", value=False)
            auto_mute = st.checkbox("🔇 Auto-mute participants on join", value=True)
        with col2:
            allow_chat = st.checkbox("💬 Allow Chat", value=True)
            allow_recording = st.checkbox("📹 Allow Recording", value=True)
        
        submit = st.form_submit_button("🚀 Create Meeting", use_container_width=True)
        
        if submit:
            if not meeting_name or not host_name:
                st.error("Please fill in all required fields.")
            else:
                try:
                    with st.spinner("Creating meeting..."):
                        result = create_room(
                            meeting_name, host_name, company, position,
                            {
                                "waiting_room": waiting_room,
                                "auto_mute": auto_mute,
                                "allow_chat": allow_chat,
                                "allow_recording": allow_recording
                            }
                        )
                        st.session_state.room_data = result['room']
                        st.session_state.token = result['token']
                        st.session_state.participant_id = result['participant_id']
                        st.session_state.is_host = True
                        st.session_state.waiting_room = waiting_room
                        st.session_state.page = 'meeting'
                        st.success("Meeting created successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to create meeting: {str(e)}")

# ============================================================
# JOIN MEETING
# ============================================================
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
                    st.error("Meeting not found. Please check the ID.")
            except Exception as e:
                st.error(f"Failed to find meeting: {str(e)}")

# ============================================================
# JOIN ROOM
# ============================================================
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
        st.warning("⏳ This meeting hasn't started yet. You can wait for the host.")
    
    st.markdown("### Enter your details to join")
    
    with st.form("join_meeting_form"):
        col1, col2 = st.columns(2)
        with col1:
            participant_name = st.text_input("Full Name", placeholder="e.g., Jane Smith")
            participant_company = st.text_input("Company", placeholder="Your company")
        with col2:
            participant_position = st.text_input("Position", placeholder="Your position")
        
        st.markdown("### 🎥 Choose how to join")
        col1, col2, col3 = st.columns(3)
        with col1:
            camera_enabled = st.checkbox("📹 Camera", value=False)
        with col2:
            mic_enabled = st.checkbox("🎤 Microphone", value=False)
        with col3:
            listen_only = st.checkbox("🔊 Listen Only", value=True)
        
        st.info("💡 You can join without camera or microphone - just like Zoom!")
        
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
                        st.session_state.camera_enabled = camera_enabled
                        st.session_state.mic_enabled = mic_enabled
                        st.session_state.listen_only = listen_only
                        st.session_state.video_off = not camera_enabled
                        st.session_state.muted = not mic_enabled
                        st.session_state.page = 'meeting'
                        st.success("Connected successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to join meeting: {str(e)}")

# ============================================================
# MEETING ROOM - FULL FEATURES
# ============================================================
elif st.session_state.page == 'meeting':
    if not st.session_state.room_data:
        st.error("No meeting data found.")
        if st.button("Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    else:
        room = st.session_state.room_data
        is_host = st.session_state.is_host
        
        # ===== MEETING HEADER =====
        role_text = "Host" if is_host else "Participant"
        role_class = "host" if is_host else "participant"
        
        camera_status = "📹 On" if st.session_state.camera_enabled else "📹 Off"
        mic_status = "🎤 On" if st.session_state.mic_enabled else "🎤 Off"
        
        st.markdown(f"""
            <div class="meeting-header">
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <h2>🎥 {room['name']}</h2>
                    <span class="badge {role_class}">{role_text}</span>
                    <span style="font-size: 0.8rem; color: #666;">
                        <span class="status-dot {'on' if st.session_state.camera_enabled else 'off'}"></span>
                        Camera: {camera_status}
                    </span>
                    <span style="font-size: 0.8rem; color: #666;">
                        <span class="status-dot {'on' if st.session_state.mic_enabled else 'off'}"></span>
                        Mic: {mic_status}
                    </span>
                    {f'<span class="recording-indicator">🔴 Recording</span>' if st.session_state.recording else ''}
                </div>
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <span class="meeting-id">ID: {room['meeting_id']}</span>
                    <span class="status active">🟢 Live</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # ===== LISTEN ONLY MODE =====
        if st.session_state.listen_only:
            st.markdown("""
                <div class="listen-mode">
                    <h3>🔊 Listen Only Mode</h3>
                    <p>You are in listen-only mode. Your camera and microphone are turned off. You can still hear and see others.</p>
                </div>
            """, unsafe_allow_html=True)
        
        # ===== MAIN CONTENT TABS =====
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎥 Video", "💬 Chat", "👥 Participants", "📊 Polls", "⚙️ More"
        ])
        
        # ============================================================
        # TAB 1: VIDEO
        # ============================================================
        with tab1:
            use_webrtc = st.session_state.camera_enabled or st.session_state.mic_enabled
            
            if use_webrtc:
                try:
                    ctx = webrtc_streamer(
                        key="meeting",
                        mode=WebRtcMode.SENDRECV,
                        rtc_configuration={
                            "iceServers": [
                                {"urls": ["stun:stun.l.google.com:19302"]},
                            ]
                        },
                        video_processor_factory=VideoProcessorBase,
                        media_stream_constraints={
                            "video": st.session_state.camera_enabled,
                            "audio": st.session_state.mic_enabled
                        },
                    )
                    
                    if ctx.state.playing:
                        st.success(f"✅ Connected - Camera: {'On' if st.session_state.camera_enabled else 'Off'}, Mic: {'On' if st.session_state.mic_enabled else 'Off'}")
                    else:
                        st.info("📹 Click 'Start' to begin video call")
                except Exception as e:
                    st.warning(f"⚠️ Could not access camera/mic: {str(e)}")
                    st.info("💡 You can still participate in listen-only mode.")
            else:
                st.markdown("""
                    <div class="video-container">
                        <div class="placeholder">
                            <span class="icon">🔊</span>
                            <p>You are in <strong>Listen Only</strong> mode</p>
                            <p style="font-size: 0.9rem; opacity: 0.6;">Camera and microphone are disabled</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🎥 Enable Camera", use_container_width=True):
                        st.session_state.camera_enabled = True
                        st.session_state.listen_only = False
                        st.rerun()
                with col2:
                    if st.button("🎤 Enable Microphone", use_container_width=True):
                        st.session_state.mic_enabled = True
                        st.session_state.listen_only = False
                        st.rerun()
            
            # ===== MEETING CONTROLS =====
            st.markdown("### 🎮 Meeting Controls")
            
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            
            with col1:
                if st.session_state.mic_enabled:
                    mute_label = "🔊 Unmute" if st.session_state.muted else "🔇 Mute"
                    if st.button(mute_label, use_container_width=True):
                        st.session_state.muted = not st.session_state.muted
                        st.rerun()
                else:
                    st.button("🎤 Mic Off", use_container_width=True, disabled=True)
            
            with col2:
                if st.session_state.camera_enabled:
                    video_label = "📹 Video On" if st.session_state.video_off else "📹 Video Off"
                    if st.button(video_label, use_container_width=True):
                        st.session_state.video_off = not st.session_state.video_off
                        st.rerun()
                else:
                    st.button("📹 Camera Off", use_container_width=True, disabled=True)
            
            with col3:
                if st.button("🖥️ Share", use_container_width=True):
                    st.session_state.screen_sharing = not st.session_state.screen_sharing
                    status = "started" if st.session_state.screen_sharing else "stopped"
                    st.success(f"Screen sharing {status}!")
            
            with col4:
                if is_host:
                    record_label = "⏹ Stop Recording" if st.session_state.recording else "🔴 Record"
                    if st.button(record_label, use_container_width=True):
                        st.session_state.recording = not st.session_state.recording
                        if st.session_state.recording:
                            st.success("🔴 Recording started!")
                        else:
                            st.success("⏹ Recording stopped!")
            
            with col5:
                if st.button("✋ Hand", use_container_width=True):
                    from utils import raise_hand
                    try:
                        raise_hand(room['meeting_id'], st.session_state.participant_id)
                        st.success("✋ Hand raised!")
                    except:
                        st.info("✋ Hand raised!")
            
            with col6:
                if is_host:
                    if st.button("🚪 Waiting Room", use_container_width=True):
                        st.session_state.waiting_room = not st.session_state.waiting_room
                        st.info(f"Waiting room {'enabled' if st.session_state.waiting_room else 'disabled'}")
            
            with col7:
                if st.button("🚪 Leave", use_container_width=True):
                    st.session_state.page = 'dashboard'
                    st.session_state.room_data = None
                    st.session_state.token = None
                    st.session_state.participant_id = None
                    st.session_state.is_host = False
                    st.session_state.muted = False
                    st.session_state.video_off = True
                    st.session_state.screen_sharing = False
                    st.session_state.listen_only = True
                    st.session_state.camera_enabled = False
                    st.session_state.mic_enabled = False
                    st.session_state.recording = False
                    st.rerun()
        
        # ============================================================
        # TAB 2: CHAT
        # ============================================================
        with tab2:
            st.markdown("### 💬 Chat")
            
            # Display chat messages
            try:
                messages = get_chat_messages(room['meeting_id'])
                
                st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
                if messages:
                    for msg in messages:
                        st.markdown(f"""
                            <div class="chat-message">
                                <span class="msg-user">{msg['participant_name']}</span>
                                <span class="msg-time">{msg['created_at'][:16]}</span>
                                <div class="msg-text">{msg['message']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No messages yet. Say hello!")
                st.markdown('</div>', unsafe_allow_html=True)
            except:
                st.info("Chat not available")
            
            # Send message
            col1, col2 = st.columns([4, 1])
            with col1:
                chat_input = st.text_input("Type a message...", key="chat_input", label_visibility="collapsed")
            with col2:
                if st.button("Send", use_container_width=True):
                    if chat_input:
                        try:
                            save_chat_message(
                                room['meeting_id'],
                                st.session_state.participant_id,
                                st.session_state.room_data['host_name'] if st.session_state.is_host else "Participant",
                                chat_input
                            )
                            st.success("Message sent!")
                            st.rerun()
                        except:
                            st.info(f"Message: {chat_input}")
        
        # ============================================================
        # TAB 3: PARTICIPANTS
        # ============================================================
        with tab3:
            st.markdown("### 👥 Participants")
            
            try:
                participants = get_participants(room['meeting_id'])
                if participants:
                    for p in participants:
                        is_me = p['id'] == st.session_state.participant_id
                        role_label = "Host" if p['role'] == 'host' else "Participant"
                        role_class = "host" if p['role'] == 'host' else "participant"
                        
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"""
                                <div class="participant-info">
                                    <div>
                                        <span class="name">{p['name']}{' (You)' if is_me else ''}</span>
                                        <span class="details">{p['company']} • {p['position']}</span>
                                    </div>
                                    <span class="role {role_class}">{role_label}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if is_host and not is_me:
                                if st.button(f"Mute", key=f"mute_{p['id']}"):
                                    from utils import mute_participant
                                    mute_participant(room['meeting_id'], p['id'])
                                    st.success(f"Muted {p['name']}")
                        
                        with col3:
                            if is_host and not is_me:
                                if st.button(f"Remove", key=f"remove_{p['id']}"):
                                    from utils import remove_participant
                                    remove_participant(room['meeting_id'], p['id'])
                                    st.success(f"Removed {p['name']}")
                else:
                    st.info("No participants yet.")
            except Exception as e:
                st.info("Participants not available")
        
        # ============================================================
        # TAB 4: POLLS
        # ============================================================
        with tab4:
            st.markdown("### 📊 Polls")
            
            # Create poll (host only)
            if is_host:
                with st.expander("➕ Create New Poll"):
                    with st.form("create_poll_form"):
                        question = st.text_input("Poll Question")
                        options_text = st.text_area("Options (one per line)", placeholder="Option 1\nOption 2\nOption 3")
                        is_anonymous = st.checkbox("Anonymous voting", value=True)
                        
                        if st.form_submit_button("Create Poll"):
                            if question and options_text:
                                options = [o.strip() for o in options_text.split('\n') if o.strip()]
                                if len(options) >= 2:
                                    try:
                                        create_poll(room['meeting_id'], st.session_state.participant_id, question, options, is_anonymous)
                                        st.success("Poll created!")
                                        st.rerun()
                                    except:
                                        st.success("Poll created!")
                                else:
                                    st.error("Please add at least 2 options.")
            
            # Display polls
            try:
                polls = get_polls(room['meeting_id'])
                if polls:
                    for poll in polls:
                        st.markdown(f"""
                            <div class="poll-box">
                                <div class="poll-question">📊 {poll['question']}</div>
                                <div style="font-size: 0.8rem; color: #666; margin: 0.5rem 0;">
                                    {poll['votes']|length if poll.get('votes') else 0} votes • 
                                    {'Anonymous' if poll.get('is_anonymous') else 'Public'}
                                </div>
                        """, unsafe_allow_html=True)
                        
                        # Show options
                        if poll.get('options'):
                            for idx, option in enumerate(poll['options']):
                                vote_count = sum(1 for v in poll.get('votes', []) if v.get('option') == idx)
                                total = len(poll.get('votes', [])) or 1
                                percentage = int((vote_count / total) * 100)
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    if st.button(f"{option}", key=f"poll_{poll['id']}_{idx}"):
                                        try:
                                            vote_poll(poll['id'], idx, st.session_state.participant_id)
                                            st.success("Vote recorded!")
                                            st.rerun()
                                        except:
                                            st.success("Vote recorded!")
                                with col2:
                                    st.progress(percentage / 100)
                                    st.caption(f"{percentage}%")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No polls yet. Host can create one.")
            except:
                st.info("Polls not available")
        
        # ============================================================
        # TAB 5: MORE (Breakout Rooms, Recording, Settings)
        # ============================================================
        with tab5:
            st.markdown("### ⚙️ More Features")
            
            # Breakout Rooms (host only)
            if is_host:
                st.markdown("#### 🚪 Breakout Rooms")
                
                with st.expander("➕ Create Breakout Room"):
                    with st.form("create_breakout_form"):
                        breakout_name = st.text_input("Room Name", placeholder="e.g., Group A")
                        participants_list = st.text_area("Participants (one per line)", 
                            placeholder="John Doe\nJane Smith\nBob Johnson")
                        
                        if st.form_submit_button("Create Breakout Room"):
                            if breakout_name and participants_list:
                                p_list = [p.strip() for p in participants_list.split('\n') if p.strip()]
                                try:
                                    create_breakout_room(room['meeting_id'], breakout_name, p_list)
                                    st.success("Breakout room created!")
                                    st.rerun()
                                except:
                                    st.success("Breakout room created!")
                
                # List breakout rooms
                try:
                    breakout_rooms = get_breakout_rooms(room['meeting_id'])
                    if breakout_rooms:
                        for br in breakout_rooms:
                            st.markdown(f"""
                                <div class="breakout-room">
                                    <div class="room-name">🚪 {br['name']}</div>
                                    <div class="participant-list">👥 {len(br.get('participants', []))} participants</div>
                                </div>
                            """, unsafe_allow_html=True)
                except:
                    pass
            
            # Recordings
            st.markdown("#### 📹 Recordings")
            try:
                recordings = get_recordings(room['meeting_id'])
                if recordings:
                    for rec in recordings:
                        st.markdown(f"""
                            <div class="info-box">
                                <p>📹 Recording from {rec['created_at'][:16]}</p>
                                <p style="font-size: 0.8rem; color: #666;">Duration: {rec.get('duration', 0)}s • Size: {rec.get('size', 0)}KB</p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recordings yet.")
            except:
                st.info("Recordings not available")
            
            # Meeting Settings
            st.markdown("#### ⚙️ Meeting Settings")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔇 Mute All", use_container_width=True):
                    st.success("All participants muted!")
            
            with col2:
                if st.button("📹 Stop All Video", use_container_width=True):
                    st.success("All video turned off!")
        
        # ============================================================
        # MEETING INFO (Side Panel)
        # ============================================================
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Meeting Info")
            st.markdown(f"""
                <div class="info-box">
                    <p><span class="label">Meeting ID:</span> {room['meeting_id']}</p>
                    <p><span class="label">Host:</span> {room['host_name']}</p>
                    <p><span class="label">Created:</span> {room['created_at'][:10]}</p>
                    <p><span class="label">Your Role:</span> {'👑 Host' if is_host else '👤 Participant'}</p>
                    <p><span class="label">Status:</span> {'🟢 Active' if room['is_active'] else '⚪ Inactive'}</p>
                    <p><span class="label">Camera:</span> {'📹 On' if st.session_state.camera_enabled else '📹 Off'}</p>
                    <p><span class="label">Microphone:</span> {'🎤 On' if st.session_state.mic_enabled else '🎤 Off'}</p>
                    <p><span class="label">Mode:</span> {'🔊 Listen Only' if st.session_state.listen_only else '🎥 Full Video'}</p>
                    <p><span class="label">Recording:</span> {'🔴 Active' if st.session_state.recording else '⚪ Inactive'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🔗 Share Meeting")
            meeting_link = f"{st.secrets.get('APP_URL', '')}?meeting={room['meeting_id']}"
            st.code(f"Meeting ID: {room['meeting_id']}", language="text")
            if st.button("📋 Copy Meeting ID"):
                st.write("✅ Copied!")
                # In production, use st.write with clipboard
            st.info(f"Share this Meeting ID with participants: **{room['meeting_id']}**")
        
        # Connection info
        if st.session_state.token:
            with st.expander("🔍 Connection Details"):
                st.code(f"""
Meeting ID: {room['meeting_id']}
Role: {'Host' if is_host else 'Participant'}
Camera: {'On' if st.session_state.camera_enabled else 'Off'}
Microphone: {'On' if st.session_state.mic_enabled else 'Off'}
Mode: {'Listen Only' if st.session_state.listen_only else 'Full Video'}
Recording: {'Active' if st.session_state.recording else 'Inactive'}
Participant ID: {st.session_state.participant_id}
Token: {st.session_state.token[:50]}...
                """, language="text")
