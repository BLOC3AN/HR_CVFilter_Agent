"""
Session Service for managing user sessions
Tracks session_id, chat history, and CV evaluations per session
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Session:
    """Session data structure"""
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    chat_history: List[dict] = field(default_factory=list)
    cv_evaluations: List[dict] = field(default_factory=list)
    job_description: str = ""
    custom_rules: str = ""
    llm_model: str = "gemini-2.0-flash"


class SessionService:
    """Service to manage user sessions"""
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.lock = Lock()
    
    def create_session(self) -> str:
        """Create a new session and return session_id"""
        session_id = str(uuid.uuid4())
        with self.lock:
            self.sessions[session_id] = Session(session_id=session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID, return None if not found or expired"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session is None:
                return None
            
            # Check if session expired
            if datetime.now() - session.last_activity > self.session_timeout:
                del self.sessions[session_id]
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
            return session
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, Session]:
        """Get existing session or create new one"""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session_id, session
        
        # Create new session
        new_session_id = self.create_session()
        return new_session_id, self.sessions[new_session_id]
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        session = self.get_session(session_id)
        if session is None:
            return False
        
        with self.lock:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
        return True
    
    def add_chat_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a chat message to session history"""
        session = self.get_session(session_id)
        if session is None:
            return False
        
        with self.lock:
            session.chat_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
        return True
    
    def add_cv_evaluation(self, session_id: str, filename: str, evaluation: str) -> bool:
        """Add CV evaluation to session"""
        session = self.get_session(session_id)
        if session is None:
            return False
        
        with self.lock:
            session.cv_evaluations.append({
                "filename": filename,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            })
        return True
    
    def clear_session(self, session_id: str) -> bool:
        """Clear session data"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        with self.lock:
            expired = []
            for session_id, session in self.sessions.items():
                if datetime.now() - session.last_activity > self.session_timeout:
                    expired.append(session_id)
            
            for session_id in expired:
                del self.sessions[session_id]
            
            return len(expired)
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)

