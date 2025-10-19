"""
聊天相关路由
"""
from fastapi import APIRouter, HTTPException
from ..models import ChatRequest, ChatResponse

# 创建路由
router = APIRouter()

# 这些依赖将在应用初始化时注入
session_manager = None
agent_decision = None
rag_agent = None
web_search_agent = None
conversation_agent = None
config_manager = None


def init_chat_routes(sm, ad, ra, wsa, ca, cm):
    """
    初始化聊天路由的依赖
    
    Args:
        sm: SessionManager - 会话管理器
        ad: AgentDecision - Agent决策器
        ra: MedicalRAG - RAG Agent
        wsa: WebSearchAgent - 网络搜索Agent
        ca: ConversationAgent - 对话Agent
        cm: ConfigManager - 配置管理器
    """
    global session_manager, agent_decision, rag_agent, web_search_agent, conversation_agent, config_manager
    session_manager = sm
    agent_decision = ad
    rag_agent = ra
    web_search_agent = wsa
    conversation_agent = ca
    config_manager = cm


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        # 获取或创建session
        session_id, conversation_history = session_manager.get_or_create_session(
            request.session_id
        )
        
        # 添加用户消息到历史
        session_manager.add_message(session_id, "user", request.query)
        
        # Agent决策
        agent_type = agent_decision.decide(request.query, conversation_history)
        
        # 检查RAG是否启用，如果禁用则不使用RAG
        if agent_type == "RAG" and not config_manager.is_rag_enabled():
            # RAG被禁用，改为使用对话Agent
            agent_type = "CONVERSATION"
        
        # 根据决策调用相应的Agent
        if agent_type == "RAG":
            result = rag_agent.query(request.query, conversation_history)
        elif agent_type == "WEBSEARCH":
            result = web_search_agent.search(request.query, conversation_history)
        else:  # CONVERSATION
            result = conversation_agent.chat(request.query, conversation_history)
        
        # 添加助手回复到历史
        session_manager.add_message(session_id, "assistant", result["response"])
        
        return ChatResponse(
            session_id=session_id,
            agent=result["agent"],
            response=result["response"],
            sources=result.get("sources", []),
            confidence=result.get("confidence")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

