import streamlit as st
import time
import json
import os
from utils import create_room, join_room, get_rooms, get_room, get_participants
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av

# Page configuration
st.set_page_config(
    page_title="Zoom Clone Pro",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Zoom-like design
st.markdown("""
    <style>
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
        
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.6rem 1rem;
            border: none;
            transition: all 0.2s;
        }
        .stButton > button:hover { transform: scale(1.02); }
        
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
        
        .status-badge {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-badge.online { background: #4CAF50; }
        .status-badge.offline { background: #f44336; }
        
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
        
        .info-box {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .info-box p { margin: 0.3rem 0; }
        .info-box .label { font-weight: 600; color: #1A1A2E; }
        
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
        .device-selector .device-row label {
            font-weight: 500;
            min-width: 80px;
        }
        
        .join-options {
            background: #e8f5e9;
            border: 1px solid #4CAF50;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .join-options h4 { color: #2e7d32; margin: 0 0 1rem 0; }
        
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
        
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-dot.on { background: #4CAF50; }
        .status-dot.off { background: #f44336; }
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
if 'webrtc_started' not in st.session_state:
    st.session_state.webrtc_started = False
if 'camera_enabled' not in st.session_state:
    st.session_state.camera_enabled = False
if 'mic_enabled' not in st.session_state:
    st.session_state.mic_enabled = False

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
        
        **Features:**
        - 🎥 HD Video/Audio
        - 🖥️ Screen Sharing
        - 💬 Chat
        - 📹 Recording
        - 👥 Up to 100 participants
        - 🔊 Listen Only Mode
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
        
        st.markdown("---")
        st.markdown("### 🎥 Choose how to join")
        
        # Device selection like Zoom
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

elif st.session_state.page == 'meeting':
    if not st.session_state.room_data:
        st.error("No meeting data found.")
        if st.button("Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    else:
        room = st.session_state.room_data
        is_host = st.session_state.is_host
        
        # Meeting Header
        role_text = "Host" if is_host else "Participant"
        role_class = "host" if is_host else "participant"
        
        # Device status
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
                </div>
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <span class="meeting-id">ID: {room['meeting_id']}</span>
                    <span class="status active">🟢 Live</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Listen Only Mode Banner
        if st.session_state.listen_only:
            st.markdown("""
                <div class="listen-mode">
                    <h3>🔊 Listen Only Mode</h3>
                    <p>You are in listen-only mode. Your camera and microphone are turned off. You can still hear and see others.</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Video Call Section
        st.markdown("### 📹 Video Call")
        
        # Determine if we should try WebRTC
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
                # Fallback to listen-only
                st.session_state.listen_only = True
                st.rerun()
        else:
            # Listen Only Mode - Show placeholder
            st.markdown("""
                <div class="video-container">
                    <div class="placeholder">
                        <span class="icon">🔊</span>
                        <p>You are in <strong>Listen Only</strong> mode</p>
                        <p style="font-size: 0.9rem; opacity: 0.6;">Camera and microphone are disabled</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Option to enable devices
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
        
        # Meeting Controls
        st.markdown("### 🎮 Meeting Controls")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
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
                st.info(f"Screen sharing {status}!")
        
        with col4:
            if st.button("💬 Chat", use_container_width=True):
                st.session_state.chat_open = not st.session_state.chat_open
                st.rerun()
        
        with col5:
            # Quick device toggle
            if st.button("🎛️ Devices", use_container_width=True):
                st.info("Device settings - coming soon!")
        
        with col6:
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
                st.rerun()
        
        # Chat panel
        if st.session_state.chat_open:
            st.markdown("---")
            st.markdown("### 💬 Chat")
            chat_input = st.text_input("Type a message...", key="chat_input")
            if st.button("Send", key="send_chat"):
                if chat_input:
                    st.info(f"Message sent: {chat_input}")
        
        # Meeting Info
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Participants")
            try:
                participants = get_participants(room['meeting_id'])
                if participants:
                    for p in participants:
                        is_me = p['id'] == st.session_state.participant_id
                        role_label = "Host" if p['role'] == 'host' else "Participant"
                        role_class = "host" if p['role'] == 'host' else "participant"
                        st.markdown(f"""
                            <div class="participant-info">
                                <div>
                                    <span class="name">{p['name']}{' (You)' if is_me else ''}</span>
                                    <span class="details">{p['company']} • {p['position']}</span>
                                </div>
                                <span class="role {role_class}">{role_label}</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No participants yet.")
            except Exception as e:
                st.error(f"Failed to load participants: {str(e)}")
        
        with col2:
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
                </div>
            """, unsafe_allow_html=True)
        
        # Connection info
        if st.session_state.token:
            with st.expander("🔍 Connection Details"):
                st.code(f"""
Meeting ID: {room['meeting_id']}
Role: {'Host' if is_host else 'Participant'}
Camera: {'On' if st.session_state.camera_enabled else 'Off'}
Microphone: {'On' if st.session_state.mic_enabled else 'Off'}
Mode: {'Listen Only' if st.session_state.listen_only else 'Full Video'}
Participant ID: {st.session_state.participant_id}
Token: {st.session_state.token[:50]}...
                """, language="text")
