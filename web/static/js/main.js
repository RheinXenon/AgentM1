// 全局变量
let sessionId = null;

// 页面加载时获取配置
window.addEventListener('load', function() {
    loadConfig();
});

// 回车发送
document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

/**
 * 切换标签页
 * @param {string} tabName - 标签页名称
 */
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

/**
 * 加载配置
 */
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

/**
 * 保存配置
 */
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

/**
 * 重置配置
 */
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

/**
 * 显示成功消息
 * @param {string} message - 消息内容
 */
function showSuccessMessage(message) {
    const msgEl = document.getElementById('successMsg');
    msgEl.innerText = message;
    msgEl.classList.add('show');
    
    setTimeout(() => {
        msgEl.classList.remove('show');
    }, 3000);
}

/**
 * 发送消息
 */
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
        
        // 更新调试信息
        if (data.debug_info) {
            updateDebugInfo(data.debug_info);
        }
        
    } catch (error) {
        addMessage('assistant', '抱歉,发生错误: ' + error.message, '系统');
    } finally {
        document.getElementById('sendBtn').disabled = false;
        document.getElementById('loading').classList.remove('active');
    }
}

/**
 * 添加消息到聊天框
 * @param {string} role - 角色 (user/assistant)
 * @param {string} content - 消息内容
 * @param {string} agent - Agent名称
 * @param {Array} sources - 来源信息
 */
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

/**
 * 切换调试信息显示
 */
function toggleDebugInfo() {
    const debugInfo = document.getElementById('debugInfo');
    debugInfo.classList.toggle('show');
}

/**
 * 更新调试信息
 * @param {Object} debugInfo - 调试信息对象
 */
function updateDebugInfo(debugInfo) {
    // 更新决策信息
    const decisionEl = document.getElementById('debugDecision');
    if (debugInfo.decision_agent) {
        decisionEl.innerHTML = `<strong>决策结果:</strong> ${debugInfo.decision_agent}`;
    }
    
    // 更新执行Agent信息
    const executionEl = document.getElementById('debugExecution');
    if (debugInfo.execution_agent) {
        executionEl.innerHTML = `<strong>执行Agent:</strong> ${debugInfo.execution_agent}`;
    }
    
    // 更新LLM调用记录
    const llmCallsEl = document.getElementById('debugLLMCalls');
    if (debugInfo.llm_calls && debugInfo.llm_calls.length > 0) {
        let html = '';
        debugInfo.llm_calls.forEach((call, index) => {
            html += `
                <div class="debug-llm-call">
                    <div><strong>调用 ${index + 1}:</strong></div>
                    <div class="agent-name">Agent: ${call.agent}</div>
                    <div class="model-name">模型: ${call.model}</div>
                    <div class="purpose">用途: ${call.purpose}</div>
                </div>
            `;
        });
        llmCallsEl.innerHTML = html;
    } else {
        llmCallsEl.innerHTML = '暂无调用记录';
    }
}

