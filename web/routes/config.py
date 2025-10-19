"""
配置相关路由
"""
from fastapi import APIRouter, HTTPException
from ..models import ConfigRequest

# 创建路由
router = APIRouter()

# 这些依赖将在应用初始化时注入
config_manager = None
agent_decision = None
rag_agent = None
web_search_agent = None
conversation_agent = None


def init_config_routes(cm, ad, ra, wsa, ca):
    """
    初始化配置路由的依赖
    
    Args:
        cm: ConfigManager - 配置管理器
        ad: AgentDecision - Agent决策器
        ra: MedicalRAG - RAG Agent
        wsa: WebSearchAgent - 网络搜索Agent
        ca: ConversationAgent - 对话Agent
    """
    global config_manager, agent_decision, rag_agent, web_search_agent, conversation_agent
    config_manager = cm
    agent_decision = ad
    rag_agent = ra
    web_search_agent = wsa
    conversation_agent = ca


@router.get("/config")
async def get_config():
    """获取当前配置"""
    try:
        config = config_manager.get_config()
        return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_config(config_request: ConfigRequest):
    """更新配置"""
    try:
        # 构建更新字典（只更新非None的值）
        updates = {}
        if config_request.rag_enabled is not None:
            updates["rag_enabled"] = config_request.rag_enabled
        if config_request.agent_decision_prompt is not None:
            updates["agent_decision_prompt"] = config_request.agent_decision_prompt
        if config_request.conversation_prompt is not None:
            updates["conversation_prompt"] = config_request.conversation_prompt
        if config_request.rag_prompt is not None:
            updates["rag_prompt"] = config_request.rag_prompt
        if config_request.websearch_prompt is not None:
            updates["websearch_prompt"] = config_request.websearch_prompt
        if config_request.system_name is not None:
            updates["system_name"] = config_request.system_name
        if config_request.welcome_message is not None:
            updates["welcome_message"] = config_request.welcome_message
        
        # 更新配置
        success = config_manager.update_config(updates)
        
        if success:
            # 更新所有Agent的提示词
            agent_decision.update_prompt()
            conversation_agent.update_prompt()
            rag_agent.update_prompt()
            web_search_agent.update_prompt()
            
            return {"success": True, "message": "配置更新成功"}
        else:
            raise HTTPException(status_code=500, detail="配置保存失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/reset")
async def reset_config():
    """重置配置为默认值"""
    try:
        success = config_manager.reset_to_default()
        
        if success:
            # 更新所有Agent的提示词
            agent_decision.update_prompt()
            conversation_agent.update_prompt()
            rag_agent.update_prompt()
            web_search_agent.update_prompt()
            
            return {"success": True, "message": "配置已重置为默认值"}
        else:
            raise HTTPException(status_code=500, detail="配置重置失败")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

