# App.py 重构说明

## 重构目标

将原783行的单文件 `app.py` 重构为模块化结构，提高可维护性。

## 模块结构

```
AgentM1/
├── app.py                    # 启动脚本 (28行)
└── web/                      # Web模块
    ├── app.py               # FastAPI应用初始化
    ├── models.py            # 数据模型（ChatRequest/Response, ConfigRequest）
    ├── session_manager.py   # 会话管理（历史记录，最多20条）
    ├── routes/              # API路由
    │   ├── chat.py         # /chat - 聊天处理
    │   ├── config.py       # /config - 配置管理
    │   └── health.py       # / /health /agents - 系统信息
    └── templates/
        └── index.html       # 前端界面
```

## 主要优势

1. **职责清晰** - 每个模块单一职责
2. **易于扩展** - 新路由只需在 `routes/` 添加文件
3. **便于测试** - 模块可独立测试
4. **团队协作** - 减少代码冲突

## 启动方式

```bash
python app.py
```

或使用 uvicorn：
```bash
uvicorn web.app:create_app --factory --host 0.0.0.0 --port 8000
```

