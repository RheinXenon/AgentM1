"""
数据模型定义
"""
from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatRequest(BaseModel):
    """聊天请求模型"""
    query: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    session_id: str
    agent: str
    response: str
    sources: Optional[List[Dict]] = None
    confidence: Optional[float] = None


class ConfigRequest(BaseModel):
    """配置更新请求模型"""
    rag_enabled: Optional[bool] = None
    agent_decision_prompt: Optional[str] = None
    conversation_prompt: Optional[str] = None
    rag_prompt: Optional[str] = None
    websearch_prompt: Optional[str] = None
    system_name: Optional[str] = None
    welcome_message: Optional[str] = None

