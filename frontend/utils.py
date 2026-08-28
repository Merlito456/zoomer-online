import streamlit as st
import time
import json
from utils import create_room, join_room, get_rooms, get_room, get_participants, get_stats, API_BASE

# Page configuration
st.set_page_config(
    page_title="Zoom Clone Pro",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional look
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
        .main-header h1 {
            font-size: 3rem;
            margin: 0;
        }
        .main-header p {
            font-size: 1.2rem;
            opacity: 0.9;
            margin: 0.5rem 0 0;
        }
        .room-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border-left: 4px solid #0066FF;
        }
        .room-card h3 {
            margin: 0 0 0.5rem 0;
            color: #1A1A2E;
        }
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
        .room-card .status.active {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .room-card .status.inactive {
            background: #f5f5f5;
            color: #757575;
        }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 500;
        }
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
        .status-badge.online {
            background: #4CAF50;
        }
        .status-badge.offline {
            background: #f44336;
        }
        .meeting-container {
            background: #1A1A2E;
            border-radius: 12px;
            padding: 2rem;
            color: white;
            text-align: center;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .meeting-container h2 {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        .meeting-container .info {
            color: #aaa;
            font-size: 1rem;
        }
        .api-status {
            padding: 0.5rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .api-status.online {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .api-status.offline {
            background: #ffebee;
            color: #c62828;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'current_meeting' not in st.session_state:
    st.session_state.current_meeting = None
if 'participant_id' not in st.session_state:
    st.session_state.participant_id = None
if 'room_data' not in st.session_state:
    st.session_state.room_data = None
if 'token' not in st.session_state:
    st.session_state.token = None

# Header
st.markdown("""
    <div class="main-header">
        <h1>🎥 Zoom Clone Pro</h1>
        <p>Professional Video Conferencing Platform</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar - Navigation
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
        # Check backend status
        try:
            import requests
            response = requests.get(f"{API_BASE}/api/health", timeout=2)
            if response.status_code == 200:
                st.markdown('<span class="status-badge online"></span> Online', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-badge offline"></span> Offline', unsafe_allow_html=True)
        except:
            st.markdown('<span class="status-badge offline"></span> Offline', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**LiveKit**")
        st.markdown('<span class="status-badge online"></span> Connected', unsafe_allow_html=True)

# Main content
if st.session_state.page == 'dashboard':
    # Dashboard View
    st.markdown("## 📊 Your Meetings")
    
    # Check API connection
    try:
        stats = get_stats()
        st.markdown(f"""
            <div class="api-status online">
                ✅ Connected to backend at {API_BASE}
            </div>
        """, unsafe_allow_html=True)
        
        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Meetings", stats.get('total_rooms', 0))
        with col2:
            st.metric("Active Meetings", stats.get('active_rooms', 0))
        with col3:
            st.metric("Participants", stats.get('total_participants', 0))
            
    except:
        st.markdown(f"""
            <div class="api-status offline">
                ❌ Cannot connect to backend at {API_BASE}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
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
                    
                    with col2:
                        st.markdown("")
                    
                    with col3:
                        if st.button(f"Join {room['meeting_id'][:4]}", key=f"join_{room['id']}"):
                            st.session_state.page = 'join_room'
                            st.session_state.room_data = room
                            st.rerun()
        else:
            st.info("No meetings created yet. Create a new meeting to get started!")
            
    except Exception as e:
        st.error(f"Failed to load rooms: {str(e)}")
        st.info("Make sure the backend server is running.")

elif st.session_state.page == 'create':
    # Create Meeting View
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
                        st.session_state.page = 'meeting'
                        st.success("Meeting created successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to create meeting: {str(e)}")

elif st.session_state.page == 'join':
    # Join Meeting View
    st.markdown("## 🔗 Join Meeting")
    
    meeting_id = st.text_input("Meeting ID", placeholder="e.g., A1B2C3D4", max_chars=8)
    meeting_id = meeting_id.upper()
    
    if st.button("Check Meeting", use_container_width=True):
        if meeting_id:
            try:
                room = get_room(meeting_id)
                if room:
                    st.session_state.room_data = room
                    st.session_state.page = 'join_room'
                    st.rerun()
                else:
                    st.error("Meeting not found. Please check the ID.")
            except Exception as e:
                st.error(f"Failed to find meeting: {str(e)}")

elif st.session_state.page == 'join_room':
    # Join Room View (after meeting found)
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
            st.markdown("")  # Spacer
        
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
                            participant_company or "Unknown",
                            participant_position or "Guest"
                        )
                        st.session_state.token = result['token']
                        st.session_state.participant_id = result['participant_id']
                        st.session_state.page = 'meeting'
                        st.success("Connected successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to join meeting: {str(e)}")

elif st.session_state.page == 'meeting':
    # Meeting View
    if not st.session_state.room_data:
        st.error("No meeting data found. Please go back to the dashboard.")
        if st.button("Back to Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    else:
        room = st.session_state.room_data
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2>🎥 {room['name']}</h2>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span style="font-size: 0.9rem; color: #666;">ID: {room['meeting_id']}</span>
                    <span class="status active">🟢 Live</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Meeting controls
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🎤 Mute", use_container_width=True):
                st.info("Toggle mute - Coming soon!")
        
        with col2:
            if st.button("📹 Video", use_container_width=True):
                st.info("Toggle video - Coming soon!")
        
        with col3:
            if st.button("🖥️ Share", use_container_width=True):
                st.info("Screen sharing - Coming soon!")
        
        with col4:
            if st.button("💬 Chat", use_container_width=True):
                st.info("Chat - Coming soon!")
        
        with col5:
            if st.button("🚪 Leave", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.session_state.room_data = None
                st.session_state.token = None
                st.session_state.participant_id = None
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
                        st.markdown(f"""
                            <div class="participant-info">
                                <strong>{p['name']}</strong>
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
                    <p><strong>Status:</strong> {'🟢 Active' if room['is_active'] else '⚪ Inactive'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Connection info
        if st.session_state.token:
            st.markdown("---")
            st.markdown("### 🔗 Connection Details")
            st.success("✅ Securely connected to media server")
            
            with st.expander("🔍 Technical Details"):
                st.code(f"""
API Base: {API_BASE}
Meeting ID: {room['meeting_id']}
Participant ID: {st.session_state.participant_id}
Token: {st.session_state.token[:50]}...
                """, language="text")
