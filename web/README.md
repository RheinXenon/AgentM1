# Web模块说明

## 模块概述

本模块包含了FastAPI Web应用的所有组件，采用模块化设计，职责清晰。

## 目录结构

```
web/
├── __init__.py              # 模块初始化，导出create_app函数
├── app.py                   # FastAPI应用工厂函数
├── models.py                # Pydantic数据模型
├── session_manager.py       # 会话管理器
├── routes/                  # API路由模块
│   ├── __init__.py         # 路由模块初始化
│   ├── chat.py             # 聊天相关路由
│   ├── config.py           # 配置相关路由
│   └── health.py           # 健康检查路由
└── templates/               # 前端模板
    └── index.html          # 主页面HTML模板
```

## 快速开始

### 启动应用

从项目根目录运行：

```bash
python app.py
```

或使用uvicorn直接启动：

```bash
uvicorn web.app:create_app --factory --host 0.0.0.0 --port 8000
```

### 开发模式（自动重载）

```bash
uvicorn web.app:create_app --factory --reload
```

## 模块详解

### app.py - 应用工厂

**主要功能**:
- 创建FastAPI应用实例
- 配置中间件（CORS等）
- 初始化所有组件（SessionManager, ConfigManager, Agents）
- 注册路由

**核心函数**:
```python
def create_app() -> FastAPI:
    """创建并配置FastAPI应用"""
    # 返回配置好的应用实例
```

### models.py - 数据模型

定义了三个Pydantic模型：

1. **ChatRequest** - 聊天请求
   - `query: str` - 用户问题
   - `session_id: Optional[str]` - 会话ID
   - `conversation_history: Optional[List[Dict]]` - 对话历史

2. **ChatResponse** - 聊天响应
   - `session_id: str` - 会话ID
   - `agent: str` - 使用的Agent类型
   - `response: str` - 回复内容
   - `sources: Optional[List[Dict]]` - 参考来源
   - `confidence: Optional[float]` - 置信度

3. **ConfigRequest** - 配置更新请求
   - 支持更新所有配置项
   - 所有字段均为可选

### session_manager.py - 会话管理

**主要功能**:
- 管理用户会话和对话历史
- 自动生成会话ID
- 限制历史记录长度（最多20条）

**主要方法**:
```python
# 获取或创建会话
get_or_create_session(session_id: str = None) -> tuple

# 添加消息到历史
add_message(session_id: str, role: str, content: str)

# 获取会话数量
get_session_count() -> int
```

### routes/ - API路由

#### chat.py - 聊天路由
- **POST /chat** - 处理用户聊天请求
  - 会话管理
  - Agent决策
  - 调用相应的Agent处理请求

#### config.py - 配置路由
- **GET /config** - 获取当前配置
- **POST /config** - 更新配置
- **POST /config/reset** - 重置为默认配置

#### health.py - 系统路由
- **GET /** - 返回前端页面
- **GET /health** - 健康检查
- **GET /agents** - 获取Agent信息

### templates/ - 前端模板

包含完整的前端界面，采用原生HTML/CSS/JavaScript实现。

## 依赖注入

路由模块使用函数注入依赖：

```python
# 在web/app.py中初始化依赖
init_chat_routes(session_manager, agent_decision, ...)

# 在路由模块中使用全局变量接收
def init_chat_routes(sm, ad, ...):
    global session_manager, agent_decision
    session_manager = sm
    agent_decision = ad
```

这种设计允许路由函数访问共享的组件实例。

## API端点

### 聊天接口
```http
POST /chat
Content-Type: application/json

{
  "query": "你好",
  "session_id": "uuid-string"  // 可选
}
```

### 配置接口
```http
# 获取配置
GET /config

# 更新配置
POST /config
Content-Type: application/json

{
  "rag_enabled": true,
  "system_name": "智能助手",
  ...
}

# 重置配置
POST /config/reset
```

### 系统接口
```http
# 健康检查
GET /health

# Agent信息
GET /agents
```

## 扩展指南

### 添加新的API路由

1. 在 `routes/` 目录创建新的路由文件
2. 定义路由和处理函数
3. 在 `routes/__init__.py` 中导出路由
4. 在 `web/app.py` 中注册路由

示例：
```python
# routes/new_route.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/new")
async def new_endpoint():
    return {"message": "New endpoint"}

# routes/__init__.py
from .new_route import router as new_router

# web/app.py
app.include_router(new_router, tags=["新功能"])
```

### 修改前端界面

直接编辑 `templates/index.html` 文件即可。

## 注意事项

1. **会话存储**: 当前使用内存存储会话，生产环境建议使用Redis
2. **静态文件**: 如需提供静态文件，可使用FastAPI的StaticFiles中间件
3. **模板引擎**: 当前使用简单的文件读取，可改用Jinja2模板引擎

## 版本历史

- **v2.0.0** - 模块化重构，将原783行的app.py拆分为多个模块
- **v1.0.0** - 初始单文件版本

