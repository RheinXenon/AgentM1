# AgentM1 智能Agent系统

> ⚠️ **初始验证项目** - 功能和可行性尚在验证中

基于LLM的可配置多智能体系统 - 支持自定义提示词和知识库管理

## ✨ 新功能

### v2.1 - 多知识库支持
- 📚 **多知识库管理**：支持配置和使用多个独立的知识库
- 🎯 **智能路由**：自动识别问题并选择最合适的知识库
- 📥 **批量导入**：一键导入多个知识库的文档
- 🔍 **知识库管理工具**：查看、统计、搜索知识库

### v2.0 - 可配置化系统
- 🎛️ **可配置化系统**：完全移除硬编码，支持网页界面配置
- 📝 **自定义提示词**：可在界面上修改所有Agent的提示词
- 🔄 **RAG开关**：可选择启用或禁用知识库检索功能
- 💾 **配置持久化**：配置自动保存，重启后仍然有效
- 🎨 **灵活定制**：可自定义系统名称和欢迎消息

## 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 配置
创建`.env`文件，配置阿里云百炼平台API：
```
DASHSCOPE_API_KEY=your_key
DASHSCOPE_MODEL_NAME=qwen-plus
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v2
...
```

### 导入数据（可选）

#### 方式一：批量导入多个知识库（推荐）
```bash
# 自动导入 text/ 文件夹下所有子文件夹的文档
python ingest_data.py --all
```

#### 方式二：导入到指定知识库
```bash
python ingest_data.py --folder ./my_docs --kb 医疗知识库
```

详细说明请查看：[多知识库使用指南](docs/多知识库使用指南.md)

### 运行
```bash
python app.py
```

访问 http://localhost:8000

## 📖 使用指南

### 配置系统

1. 打开浏览器访问 http://localhost:8000
2. 点击顶部的 **⚙️ 配置** 标签
3. 在配置页面中可以：
   - 修改系统名称和欢迎消息
   - 启用/禁用RAG知识库
   - 自定义所有Agent的提示词
   - 保存或重置配置

### 管理知识库

```bash
# 查看所有知识库
python manage_knowledge_bases.py list

# 查看知识库统计
python manage_knowledge_bases.py stats

# 搜索知识库
python manage_knowledge_bases.py search "您的问题" --kb 医疗知识库
```

### 测试系统

```bash
python test_system.py
```

### 详细文档

- [配置系统使用说明](docs/配置系统使用说明.md)
- [多知识库使用指南](docs/多知识库使用指南.md)
- [数据导入使用说明](docs/数据导入使用说明.md)

## 🏗️ 系统架构

### 技术栈
- **后端框架**: FastAPI
- **LLM**: LangChain + 阿里云百炼平台（通义千问）
- **向量数据库**: Qdrant
- **Agent架构**: 多Agent系统（决策/RAG/搜索/对话）
- **配置管理**: 动态配置系统

### 核心组件

1. **ConfigManager**: 配置管理器，处理所有配置的保存和加载
2. **AgentDecision**: 决策Agent，根据查询内容路由到合适的Agent和知识库
3. **ConversationAgent**: 对话Agent，处理一般性对话
4. **MedicalRAG**: RAG Agent，支持多知识库的检索增强生成
5. **WebSearchAgent**: 搜索Agent，基于网络搜索的回答

### 知识库架构

- 支持多个独立的知识库（Collection）
- 每个知识库存储特定领域的专业知识
- 智能路由系统自动选择相关知识库
- 支持跨知识库检索和排序

### 配置文件
- `./data/user_config.json`: 用户配置文件（自动生成）
- `.env`: 环境变量配置

## 免责声明
**仅供学习研究，不可用于实际医疗诊断**

## License
MIT

