"""
FastAPI应用初始化
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .session_manager import SessionManager
from .routes import chat_router, config_router, health_router
from .routes.chat import init_chat_routes
from .routes.config import init_config_routes
from .routes.health import init_health_routes

# 导入智能体
from agents.agent_decision import AgentDecision
from agents.rag_agent import MedicalRAG
from agents.web_search_agent import WebSearchAgent
from agents.conversation_agent import ConversationAgent

# 导入配置管理器
from config_manager import ConfigManager


def create_app() -> FastAPI:
    """
    创建并配置FastAPI应用
    
    Returns:
        FastAPI: 配置好的FastAPI应用实例
    """
    # 创建FastAPI应用
    app = FastAPI(
        title="简易医疗Agent系统",
        description="基于LLM的智能医疗咨询系统(文字版)",
        version="2.0.0"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 初始化组件
    session_manager = SessionManager()
    config_manager = ConfigManager()
    
    # 初始化智能体（传入配置管理器）
    agent_decision = AgentDecision(config_manager)
    rag_agent = MedicalRAG(config_manager)
    web_search_agent = WebSearchAgent(config_manager)
    conversation_agent = ConversationAgent(config_manager)
    
    # 初始化各个路由模块的依赖
    init_chat_routes(
        session_manager,
        agent_decision,
        rag_agent,
        web_search_agent,
        conversation_agent,
        config_manager
    )
    
    init_config_routes(
        config_manager,
        agent_decision,
        rag_agent,
        web_search_agent,
        conversation_agent
    )
    
    init_health_routes(
        session_manager,
        agent_decision
    )
    
    # 注册路由
    app.include_router(chat_router, tags=["聊天"])
    app.include_router(config_router, tags=["配置"])
    app.include_router(health_router, tags=["系统"])
    
    return app

