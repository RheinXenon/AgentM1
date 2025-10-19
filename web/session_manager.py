"""
会话管理器 - 管理用户会话和对话历史
"""
from typing import Dict, List
import uuid


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.sessions: Dict[str, Dict] = {}
    
    def get_or_create_session(self, session_id: str = None) -> tuple:
        """
        获取或创建会话
        
        Args:
            session_id: 会话ID，如果为None则创建新会话
            
        Returns:
            tuple: (session_id, conversation_history)
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "conversation_history": []
            }
        
        return session_id, self.sessions[session_id]["conversation_history"]
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        添加消息到会话历史
        
        Args:
            session_id: 会话ID
            role: 角色（user/assistant）
            content: 消息内容
        """
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"].append({
                "role": role,
                "content": content
            })
            
            # 限制历史长度，保持最近20条消息
            history = self.sessions[session_id]["conversation_history"]
            if len(history) > 20:
                self.sessions[session_id]["conversation_history"] = history[-20:]
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        return len(self.sessions)
    
    def clear_session(self, session_id: str):
        """清除指定会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]

