"""
健康检查和系统信息路由
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

# 创建路由
router = APIRouter()

# 这些依赖将在应用初始化时注入
session_manager = None
agent_decision = None


def init_health_routes(sm, ad):
    """
    初始化健康检查路由的依赖
    
    Args:
        sm: SessionManager - 会话管理器
        ad: AgentDecision - Agent决策器
    """
    global session_manager, agent_decision
    session_manager = sm
    agent_decision = ad


@router.get("/", response_class=HTMLResponse)
async def home():
    """返回前端页面"""
    # 读取HTML模板文件
    template_path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "医疗Agent系统运行正常"}


@router.get("/agents")
async def get_agents():
    """获取可用的Agent信息"""
    return {
        "agents": agent_decision.get_agent_info(),
        "current_sessions": session_manager.get_session_count()
    }

