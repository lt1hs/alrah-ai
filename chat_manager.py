import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class ChatManager:
    def __init__(self, base_dir: str = "chat_history"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
    def create_session(self, user_id: int) -> str:
        session_id = str(uuid.uuid4())[:8]
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        self._save_session(user_id, session_id, session_data)
        return session_id
    
    def add_message(self, user_id: int, session_id: str, role: str, content: str):
        session_data = self._load_session(user_id, session_id)
        if session_data:
            session_data["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self._save_session(user_id, session_id, session_data)
    
    def get_session_history(self, user_id: int, session_id: str) -> List[Dict]:
        session_data = self._load_session(user_id, session_id)
        return session_data["messages"] if session_data else []
    
    def list_user_sessions(self, user_id: int) -> List[Dict]:
        sessions = []
        for filename in os.listdir(self.base_dir):
            if filename.startswith(f"user_{user_id}_"):
                session_id = filename.replace(f"user_{user_id}_", "").replace(".json", "")
                session_data = self._load_session(user_id, session_id)
                if session_data:
                    sessions.append({
                        "session_id": session_id,
                        "created_at": session_data["created_at"],
                        "message_count": len(session_data["messages"])
                    })
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
    
    def delete_session(self, user_id: int, session_id: str) -> bool:
        filepath = self._get_filepath(user_id, session_id)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def _get_filepath(self, user_id: int, session_id: str) -> str:
        return os.path.join(self.base_dir, f"user_{user_id}_{session_id}.json")
    
    def _load_session(self, user_id: int, session_id: str) -> Optional[Dict]:
        filepath = self._get_filepath(user_id, session_id)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_session(self, user_id: int, session_id: str, data: Dict):
        filepath = self._get_filepath(user_id, session_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
