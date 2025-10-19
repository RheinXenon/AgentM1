# AgentM1 医疗Agent系统

> ⚠️ **初始验证项目** - 功能和可行性尚在验证中

基于LLM的多智能体医疗咨询系统原型

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

### 运行
```bash
python app.py
```

访问 http://localhost:8000

## 技术栈
- FastAPI后端
- LangChain + 阿里云百炼平台（通义千问）
- Qdrant向量数据库
- 多Agent架构（RAG/搜索/对话）

## 免责声明
**仅供学习研究，不可用于实际医疗诊断**

## License
MIT

