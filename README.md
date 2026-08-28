# 🎥 Zoom Clone Pro

A professional, self-hosted video conferencing platform with complete Zoom-like features.

## 🚀 Architecture

- **Frontend**: Streamlit (deployed on Streamlit Cloud)
- **Backend**: FastAPI (deployed on Render)
- **Media Server**: LiveKit (self-hosted on your PC)
- **Database**: SQLite (persistent)

## ✨ Features

- ✅ **HD Video Conferencing** - Crystal clear video with up to 100 participants
- ✅ **Screen Sharing** - Share your entire screen or specific windows
- ✅ **Audio/Video Controls** - Mute/unmute, video on/off
- ✅ **Real-time Chat** - Instant messaging during meetings
- ✅ **Meeting Recording** - Record meetings (host only)
- ✅ **Participants List** - See who's in the meeting
- ✅ **Hand Raise** - Non-verbal communication
- ✅ **Professional UI** - Modern, responsive design
- ✅ **Self-Hosted** - Complete data privacy and control

## 📦 Deployment

### 1. Backend (Render)

1. Push code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables:
   - `LIVEKIT_URL`: Your PC's LiveKit URL
   - `LIVEKIT_API_KEY`: Your LiveKit API key
   - `LIVEKIT_API_SECRET`: Your LiveKit secret
   - `ALLOWED_ORIGINS`: Your Streamlit app URL

### 2. Frontend (Streamlit Cloud)

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set `API_BASE` in secrets:
   ```toml
   API_BASE = "https://your-render-app.onrender.com"
