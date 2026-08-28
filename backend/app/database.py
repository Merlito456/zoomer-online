import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
import uuid
from contextlib import contextmanager
import os

class Database:
    def __init__(self, db_path="zoom.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                meeting_id TEXT UNIQUE NOT NULL,
                host_id TEXT NOT NULL,
                host_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                is_recording INTEGER DEFAULT 0,
                start_time TEXT,
                end_time TEXT
            )
        ''')
        
        # Participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                left_at TEXT,
                is_muted INTEGER DEFAULT 0,
                is_video_off INTEGER DEFAULT 1,
                is_screen_sharing INTEGER DEFAULT 0,
                is_hand_raised INTEGER DEFAULT 0,
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
        ''')
        
        # Chat messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                participant_id TEXT NOT NULL,
                participant_name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_private INTEGER DEFAULT 0,
                recipient_id TEXT,
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_room(self, name: str, host_id: str, host_name: str, host_email: str = None) -> dict:
        room_id = str(uuid.uuid4())
        meeting_id = f"{uuid.uuid4().hex[:8].upper()}"
        
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO rooms (id, name, meeting_id, host_id, host_name, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            ''', (room_id, name, meeting_id, host_id, host_name, datetime.utcnow().isoformat()))
            conn.commit()
        
        return self.get_room_by_meeting_id(meeting_id)
    
    def get_room_by_meeting_id(self, meeting_id: str) -> Optional[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rooms WHERE meeting_id = ?', (meeting_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def get_room_by_id(self, room_id: str) -> Optional[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def get_all_rooms(self) -> List[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rooms ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def add_participant(self, room_id: str, name: str, company: str, position: str, role: str, email: str = None) -> dict:
        participant_id = str(uuid.uuid4())
        
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO participants (id, room_id, name, email, company, position, role, joined_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (participant_id, room_id, name, email, company, position, role, datetime.utcnow().isoformat()))
            conn.commit()
        
        return self.get_participant(participant_id)
    
    def get_participant(self, participant_id: str) -> Optional[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM participants WHERE id = ?', (participant_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def get_participants(self, room_id: str) -> List[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM participants 
                WHERE room_id = ? AND left_at IS NULL
                ORDER BY joined_at
            ''', (room_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def remove_participant(self, participant_id: str):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE participants SET left_at = ? WHERE id = ?', 
                         (datetime.utcnow().isoformat(), participant_id))
            conn.commit()
    
    def save_chat_message(self, room_id: str, participant_id: str, participant_name: str, message: str) -> dict:
        msg_id = str(uuid.uuid4())
        
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_messages (id, room_id, participant_id, participant_name, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (msg_id, room_id, participant_id, participant_name, message, datetime.utcnow().isoformat()))
            conn.commit()
        
        return self.get_chat_message(msg_id)
    
    def get_chat_message(self, message_id: str) -> Optional[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM chat_messages WHERE id = ?', (message_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def get_chat_messages(self, room_id: str, limit: int = 50) -> List[dict]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM chat_messages 
                WHERE room_id = ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (room_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
    
    def update_room_status(self, room_id: str, is_active: bool, is_recording: bool = None):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            updates = []
            values = []
            
            if is_active is not None:
                updates.append("is_active = ?")
                values.append(1 if is_active else 0)
                if is_active:
                    updates.append("start_time = ?")
                    values.append(datetime.utcnow().isoformat())
                else:
                    updates.append("end_time = ?")
                    values.append(datetime.utcnow().isoformat())
            
            if is_recording is not None:
                updates.append("is_recording = ?")
                values.append(1 if is_recording else 0)
            
            if updates:
                values.append(room_id)
                cursor.execute(f'UPDATE rooms SET {", ".join(updates)} WHERE id = ?', values)
                conn.commit()

# Use SQLite with persistent storage
db = Database("zoom.db")
