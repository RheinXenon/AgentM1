# Web静态资源目录说明

## 目录结构

```
web/static/
├── css/
│   └── style.css          # 全局CSS样式文件
├── js/
│   └── main.js            # 主要JavaScript逻辑
└── README.md              # 本说明文档
```

## 文件说明

### CSS文件

#### `css/style.css`
包含整个Web应用的样式定义，主要包括：
- 全局样式重置
- 容器和布局样式
- 标签页样式
- 聊天界面样式
- 消息展示样式
- 配置界面样式
- 调试信息样式
- 按钮和表单样式

### JavaScript文件

#### `js/main.js`
包含整个Web应用的前端逻辑，主要功能包括：

**全局变量**
- `sessionId`: 会话ID管理

**核心函数**
- `switchTab()`: 标签页切换
- `sendMessage()`: 发送用户消息
- `addMessage()`: 添加消息到聊天框
- `loadConfig()`: 加载系统配置
- `saveConfig()`: 保存系统配置
- `resetConfig()`: 重置配置为默认值
- `toggleDebugInfo()`: 切换调试信息显示
- `updateDebugInfo()`: 更新调试信息
- `showSuccessMessage()`: 显示成功提示消息

## 维护建议

### 添加新样式
1. 在 `css/style.css` 中添加新的CSS规则
2. 使用有意义的类名，遵循现有命名规范
3. 保持样式的模块化和可复用性

### 添加新功能
1. 在 `js/main.js` 中添加新的函数
2. 使用清晰的函数命名和注释
3. 保持代码的模块化，每个函数专注于单一职责

### 进一步拆分建议
如果项目继续增长，可以考虑：
- 将CSS按功能模块拆分（如 `chat.css`, `config.css`, `debug.css`）
- 将JavaScript按功能模块拆分（如 `chat.js`, `config.js`, `api.js`）
- 引入CSS预处理器（如SASS/LESS）
- 引入前端构建工具（如Webpack/Vite）

## 版本历史

- 2025-10-22: 初始拆分，将原有的单文件HTML拆分为HTML + CSS + JS三个文件

