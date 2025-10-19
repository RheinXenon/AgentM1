"""
FastAPI主应用 - 简易医疗Agent系统
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import uuid
import os

# 导入智能体
from agents.agent_decision import AgentDecision
from agents.rag_agent import MedicalRAG
from agents.web_search_agent import WebSearchAgent
from agents.conversation_agent import ConversationAgent

# 创建FastAPI应用
app = FastAPI(
    title="简易医疗Agent系统",
    description="基于LLM的智能医疗咨询系统(文字版)",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 会话存储 (生产环境应使用Redis等)
sessions = {}

# 初始化智能体
agent_decision = AgentDecision()
rag_agent = MedicalRAG()
web_search_agent = WebSearchAgent()
conversation_agent = ConversationAgent()

# 请求模型
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None

class ChatResponse(BaseModel):
    session_id: str
    agent: str
    response: str
    sources: Optional[List[Dict]] = None
    confidence: Optional[float] = None

# API路由
@app.get("/", response_class=HTMLResponse)
async def home():
    """返回简单的前端页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>简易医疗Agent系统</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                width: 100%;
                max-width: 800px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 28px;
                margin-bottom: 10px;
            }
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            .chat-box {
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin-bottom: 20px;
                display: flex;
                flex-direction: column;
            }
            .message.user {
                align-items: flex-end;
            }
            .message.assistant {
                align-items: flex-start;
            }
            .message-content {
                max-width: 70%;
                padding: 15px;
                border-radius: 15px;
                word-wrap: break-word;
            }
            .message.user .message-content {
                background: #667eea;
                color: white;
            }
            .message.assistant .message-content {
                background: white;
                color: #333;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .agent-label {
                font-size: 12px;
                color: #667eea;
                margin-bottom: 5px;
                font-weight: bold;
            }
            .sources {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #eee;
                font-size: 12px;
            }
            .source-item {
                margin-top: 5px;
                padding: 5px;
                background: #f0f0f0;
                border-radius: 5px;
            }
            .input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #eee;
            }
            .input-group {
                display: flex;
                gap: 10px;
            }
            #userInput {
                flex: 1;
                padding: 15px;
                border: 2px solid #667eea;
                border-radius: 10px;
                font-size: 16px;
                outline: none;
            }
            #sendBtn {
                padding: 15px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            #sendBtn:hover {
                transform: scale(1.05);
            }
            #sendBtn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            .loading.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 简易医疗Agent系统</h1>
                <p>智能医疗咨询助手 - 为您提供专业的健康建议</p>
            </div>
            
            <div class="chat-box" id="chatBox">
                <div class="message assistant">
                    <div class="agent-label">医疗助手</div>
                    <div class="message-content">
                        您好!我是您的医疗咨询助手。我可以:
                        <br>• 回答医学健康问题
                        <br>• 搜索最新医学研究
                        <br>• 提供健康生活建议
                        <br><br>请问有什么可以帮助您的?
                    </div>
                </div>
            </div>
            
            <div class="loading" id="loading">正在思考中...</div>
            
            <div class="input-area">
                <div class="input-group">
                    <input type="text" id="userInput" placeholder="输入您的健康问题..." />
                    <button id="sendBtn" onclick="sendMessage()">发送</button>
                </div>
            </div>
        </div>

        <script>
            let sessionId = null;
            
            // 回车发送
            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            async function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // 显示用户消息
                addMessage('user', message);
                input.value = '';
                
                // 禁用输入
                document.getElementById('sendBtn').disabled = true;
                document.getElementById('loading').classList.add('active');
                
                try {
                    // 发送请求
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: message,
                            session_id: sessionId
                        })
                    });
                    
                    const data = await response.json();
                    
                    // 保存session_id
                    if (data.session_id) {
                        sessionId = data.session_id;
                    }
                    
                    // 显示助手回复
                    addMessage('assistant', data.response, data.agent, data.sources);
                    
                } catch (error) {
                    addMessage('assistant', '抱歉,发生错误: ' + error.message, '系统');
                } finally {
                    document.getElementById('sendBtn').disabled = false;
                    document.getElementById('loading').classList.remove('active');
                }
            }
            
            function addMessage(role, content, agent = '', sources = null) {
                const chatBox = document.getElementById('chatBox');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                
                let html = '';
                if (agent) {
                    html += `<div class="agent-label">${agent}</div>`;
                }
                html += `<div class="message-content">${content}`;
                
                // 添加来源信息
                if (sources && sources.length > 0) {
                    html += '<div class="sources"><strong>参考来源:</strong>';
                    sources.forEach((source, index) => {
                        if (source.url) {
                            html += `<div class="source-item">${index + 1}. <a href="${source.url}" target="_blank">${source.title}</a></div>`;
                        } else {
                            html += `<div class="source-item">${index + 1}. ${source.content || source.snippet}</div>`;
                        }
                    });
                    html += '</div>';
                }
                
                html += '</div>';
                messageDiv.innerHTML = html;
                
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        # 获取或创建session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions:
            sessions[session_id] = {
                "conversation_history": []
            }
        
        # 获取对话历史
        conversation_history = sessions[session_id]["conversation_history"]
        
        # 添加用户消息到历史
        conversation_history.append({
            "role": "user",
            "content": request.query
        })
        
        # Agent决策
        agent_type = agent_decision.decide(request.query, conversation_history)
        
        # 根据决策调用相应的Agent
        if agent_type == "RAG":
            result = rag_agent.query(request.query, conversation_history)
        elif agent_type == "WEBSEARCH":
            result = web_search_agent.search(request.query, conversation_history)
        else:  # CONVERSATION
            result = conversation_agent.chat(request.query, conversation_history)
        
        # 添加助手回复到历史
        conversation_history.append({
            "role": "assistant",
            "content": result["response"]
        })
        
        # 限制历史长度
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        # 更新session
        sessions[session_id]["conversation_history"] = conversation_history
        
        return ChatResponse(
            session_id=session_id,
            agent=result["agent"],
            response=result["response"],
            sources=result.get("sources", []),
            confidence=result.get("confidence")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "医疗Agent系统运行正常"}

@app.get("/agents")
async def get_agents():
    """获取可用的Agent信息"""
    return {
        "agents": agent_decision.get_agent_info(),
        "current_sessions": len(sessions)
    }

if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs("./data/qdrant_db", exist_ok=True)
    
    print("=" * 50)
    print("简易医疗Agent系统启动中...")
    print("访问地址: http://localhost:8000")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

