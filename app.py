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

# 导入配置管理器
from config_manager import ConfigManager

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

# 初始化配置管理器
config_manager = ConfigManager()

# 初始化智能体（传入配置管理器）
agent_decision = AgentDecision(config_manager)
rag_agent = MedicalRAG(config_manager)
web_search_agent = WebSearchAgent(config_manager)
conversation_agent = ConversationAgent(config_manager)

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

class ConfigRequest(BaseModel):
    """配置更新请求"""
    rag_enabled: Optional[bool] = None
    agent_decision_prompt: Optional[str] = None
    conversation_prompt: Optional[str] = None
    rag_prompt: Optional[str] = None
    websearch_prompt: Optional[str] = None
    system_name: Optional[str] = None
    welcome_message: Optional[str] = None

# API路由
@app.get("/", response_class=HTMLResponse)
async def home():
    """返回前端页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>智能Agent系统</title>
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
                max-width: 1200px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .tabs {
                display: flex;
                background: #f0f0f0;
                border-bottom: 2px solid #ddd;
            }
            .tab {
                flex: 1;
                padding: 15px;
                text-align: center;
                cursor: pointer;
                background: #f0f0f0;
                border: none;
                font-size: 16px;
                transition: all 0.3s;
            }
            .tab:hover {
                background: #e0e0e0;
            }
            .tab.active {
                background: white;
                border-bottom: 3px solid #667eea;
                font-weight: bold;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
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
            .config-section {
                padding: 30px;
                max-height: 600px;
                overflow-y: auto;
            }
            .config-item {
                margin-bottom: 25px;
            }
            .config-item label {
                display: block;
                font-weight: bold;
                margin-bottom: 8px;
                color: #333;
            }
            .config-item input[type="text"],
            .config-item textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                transition: border-color 0.3s;
            }
            .config-item input[type="text"]:focus,
            .config-item textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .config-item textarea {
                min-height: 150px;
                resize: vertical;
            }
            .config-item .checkbox-wrapper {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .config-item input[type="checkbox"] {
                width: 20px;
                height: 20px;
                cursor: pointer;
            }
            .config-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 30px;
            }
            .btn {
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover {
                transform: scale(1.05);
            }
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            .btn-secondary:hover {
                background: #5a6268;
            }
            .success-message {
                display: none;
                padding: 15px;
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 8px;
                color: #155724;
                margin-bottom: 20px;
            }
            .success-message.show {
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 智能Agent系统</h1>
                <p id="systemDesc">智能助手 - 为您提供专业的咨询服务</p>
            </div>
            
            <!-- 标签页导航 -->
            <div class="tabs">
                <button class="tab active" onclick="switchTab('chat')">💬 对话</button>
                <button class="tab" onclick="switchTab('config')">⚙️ 配置</button>
            </div>
            
            <!-- 对话标签页 -->
            <div id="chatTab" class="tab-content active">
                <div class="chat-box" id="chatBox">
                    <div class="message assistant">
                        <div class="agent-label">智能助手</div>
                        <div class="message-content" id="welcomeMsg">
                            您好!我是您的智能助手。请问有什么可以帮助您的?
                        </div>
                    </div>
                </div>
                
                <div class="loading" id="loading">正在思考中...</div>
                
                <div class="input-area">
                    <div class="input-group">
                        <input type="text" id="userInput" placeholder="输入您的问题..." />
                        <button id="sendBtn" onclick="sendMessage()">发送</button>
                    </div>
                </div>
            </div>
            
            <!-- 配置标签页 -->
            <div id="configTab" class="tab-content">
                <div class="config-section">
                    <div class="success-message" id="successMsg"></div>
                    
                    <h2 style="margin-bottom: 20px;">系统配置</h2>
                    
                    <div class="config-item">
                        <label>系统名称</label>
                        <input type="text" id="systemName" placeholder="智能Agent系统" />
                    </div>
                    
                    <div class="config-item">
                        <label>欢迎消息</label>
                        <textarea id="welcomeMessage" placeholder="输入欢迎消息..."></textarea>
                    </div>
                    
                    <div class="config-item">
                        <label class="checkbox-wrapper">
                            <input type="checkbox" id="ragEnabled" />
                            <span>启用RAG知识库（禁用后将不使用知识库检索）</span>
                        </label>
                    </div>
                    
                    <h3 style="margin: 30px 0 15px 0;">提示词配置</h3>
                    
                    <div class="config-item">
                        <label>Agent决策提示词</label>
                        <textarea id="agentDecisionPrompt" placeholder="输入Agent决策提示词..."></textarea>
                    </div>
                    
                    <div class="config-item">
                        <label>对话Agent提示词</label>
                        <textarea id="conversationPrompt" placeholder="输入对话Agent提示词..."></textarea>
                    </div>
                    
                    <div class="config-item">
                        <label>RAG Agent提示词</label>
                        <textarea id="ragPrompt" placeholder="输入RAG Agent提示词..."></textarea>
                    </div>
                    
                    <div class="config-item">
                        <label>网络搜索Agent提示词</label>
                        <textarea id="websearchPrompt" placeholder="输入网络搜索Agent提示词..."></textarea>
                    </div>
                    
                    <div class="config-buttons">
                        <button class="btn btn-primary" onclick="saveConfig()">💾 保存配置</button>
                        <button class="btn btn-secondary" onclick="resetConfig()">🔄 重置为默认</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let sessionId = null;
            
            // 页面加载时获取配置
            window.addEventListener('load', function() {
                loadConfig();
            });
            
            // 回车发送
            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // 切换标签页
            function switchTab(tabName) {
                // 更新标签按钮状态
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                event.target.classList.add('active');
                
                // 更新标签页内容
                document.getElementById('chatTab').classList.remove('active');
                document.getElementById('configTab').classList.remove('active');
                
                if (tabName === 'chat') {
                    document.getElementById('chatTab').classList.add('active');
                } else if (tabName === 'config') {
                    document.getElementById('configTab').classList.add('active');
                    loadConfig(); // 加载最新配置
                }
            }
            
            // 加载配置
            async function loadConfig() {
                try {
                    const response = await fetch('/config');
                    const data = await response.json();
                    
                    if (data.success && data.config) {
                        const config = data.config;
                        
                        // 填充表单
                        document.getElementById('systemName').value = config.system_name || '';
                        document.getElementById('welcomeMessage').value = config.welcome_message || '';
                        document.getElementById('ragEnabled').checked = config.rag_enabled !== false;
                        document.getElementById('agentDecisionPrompt').value = config.agent_decision_prompt || '';
                        document.getElementById('conversationPrompt').value = config.conversation_prompt || '';
                        document.getElementById('ragPrompt').value = config.rag_prompt || '';
                        document.getElementById('websearchPrompt').value = config.websearch_prompt || '';
                        
                        // 更新欢迎消息
                        if (config.welcome_message) {
                            document.getElementById('welcomeMsg').innerText = config.welcome_message;
                        }
                    }
                } catch (error) {
                    console.error('加载配置失败:', error);
                }
            }
            
            // 保存配置
            async function saveConfig() {
                try {
                    const config = {
                        system_name: document.getElementById('systemName').value,
                        welcome_message: document.getElementById('welcomeMessage').value,
                        rag_enabled: document.getElementById('ragEnabled').checked,
                        agent_decision_prompt: document.getElementById('agentDecisionPrompt').value,
                        conversation_prompt: document.getElementById('conversationPrompt').value,
                        rag_prompt: document.getElementById('ragPrompt').value,
                        websearch_prompt: document.getElementById('websearchPrompt').value
                    };
                    
                    const response = await fetch('/config', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(config)
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showSuccessMessage('配置保存成功！');
                        // 更新欢迎消息
                        if (config.welcome_message) {
                            document.getElementById('welcomeMsg').innerText = config.welcome_message;
                        }
                    } else {
                        alert('保存失败: ' + data.message);
                    }
                } catch (error) {
                    alert('保存配置失败: ' + error.message);
                }
            }
            
            // 重置配置
            async function resetConfig() {
                if (!confirm('确定要重置为默认配置吗？这将清除所有自定义设置。')) {
                    return;
                }
                
                try {
                    const response = await fetch('/config/reset', {
                        method: 'POST'
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showSuccessMessage('配置已重置为默认值！');
                        loadConfig(); // 重新加载配置
                    } else {
                        alert('重置失败: ' + data.message);
                    }
                } catch (error) {
                    alert('重置配置失败: ' + error.message);
                }
            }
            
            // 显示成功消息
            function showSuccessMessage(message) {
                const msgEl = document.getElementById('successMsg');
                msgEl.innerText = message;
                msgEl.classList.add('show');
                
                setTimeout(() => {
                    msgEl.classList.remove('show');
                }, 3000);
            }
            
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

@app.get("/config")
async def get_config():
    """获取当前配置"""
    try:
        config = config_manager.get_config()
        return {"success": True, "config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config")
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

@app.post("/config/reset")
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

if __name__ == "__main__":
    # 确保数据目录存在
    os.makedirs("./data/qdrant_db", exist_ok=True)
    
    print("=" * 50)
    print("简易医疗Agent系统启动中...")
    print("访问地址: http://localhost:8000")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

